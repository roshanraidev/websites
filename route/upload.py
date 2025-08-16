# route/uploads.py
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["upload"])

BASE = Path("uploads")
BASE.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    type: str = Form("misc"),
):
    # folder sanitization
    safe_type = "".join(ch for ch in type if ch.isalnum() or ch in ("-", "_")).strip() or "misc"
    folder = BASE / safe_type
    folder.mkdir(parents=True, exist_ok=True)

    # save file
    safe_name = file.filename.replace(" ", "_")
    name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{safe_name}"
    dest = folder / name
    data = await file.read()
    dest.write_bytes(data)

    # static URL (served by /uploads mount)
    url = f"/uploads/{safe_type}/{name}"
    return JSONResponse({"url": url})
