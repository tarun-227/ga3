"""Shared helpers: canonical JSON, hashing, SQLite storage, LLM client."""
import asyncio
import hashlib
import json
import os
import re
import sqlite3
import threading

import httpx

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "state.db")

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://aipipe.org/openai/v1").rstrip("/")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4.1-mini")


# ---------------------------------------------------------------- canonical JSON
def _norm(v):
    if isinstance(v, bool) or v is None or isinstance(v, (int, str)):
        return v
    if isinstance(v, float):
        return int(v) if v.is_integer() and abs(v) < 2**53 else v
    if isinstance(v, dict):
        return {k: _norm(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_norm(x) for x in v]
    return v


def canon(v) -> str:
    """Recursively key-sorted compact JSON, JS-compatible number spelling."""
    return json.dumps(_norm(v), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(s) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def digest(v) -> str:
    return sha256_hex(canon(v))


# ---------------------------------------------------------------- storage
_db_lock = threading.Lock()
_conn = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
_conn.execute("PRAGMA journal_mode=WAL")
_conn.execute("CREATE TABLE IF NOT EXISTS kv (ns TEXT, k TEXT, v TEXT, PRIMARY KEY (ns, k))")


def kv_get(ns, k):
    with _db_lock:
        row = _conn.execute("SELECT v FROM kv WHERE ns=? AND k=?", (ns, k)).fetchone()
    return json.loads(row[0]) if row else None


def kv_put(ns, k, v):
    with _db_lock:
        _conn.execute("INSERT OR REPLACE INTO kv (ns, k, v) VALUES (?, ?, ?)", (ns, k, json.dumps(v)))


def kv_list(ns, prefix=""):
    with _db_lock:
        rows = _conn.execute(
            "SELECT k, v FROM kv WHERE ns=? AND k LIKE ? ORDER BY rowid", (ns, prefix.replace("%", "") + "%")
        ).fetchall()
    return [(k, json.loads(v)) for k, v in rows]


_locks: dict = {}
ERRORS: list = []


def log_error(where, exc):
    """Keep the last few failures (no request content) for /debug/errors."""
    import datetime
    msg = f"{type(exc).__name__}: {str(exc)[:300]}"
    ERRORS.append({"at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z", "where": where, "error": msg})
    del ERRORS[:-100]
    print(f"[error] {where}: {msg}", flush=True)


def lock_for(key) -> asyncio.Lock:
    lk = _locks.get(key)
    if lk is None:
        lk = _locks[key] = asyncio.Lock()
    return lk


# ---------------------------------------------------------------- LLM
_llm_sem = asyncio.Semaphore(int(os.environ.get("LLM_CONCURRENCY", "16")))


async def llm_json(system: str, user: str, timeout: float = 40.0, model: str | None = None) -> dict:
    """One chat completion that must return a JSON object."""
    if os.environ.get("LLM_FAKE"):
        from . import fake_llm
        return fake_llm.answer(system, user)
    if not LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY not configured")
    body = {
        "model": model or LLM_MODEL,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    loop = asyncio.get_running_loop()
    end = loop.time() + timeout
    async with _llm_sem:
        async with httpx.AsyncClient(timeout=max(1.0, end - loop.time())) as client:
            for attempt in range(3):
                r = await client.post(
                    f"{LLM_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {LLM_API_KEY}"},
                    json=body,
                    timeout=max(1.0, end - loop.time()),
                )
                if (r.status_code in (429, 500, 502, 503, 504) and end - loop.time() > 4
                        and "usage" not in r.text.lower() and "quota" not in r.text.lower()):
                    await asyncio.sleep(1 + attempt)
                    continue
                break
    if r.status_code >= 400:
        raise RuntimeError(f"LLM HTTP {r.status_code}: {r.text[:200]}")
    text = r.json()["choices"][0]["message"]["content"]
    return parse_json_obj(text)


def parse_json_obj(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise
        return json.loads(m.group(0))
