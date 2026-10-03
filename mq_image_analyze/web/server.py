from __future__ import annotations

import dataclasses
import io
import tempfile
from pathlib import Path

from fastapi import HTTPException
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image, UnidentifiedImageError

from mq_image_analyze.reasoning.prompts.reverse_prompt import build
from mq_image_analyze.vision.semantic.provider import normalize_vision_mode

app = FastAPI(title="mq-image-analyze", docs_url=None, redoc_url=None)

_WEB_DIR = Path(__file__).parent

# Same formats the MCP tools accept. Uploads are checked before anything is
# written to disk: extension, then byte size, then the pixel count Pillow reads
# from the header, so a small file that decodes to a huge bitmap is refused too.
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_IMAGE_PIXELS = 50_000_000


def _validated_upload(filename: str, data: bytes) -> str:
    """Return the file suffix, or raise HTTPException for an unacceptable upload."""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image format: {suffix or '(none)'} (allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))})",
        )
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"Upload too large (max {MAX_UPLOAD_BYTES} bytes)")
    try:
        with Image.open(io.BytesIO(data)) as img:
            width, height = img.size
    except Image.DecompressionBombError as exc:
        raise HTTPException(status_code=413, detail=f"Image has too many pixels (max {MAX_IMAGE_PIXELS})") from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=422, detail="Upload is not a readable image") from exc
    if width * height > MAX_IMAGE_PIXELS:
        raise HTTPException(status_code=413, detail=f"Image has too many pixels (max {MAX_IMAGE_PIXELS})")
    return suffix


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
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    suffix = _validated_upload(file.filename or "", data)
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)

    try:
        mode = "exhaustive" if exhaustive.lower() == "true" else "summary"
        try:
            conf_val = float(conf) if conf else None
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="conf must be a number") from exc
        try:
            selected_vision_mode = normalize_vision_mode(vision_mode)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        result = build(
            tmp_path,
            mode=mode,
            conf=conf_val,
            vision_mode=selected_vision_mode,
            vision_model=vision_model or None,
        )
        return JSONResponse(dataclasses.asdict(result))
    finally:
        tmp_path.unlink(missing_ok=True)
