from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import re

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Response
from sqlmodel import Session, select

from database import get_session
from route.model import Category, Post
from schema import PostRead

# uploads/posts/
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads" / "posts"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    s = (text or "").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"(^-|-$)", "", s)
    return s or "item"


async def save_cover(file: UploadFile | None) -> Optional[str]:
    if not file:
        return None
    safe = file.filename.replace(" ", "_")
    name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{safe}"
    dest = UPLOADS_DIR / name
    data = await file.read()
    dest.write_bytes(data)
    return f"/uploads/posts/{name}"


router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("", response_model=List[PostRead])
def list_posts(
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    stmt = select(Post)
    if q:
        stmt = stmt.where(Post.title.ilike(f"%{q}%"))
    if category_id is not None:
        stmt = stmt.where(Post.category_id == category_id)
    if status is not None:
        stmt = stmt.where(Post.status == status)
    stmt = stmt.order_by(Post.created_at.desc())
    return session.exec(stmt).all()


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("", response_model=PostRead, status_code=201)
async def create_post(
    title: str = Form(...),
    category_id: Optional[int] = Form(None),
    status: str = Form("active"),
    excerpt: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    read_time: int = Form(5),
    thumbnail: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    if content is None or not content.strip():
        raise HTTPException(status_code=400, detail="Content is required")

    if category_id is None:
        raise HTTPException(status_code=400, detail="Category must be selected")

    if not session.get(Category, category_id):
        raise HTTPException(status_code=400, detail="Invalid category_id")

    slug = slugify(title)
    exists = session.exec(select(Post).where(Post.slug == slug)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Post with similar slug already exists")

    cover_url = await save_cover(thumbnail) if thumbnail else None
    post = Post(
        title=title,
        slug=slug,
        category_id=category_id,
        status=status,
        excerpt=excerpt,
        content=content,
        read_time=read_time,
        cover_url=cover_url,
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.put("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    title: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    status: Optional[str] = Form(None),
    excerpt: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    read_time: Optional[int] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if title:
        if not title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        new_slug = slugify(title)
        if new_slug != post.slug:
            clash = session.exec(select(Post).where(Post.slug == new_slug)).first()
            if clash:
                raise HTTPException(status_code=400, detail="Another post already uses this slug")
        post.title = title
        post.slug = new_slug

    if category_id is not None:
        if category_id != 0 and not session.get(Category, category_id):
            raise HTTPException(status_code=400, detail="Invalid category_id")
        post.category_id = category_id

    if status is not None:
        post.status = status
    if excerpt is not None:
        post.excerpt = excerpt
    if content is not None:
        if not content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        post.content = content
    if read_time is not None:
        post.read_time = int(read_time)

    if thumbnail is not None:
        url = await save_cover(thumbnail)
        if url:
            post.cover_url = url

    post.updated_at = datetime.utcnow()
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(post)
    session.commit()
    return Response(status_code=204)  # ✅ No body for 204
