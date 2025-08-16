# main.py
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import init_db
from route.categories import router as categories_router
from route.blog import router as posts_router
from route.banner import router as banner_router  # 👈 Banner API

app = FastAPI()

# ---------- Init DB ----------
init_db()

# ---------- Routers ----------
app.include_router(categories_router)
app.include_router(posts_router)
app.include_router(banner_router)

# ---------- Uploads (static) ----------
# Ensure folders exist
Path("uploads/categories").mkdir(parents=True, exist_ok=True)
Path("uploads/posts").mkdir(parents=True, exist_ok=True)
Path("uploads/banner").mkdir(parents=True, exist_ok=True)
Path("uploads/profile").mkdir(parents=True, exist_ok=True)
Path("uploads/misc").mkdir(parents=True, exist_ok=True)

# Serve /uploads/*
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ---------- Templates ----------
templates = Jinja2Templates(directory="templates")


# ---------- Simple uploader used by the Admin UI ----------
# JS calls: POST /api/upload with form fields: type, file
@app.post("/api/upload")
async def upload_file(
    type: str = Form("misc"),
    file: UploadFile = File(...),
):
    """
    Accepts a single file and saves it under /uploads/{bucket}/.
    Buckets: banner | categories | posts | profile | misc (default)
    Returns a public URL served by StaticFiles.
    """
    # Map friendly types to subdirectories
    bucket_map = {
        "banner": "banner",
        "banners": "banner",
        "category": "categories",
        "categories": "categories",
        "post": "posts",
        "posts": "posts",
        "profile": "profile",
        "avatar": "profile",
        "misc": "misc",
    }
    bucket = bucket_map.get(type.lower().strip(), "misc")

    # Sanitize filename
    orig = file.filename or "file"
    safe = "".join(ch if ch.isalnum() or ch in (".", "_", "-", " ") else "_" for ch in orig).strip()
    safe = safe.replace(" ", "_")
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    name = f"{ts}_{safe}" if safe else f"{ts}_file"

    # Compute destination path
    dest_dir = Path("uploads") / bucket
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / name

    # Save
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    dest.write_bytes(data)

    # Public URL
    url = f"/uploads/{bucket}/{name}"
    return {"url": url, "bucket": bucket, "filename": name}


# ---------- Admin UI ----------
@app.get("/")
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
