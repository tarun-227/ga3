import os

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from . import a2a, incident, mailroom

app = FastAPI(title="GA3 agents", docs_url=None, redoc_url=None, openapi_url=None)
app.router.redirect_slashes = False
app.include_router(a2a.router)
app.include_router(mailroom.router)
app.include_router(incident.router)

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
