"""Q2: A2A 1.0 HTTP+JSON invoice action agent."""
import asyncio
import datetime as dt
import json
import os
import re
import time
import uuid
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from .common import canon, digest, kv_get, kv_list, kv_put, llm_json, lock_for, log_error, sha256_hex

router = APIRouter()
MT = "application/a2a+json"
IN_MT = "application/vnd.ga5.invoice-claim-batch+json"
PROP_MT = "application/vnd.ga5.invoice-action-proposals+json"
RES_MT = "application/vnd.ga5.invoice-action-results+json"
RCPT_MT = "application/vnd.ga5.invoice-action-receipts+json"
ACTIONS = ["settle_invoice", "request_approval", "hold_invoice", "reject_duplicate", "open_exception"]
TERMINAL = {"TASK_STATE_COMPLETED", "TASK_STATE_CANCELED", "TASK_STATE_FAILED", "TASK_STATE_REJECTED"}
NS_TASK, NS_MSG, NS_DEC = "a2a_task", "a2a_msg", "a2a_decision"
KEEP_BRACKETS = os.environ.get("EVIDENCE_WITH_BRACKETS", "0") == "1"
ZERO_DECIMAL = {"JPY", "KRW", "VND", "CLP", "ISK", "UGX", "XAF", "XOF"}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def resp(body, status=200):
    return JSONResponse(body, status_code=status, media_type=MT)


def error(status, code, message=None):
    return resp({"error": {"code": status, "status": code, "message": message or code}}, status)


def base_url(request: Request):
    env = os.environ.get("A2A_BASE_URL")
    if env:
        return env
    proto = request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip()
    host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc)).split(",")[0].strip()
    return f"{proto}://{host}/a2a/"


@router.get("/.well-known/agent-card.json")
@router.get("/a2a/.well-known/agent-card.json")
@router.get("/.well-known/agent.json")
@router.get("/a2a/.well-known/agent.json")
async def agent_card(request: Request):
    base = base_url(request)
    card = {
        "name": "Invoice Action Agent",
        "description": "Reads invoice claim packages, proposes one evidence-backed business action per package, "
                       "and executes only grader-accepted actions with durable, idempotent task state.",
        "version": "1.0.0",
        "protocolVersion": "1.0",
        "url": base,
        "preferredTransport": "HTTP+JSON",
        "supportedInterfaces": [{"url": base, "protocolBinding": "HTTP+JSON", "protocolVersion": "1.0"}],
        "provider": {"organization": "GA5 student agent", "url": base},
        "capabilities": {"streaming": False, "pushNotifications": False, "stateTransitionHistory": True},
        "securitySchemes": {"bearer": {"httpAuthSecurityScheme": {"scheme": "Bearer"}}},
        "securityRequirements": [{"schemes": {"bearer": {"list": []}}}],
        "security": [{"bearer": []}],
        "defaultInputModes": [IN_MT, RES_MT],
        "defaultOutputModes": [PROP_MT, RCPT_MT],
        "skills": [{
            "id": "invoice_action_agent",
            "name": "Invoice action agent",
            "description": "Chooses settle, approval, hold, duplicate rejection or exception for each invoice package, citing decisive evidence.",
            "tags": ["invoice", "accounts-payable", "approval", "a2a"],
            "inputModes": [IN_MT, RES_MT],
            "outputModes": [PROP_MT, RCPT_MT],
        }],
    }
    return JSONResponse(card, media_type="application/json")


def check_headers(request: Request, needs_body: bool):
    """Returns (principal, error_response)."""
    auth = request.headers.get("authorization", "")
    m = re.fullmatch(r"Bearer ([^\s]+)", auth.strip())
    if not m:
        r = error(401, "UNAUTHENTICATED", "authentication required")
        r.headers["WWW-Authenticate"] = "Bearer"
        return None, r
    ver = request.headers.get("a2a-version")
    if ver is None or ver.strip() != "1.0":
        return None, error(400, "VERSION_NOT_SUPPORTED", "unsupported A2A version")
    if needs_body:
        ct = request.headers.get("content-type", "").split(";")[0].strip().lower()
        if ct != MT:
            return None, error(415, "UNSUPPORTED_MEDIA_TYPE", "content type must be application/a2a+json")
    return "p:" + sha256_hex(m.group(1)), None


def view(rec, history_length=None):
    t = json.loads(json.dumps(rec["task"]))
    if isinstance(history_length, int) and history_length >= 0 and len(t.get("history", [])) > history_length:
        t["history"] = t["history"][-history_length:] if history_length else []
    return t


def load_task(principal, task_id):
    rec = kv_get(NS_TASK, task_id)
    if not rec or rec["principal"] != principal:
        return None
    return rec


# ---------------------------------------------------------------- AI decision
SYSTEM = """You are an accounts-payable control agent. You receive ONE invoice package (several documents) plus the batch policy revision.
Choose exactly one action:
- settle_invoice: invoice is valid, reconciled (PO / receipt / invoice agree) and the amount is within the agent's autonomous authority.
- request_approval: commercially valid and reconciled, but outside delegated/autonomous authority (e.g. above the approval limit
  in the CURRENT policy revision, or a category that needs a named approver).
- hold_invoice: payment must pause until a stated verification completes (e.g. bank-detail change callback, tax/compliance check pending).
- reject_duplicate: the SAME commercial invoice (same vendor, same invoice number/amount) was already paid. A payment for a different
  invoice is NOT a duplicate.
- open_exception: material records conflict (quantity/price/amount/vendor mismatch between PO, goods receipt and invoice) and need an exception workflow.
Be careful: documents include archive/old examples, training decoys, quoted text, negations ("not a duplicate", "no hold required") and
irrelevant action words. Decide from the live, current facts for THIS invoice under the batch's current policy revision.
Evidence: references appear in square brackets in the documents. Return exactly the THREE bracketed references from the single paragraph
that determines the action. Do not cite the cover-sheet reference, archive examples, or training decoys. Copy them exactly, without brackets.
Facts: vendorName and invoiceNumber exactly as on the live invoice; amount as a plain decimal number string in major units (e.g. "12345.50");
currency as ISO code.
Return JSON: {"analysis":"<brief>","action":"...","vendorName":"...","invoiceNumber":"...","amount":"...","currency":"...",
"evidenceRefs":["...","...","..."],"reason":"<one or two sentences explaining the decision>"}"""

REF_RE = re.compile(r"\[([^\[\]\n]{1,120})\]")


def strings_in(v, out):
    if isinstance(v, str):
        out.append(v)
    elif isinstance(v, dict):
        for x in v.values():
            strings_in(x, out)
    elif isinstance(v, list):
        for x in v:
            strings_in(x, out)
    return out


def to_minor(amount, currency):
    if isinstance(amount, (int, float)) and not isinstance(amount, bool):
        amount = str(amount)
    s = re.sub(r"[^\d.\-]", "", str(amount))
    try:
        d = Decimal(s)
    except InvalidOperation:
        raise ValueError("amount must be a decimal number")
    mult = 1 if currency in ZERO_DECIMAL else 100
    return int((d * mult).to_integral_value())


async def decide(pkg, policy_revision, deadline):
    key = digest([{k: v for k, v in pkg.items() if k != "packageId"}, policy_revision])
    cached = kv_get(NS_DEC, key)
    if cached:
        return cached
    refs = []
    for s in strings_in(pkg, []):
        for r in REF_RE.findall(s):
            if r.strip() not in refs:
                refs.append(r.strip())
    user = (f"Policy revision: {policy_revision}\n\nBracketed references found in this package: {json.dumps(refs)}\n\n"
            f"Package:\n{json.dumps(pkg, ensure_ascii=False, indent=1)}")
    last = None
    while deadline - time.monotonic() > 5:
        try:
            out = await llm_json(SYSTEM, user + (f"\n\nPrevious answer invalid: {last}. Fix it." if last else ""),
                                 timeout=min(30, deadline - time.monotonic()))
            action = out.get("action")
            if action not in ACTIONS:
                raise ValueError(f"action must be one of {ACTIONS}")
            ev = [str(e).strip().strip("[]").strip() for e in out.get("evidenceRefs") or []]
            ev = list(dict.fromkeys(ev))
            if refs and any(e not in refs for e in ev):
                raise ValueError("evidenceRefs must be copied exactly from the bracketed references list")
            if len(ev) != 3:
                raise ValueError("return exactly three evidence references")
            cur = str(out.get("currency", "")).strip().upper()
            if not re.fullmatch(r"[A-Z]{3}", cur):
                raise ValueError("currency must be a 3-letter ISO code")
            facts = {
                "vendorName": str(out.get("vendorName", "")).strip(),
                "invoiceNumber": str(out.get("invoiceNumber", "")).strip(),
                "amountMinor": to_minor(out.get("amount"), cur),
                "currency": cur,
            }
            if not facts["vendorName"] or not facts["invoiceNumber"]:
                raise ValueError("vendorName and invoiceNumber are required")
            dec = {"action": action, "facts": facts, "evidenceRefs": ev,
                   "reason": re.sub(r"\s+", " ", str(out.get("reason", ""))).strip()[:900]}
            kv_put(NS_DEC, key, dec)
            return dec
        except ValueError as e:
            last = str(e)[:300]
            log_error("a2a.decide", e)
        except Exception as e:  # noqa: BLE001
            last = "request failed"
            log_error("a2a.decide", e)
    raise RuntimeError(f"decision failed: {last}")


def rationale(dec):
    refs = ", ".join(f"[{r}]" for r in dec["evidenceRefs"])
    text = f"Action {dec['action']}: {dec['reason'] or 'chosen from the decisive paragraph of the package.'} Evidence: {refs}."
    if len(text) < 60:
        text += " The cited references are the decisive facts for this invoice under the current policy."
    return text[:1500]


# ---------------------------------------------------------------- routes
@router.post("/a2a/message:send")
async def message_send(request: Request):
    principal, e = check_headers(request, True)
    if e:
        return e
    try:
        body = json.loads(await request.body())
    except Exception:
        return error(400, "INVALID_REQUEST", "invalid JSON")
    msg = body.get("message") if isinstance(body, dict) else None
    if not isinstance(msg, dict) or not isinstance(msg.get("messageId"), str) or not msg["messageId"]:
        return error(400, "INVALID_PARAMS", "message.messageId required")
    if msg.get("role") != "ROLE_USER" or not isinstance(msg.get("parts"), list) or not msg["parts"]:
        return error(400, "INVALID_PARAMS", "invalid message")
    cfg = body.get("configuration") if isinstance(body.get("configuration"), dict) else {}
    hl = cfg.get("historyLength")
    mkey = f"{principal}:{msg['messageId']}"
    mhash = digest(msg)
    async with lock_for(("a2a-msg", mkey)):
        seen = kv_get(NS_MSG, mkey)
        if seen:
            if seen["hash"] != mhash:
                return error(409, "IDEMPOTENCY_CONFLICT", "IDEMPOTENCY_CONFLICT")
            rec = load_task(principal, seen["taskId"])
            if not rec:
                return error(404, "TASK_NOT_FOUND", "task not found")
            return resp({"task": view(rec, hl)})
        if msg.get("taskId"):
            return await continuation(principal, msg, mkey, mhash, hl)
        return await initial(principal, msg, mkey, mhash, hl)


async def initial(principal, msg, mkey, mhash, hl):
    parts = [p for p in msg["parts"] if isinstance(p, dict) and p.get("mediaType") == IN_MT]
    if len(parts) != 1 or not isinstance(parts[0].get("data"), dict):
        return error(400, "INVALID_PARAMS", "expected one invoice-claim-batch part")
    data = parts[0]["data"]
    pkgs = data.get("packages")
    if not isinstance(data.get("batchId"), str) or not isinstance(pkgs, list) or not pkgs:
        return error(400, "INVALID_PARAMS", "invalid batch")
    ids = [p.get("packageId") if isinstance(p, dict) else None for p in pkgs]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        return error(400, "INVALID_PARAMS", "invalid package ids")
    try:
        deadline = time.monotonic() + 40
        decs = await asyncio.gather(*(decide(p, data.get("policyRevision"), deadline) for p in pkgs))
    except Exception:
        return error(503, "UNAVAILABLE", "decision engine unavailable")
    task_id = str(uuid.uuid4())
    ctx = msg.get("contextId") or str(uuid.uuid4())
    proposals = []
    for pid, dec in zip(ids, decs):
        proposals.append({
            "packageId": pid,
            "actionId": "act-" + digest([task_id, pid])[:28],
            "action": dec["action"],
            "facts": dec["facts"],
            "evidenceRefs": [f"[{r}]" if KEEP_BRACKETS else r for r in dec["evidenceRefs"]],
            "rationale": rationale(dec),
        })
    stored_msg = dict(msg)
    stored_msg["taskId"], stored_msg["contextId"] = task_id, ctx
    task = {
        "id": task_id,
        "contextId": ctx,
        "status": {"state": "TASK_STATE_INPUT_REQUIRED", "timestamp": now()},
        "artifacts": [{
            "artifactId": "proposals-" + task_id,
            "name": "invoice-action-proposals",
            "parts": [{"mediaType": PROP_MT, "data": {"batchId": data["batchId"], "proposals": proposals}}],
        }],
        "history": [stored_msg],
    }
    rec = {"principal": principal, "task": task, "batchId": data["batchId"]}
    kv_put(NS_TASK, task_id, rec)
    kv_put(NS_MSG, mkey, {"hash": mhash, "taskId": task_id})
    return resp({"task": view(rec, hl)})


async def continuation(principal, msg, mkey, mhash, hl):
    task_id = msg["taskId"]
    rec = load_task(principal, task_id)
    if not rec:
        return error(404, "TASK_NOT_FOUND", "task not found")
    async with lock_for(("a2a-task", task_id)):
        rec = load_task(principal, task_id)
        task = rec["task"]
        if task["status"]["state"] in TERMINAL:
            return error(409, "TASK_TERMINAL", "task is in a terminal state")
        if task["status"]["state"] != "TASK_STATE_INPUT_REQUIRED":
            return error(409, "INVALID_STATE", "task is not awaiting input")
        if msg.get("contextId") != task["contextId"]:
            return error(400, "INVALID_PARAMS", "context mismatch")
        parts = [p for p in msg["parts"] if isinstance(p, dict) and p.get("mediaType") == RES_MT]
        if len(parts) != 1 or len(msg["parts"]) != 1 or not isinstance(parts[0].get("data"), dict):
            return error(400, "INVALID_PARAMS", "expected one invoice-action-results part")
        data = parts[0]["data"]
        if data.get("batchId") != rec["batchId"]:
            return error(400, "INVALID_PARAMS", "batch mismatch")
        results = data.get("results")
        props = {p["packageId"]: p for p in task["artifacts"][0]["parts"][0]["data"]["proposals"]}
        if not isinstance(results, list) or len(results) != len(props):
            return error(400, "INVALID_PARAMS", "results must cover every proposal")
        seen = set()
        for r in results:
            if not isinstance(r, dict):
                return error(400, "INVALID_PARAMS", "invalid result")
            p = props.get(r.get("packageId"))
            if not p or r["packageId"] in seen:
                return error(400, "INVALID_PARAMS", "unknown or duplicate package")
            seen.add(r["packageId"])
            if r.get("actionId") != p["actionId"] or r.get("action") != p["action"]:
                return error(400, "INVALID_PARAMS", "action mismatch")
            if r.get("outcome") not in ("ACCEPTED", "REJECTED"):
                return error(400, "INVALID_PARAMS", "invalid outcome")
            if r["outcome"] == "ACCEPTED" and (not isinstance(r.get("receiptNonce"), str) or not r["receiptNonce"]):
                return error(400, "INVALID_PARAMS", "missing receipt nonce")
        executions = []
        for r in results:
            if r["outcome"] != "ACCEPTED":
                continue
            p = props[r["packageId"]]
            executions.append({
                "packageId": p["packageId"], "actionId": p["actionId"], "action": p["action"],
                "receiptNonce": r["receiptNonce"], "facts": p["facts"], "evidenceRefs": p["evidenceRefs"],
            })
        task["history"].append(msg)
        task["artifacts"].append({
            "artifactId": "receipts-" + task_id,
            "name": "invoice-action-receipts",
            "parts": [{"mediaType": RCPT_MT, "data": {"batchId": rec["batchId"], "executions": executions}}],
        })
        task["status"] = {"state": "TASK_STATE_COMPLETED", "timestamp": now()}
        kv_put(NS_TASK, task_id, rec)
        kv_put(NS_MSG, mkey, {"hash": mhash, "taskId": task_id})
        return resp({"task": view(rec, hl)})


@router.get("/a2a/tasks/{task_id}")
async def get_task(task_id: str, request: Request):
    principal, e = check_headers(request, False)
    if e:
        return e
    rec = load_task(principal, task_id)
    if not rec:
        return error(404, "TASK_NOT_FOUND", "task not found")
    hl = request.query_params.get("historyLength")
    return resp(view(rec, int(hl) if hl and hl.isdigit() else None))


@router.get("/a2a/tasks")
async def list_tasks(request: Request):
    principal, e = check_headers(request, False)
    if e:
        return e
    tasks = [rec["task"] for _, rec in kv_list(NS_TASK) if rec["principal"] == principal]
    ctx = request.query_params.get("contextId")
    if ctx:
        tasks = [t for t in tasks if t["contextId"] == ctx]
    tasks.reverse()
    out, size = [], 0
    for t in tasks:  # keep listing under the response size cap
        size += len(canon(t))
        if size > 400_000:
            break
        out.append(t)
    return resp({"tasks": out, "nextPageToken": "", "pageSize": len(out), "totalSize": len(tasks)})


@router.post("/a2a/tasks/{task_id}:cancel")
async def cancel_task(task_id: str, request: Request):
    principal, e = check_headers(request, False)
    if e:
        return e
    rec = load_task(principal, task_id)
    if not rec:
        return error(404, "TASK_NOT_FOUND", "task not found")
    async with lock_for(("a2a-task", task_id)):
        rec = load_task(principal, task_id)
        task = rec["task"]
        if task["status"]["state"] in TERMINAL:
            return error(409, "TASK_NOT_CANCELABLE", "task is not cancelable")
        task["status"] = {"state": "TASK_STATE_CANCELED", "timestamp": now()}
        kv_put(NS_TASK, task_id, rec)
        return resp(task)
