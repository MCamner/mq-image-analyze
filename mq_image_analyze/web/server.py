from __future__ import annotations

import dataclasses
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from mq_image_analyze.reasoning.prompts.reverse_prompt import build

app = FastAPI(title="mq-image-analyze", docs_url=None, redoc_url=None)

_WEB_DIR = Path(__file__).parents[2] / "web"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_WEB_DIR / "index.html")


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    exhaustive: str = Form("false"),
    conf: str = Form(""),
    vision_mode: str = Form("local-fast"),
    vision_model: str = Form(""),
) -> JSONResponse:
    suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        mode = "exhaustive" if exhaustive.lower() == "true" else "summary"
        conf_val = float(conf) if conf else None
        result = build(
            tmp_path,
            mode=mode,
            conf=conf_val,
            vision_mode=vision_mode,
            vision_model=vision_model or None,
        )
        return JSONResponse(dataclasses.asdict(result))
    finally:
        tmp_path.unlink(missing_ok=True)
