# route/banner.py
from __future__ import annotations
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select

from database import get_session
from route.model import Banner
from schema import BannerRead, BannerUpdate

router = APIRouter(prefix="/api/banner", tags=["banner"])


def _get_singleton(session: Session) -> Banner | None:
    return session.exec(select(Banner).limit(1)).first()


@router.get("", response_model=BannerRead)
def get_banner(session: Session = Depends(get_session)):
    b = _get_singleton(session)
    if not b:
        # Frontend handles 404 as "not configured yet"
        raise HTTPException(status_code=404, detail="Banner not configured")
    return b


@router.get("/all", response_model=list[BannerRead])
def get_banner_list(session: Session = Depends(get_session)):
    """Handy for your 'List' table. Returns [] or [banner]."""
    return session.exec(select(Banner)).all()


@router.put("", response_model=BannerRead)
def upsert_banner(
    raw: dict = Body(...),  # accept raw JSON; we'll normalize keys
    session: Session = Depends(get_session),
):
    """
    Upsert the single banner record.

    Accepts:
      - image1_url, image2_url, heading, content,
        btn1_text, btn1_url, btn2_text, btn2_url
    Also accepted (legacy keys):
      - btn1_link -> btn1_url
      - btn2_link -> btn2_url
      - go1       -> btn1_url
      - go2       -> btn2_url
    """
    # Normalize legacy keys to *_url
    if "btn1_link" in raw and "btn1_url" not in raw:
        raw["btn1_url"] = raw.pop("btn1_link")
    if "btn2_link" in raw and "btn2_url" not in raw:
        raw["btn2_url"] = raw.pop("btn2_link")
    if "go1" in raw and "btn1_url" not in raw:
        raw["btn1_url"] = raw.pop("go1")
    if "go2" in raw and "btn2_url" not in raw:
        raw["btn2_url"] = raw.pop("go2")

    payload = BannerUpdate(**raw)

    b = _get_singleton(session)
    if not b:
        b = Banner()
        session.add(b)

    # Update only provided fields
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(b, field, value)

    b.updated_at = datetime.utcnow()
    session.add(b)
    session.commit()
    session.refresh(b)
    return b


@router.delete("")
def delete_banner(session: Session = Depends(get_session)):
    """Delete the singleton banner (idempotent)."""
    b = _get_singleton(session)
    if not b:
        return {"ok": True}
    session.delete(b)
    session.commit()
    return {"ok": True}
