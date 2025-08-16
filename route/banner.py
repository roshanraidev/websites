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

@router.delete("")
def delete_banner(session: Session = Depends(get_session)):
    b = session.exec(select(Banner).limit(1)).first()
    if not b:
        raise HTTPException(status_code=404, detail="Banner not configured")
    session.delete(b)
    session.commit()
    return {"ok": True}

@router.put("", response_model=BannerRead)
def upsert_banner(
    raw: dict = Body(...),   # accept raw to allow legacy keys
    session: Session = Depends(get_session),
):
    """
    Upsert the single banner record.

    Accepts both:
      - Canonical fields: image1_url, image2_url, heading, content,
                          btn1_text, btn1_link, btn2_text, btn2_link
      - Legacy fields: go1, go2  (mapped to btn1_link, btn2_link)
    """
    # Legacy mapping
    if "go1" in raw and "btn1_link" not in raw:
        raw["btn1_link"] = raw.pop("go1")
    if "go2" in raw and "btn2_link" not in raw:
        raw["btn2_link"] = raw.pop("go2")

    payload = BannerUpdate(**raw)

    b = _get_singleton(session)
    if not b:
        b = Banner()
        session.add(b)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(b, field, value)

    b.updated_at = datetime.utcnow()
    session.add(b)
    session.commit()
    session.refresh(b)
    return b
