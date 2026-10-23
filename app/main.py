import hashlib
import json
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response

from . import a2a, incident, mailroom

app = FastAPI(title="GA3 agents", docs_url=None, redoc_url=None, openapi_url=None)
app.router.redirect_slashes = False
app.include_router(a2a.router)
app.include_router(mailroom.router)
app.include_router(incident.router)

# Request log for debugging grader runs. Readable only with the debug token (its SHA-256 is stored here).
DEBUG_TOKEN_SHA256 = os.environ.get("DEBUG_TOKEN_SHA256", "fbab577687308d0702e72c9adc40292d8e66f459d53b23d3e136509be3ddc811")
REQUEST_LOG: list = []
LOGGED = ("/incident", "/v2/", "/mailroom", "/a2a")


def _strip_sensitive(raw: bytes):
    try:
        body = json.loads(raw)
    except Exception:
        return raw[:2000].decode("utf-8", "replace")
    if isinstance(body, dict) and "sensitive" in body:
        body["sensitive"] = "[omitted]"
    return body


@app.middleware("http")
async def log_requests(request: Request, call_next):
    if not request.url.path.startswith(LOGGED):
        return await call_next(request)
    raw = await request.body()
    t0 = time.time()
    response = await call_next(request)
    chunks = [c async for c in response.body_iterator]
    out = b"".join(chunks)
    REQUEST_LOG.append({
        "t": round(t0, 3), "ms": int((time.time() - t0) * 1000), "method": request.method, "path": request.url.path,
        "headers": {k: v for k, v in request.headers.items() if k in ("traceparent", "tracestate", "content-type", "a2a-version")},
        "request": _strip_sensitive(raw) if raw else None,
        "status": response.status_code,
        "response": _strip_sensitive(out[:200_000]),
    })
    del REQUEST_LOG[:-150]
    return Response(content=out, status_code=response.status_code, headers=dict(response.headers),
                    media_type=response.media_type)


@app.get("/debug/requests")
async def debug_requests(token: str = "", path: str = "", limit: int = 40):
    if hashlib.sha256(token.encode()).hexdigest() != DEBUG_TOKEN_SHA256:
        return JSONResponse({"error": "forbidden"}, status_code=403)
    rows = [r for r in REQUEST_LOG if path in r["path"]]
    return {"count": len(rows), "requests": rows[-limit:]}


GLB = os.path.join(os.path.dirname(__file__), "face.glb")


@app.get("/debug/errors")
async def debug_errors():
    from .common import ERRORS
    return {"errors": ERRORS[-50:]}


@app.get("/")
async def health():
    return {"ok": True, "endpoints": ["/a2a/", "/mailroom", "/incident", "/face.glb"]}


@app.api_route("/face.glb", methods=["GET", "HEAD"])
async def face():
    return FileResponse(GLB, media_type="model/gltf-binary", headers={
        "Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=3600"})


@app.options("/face.glb")
async def face_options():
    return JSONResponse({}, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                                     "Access-Control-Allow-Headers": "*"})
