"""Deterministic stand-in for the LLM, used only by local tests (LLM_FAKE=1)."""
import json
import re


def answer(system, user):
    if "accounts-payable" in system:
        refs = json.loads(re.search(r"references found in this package: (\[.*?\])\n", user).group(1))
        return {"action": "hold_invoice", "vendorName": "Acme", "invoiceNumber": "INV-1", "amount": "123.45",
                "currency": "INR", "evidenceRefs": refs[-3:], "reason": "Bank details verification pending."}
    if "mailroom" in system:
        d = json.loads(user.split("Dossier:\n", 1)[1].split("\n\nYour previous", 1)[0])
        line = d["sources"][0]["lines"][0]
        return {"action": "no_action", "targetId": None,
                "payload": {"reasonCode": "INFORMATIONAL", "referenceId": d["sources"][0]["sourceId"]},
                "evidence": [line["lineId"]]}
    body = json.loads(user.split("\n\nPrevious", 1)[0])
    ev = re.findall(r"\[(ev_[A-Za-z0-9_]+)\]", body["incident"]["transcript"])
    dt = body["diagnosticTools"]
    return {"rootCause": body["incident"]["allowedRootCauses"][0], "evidence": ev[:2],
            "diagnostics": [{"toolName": t["name"], "arguments": {"service": body["incident"]["service"]}, "evidence": [ev[0]]} for t in dt[:2]],
            "effect": {"toolName": body["policy"]["effectTools"][0], "arguments": {"service": body["incident"]["service"]}, "evidence": [ev[1]]}}
