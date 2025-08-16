from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import re

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from database import get_session
from route.model import Category, Post
from schema import CategoryRead  # your single file schemas

# uploads/categories/
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads" / "categories"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    s = (text or "").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"(^-|-$)", "", s)
    return s or "item"


async def save_thumbnail(file: UploadFile | None) -> Optional[str]:
    if not file:
        return None
    safe = file.filename.replace(" ", "_")
    name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{safe}"
    dest = UPLOADS_DIR / name
    data = await file.read()
    dest.write_bytes(data)
    return f"/uploads/categories/{name}"


router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=List[CategoryRead])
def list_categories(q: Optional[str] = None, session: Session = Depends(get_session)):
    stmt = select(Category)
    if q:
        stmt = stmt.where(Category.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Category.created_at.desc())
    return session.exec(stmt).all()


@router.get("/{cat_id}", response_model=CategoryRead)
def get_category(cat_id: int, session: Session = Depends(get_session)):
    cat = session.get(Category, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.post("", response_model=CategoryRead, status_code=201)
async def create_category(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
):
    slug = slugify(name)
    exists = session.exec(select(Category).where(Category.slug == slug)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category with similar slug already exists")

    thumb_url = await save_thumbnail(thumbnail) if thumbnail else None
    cat = Category(name=name, slug=slug, description=description, thumbnail_url=thumb_url)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.put("/{cat_id}", response_model=CategoryRead)
async def update_category(
    cat_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
):
    cat = session.get(Category, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    if name:
        new_slug = slugify(name)
        if new_slug != cat.slug:
            clash = session.exec(select(Category).where(Category.slug == new_slug)).first()
            if clash:
                raise HTTPException(status_code=400, detail="Another category already uses this slug")
        cat.name = name
        cat.slug = new_slug

    if description is not None:
        cat.description = description

    if thumbnail is not None:
        url = await save_thumbnail(thumbnail)
        if url:
            cat.thumbnail_url = url

    cat.updated_at = datetime.utcnow()
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.delete("/{cat_id}", status_code=204)
async def delete_category(cat_id: int, session: Session = Depends(get_session)):
    cat = session.get(Category, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    # block delete if posts exist
    linked = session.exec(select(Post).where(Post.category_id == cat_id)).first()
    if linked:
        raise HTTPException(status_code=400, detail="Cannot delete category with existing posts")

    session.delete(cat)
    session.commit()
    return JSONResponse(status_code=204, content=None)
