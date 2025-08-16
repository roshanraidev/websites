# route/banner.py
from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
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
        raise HTTPException(status_code=404, detail="Banner not configured")
    return b

@router.put("", response_model=BannerRead)
def upsert_banner(payload: BannerUpdate, session: Session = Depends(get_session)):
    b = _get_singleton(session)
    if not b:
        b = Banner()
        session.add(b)

    # update only provided fields
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(b, field, value)

    b.updated_at = datetime.utcnow()
    session.add(b)
    session.commit()
    session.refresh(b)
    return b
