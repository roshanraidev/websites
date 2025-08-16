"""Database config & session dependency for Wow Blog (FastAPI + SQLModel).

Usage in your `main.py`:

    from fastapi import FastAPI
    from database import init_db
    from categories import router as categories_router
    from posts import router as posts_router

    app = FastAPI()
    init_db()  # create tables if not present
    app.include_router(categories_router)
    app.include_router(posts_router)

In your routers (`categories.py`, `posts.py`), import the shared session:

    from database import get_session

Environment:
- DATABASE_URL  -> full SQLAlchemy URL (e.g. "sqlite:///./wowblog.db")
- WOWBLOG_DB    -> path to SQLite file (used only if DATABASE_URL not set)
- SQL_ECHO      -> set to any non-empty value to enable SQL echo logs
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine

# ----------------------------------------
# URL / Engine
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "wowblog.db"
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DEFAULT_DB_PATH}"

# For SQLite + FastAPI concurrency we need check_same_thread=False
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    echo=bool(os.getenv("SQL_ECHO")),
    connect_args=_connect_args,
)


# ----------------------------------------
# Session dependency
# ----------------------------------------
def get_session() -> Iterator[Session]:
    """Yield a SQLModel Session for FastAPI dependency injection."""
    with Session(engine) as session:
        yield session


# ----------------------------------------
# Init (create tables)
# ----------------------------------------
def init_db() -> None:
    """Create all tables if they don't exist.

    We import models inside to ensure SQLModel sees all table classes before
    creating metadata.
    """
    # Import models so SQLModel.metadata is populated
    import model  # noqa: F401

    SQLModel.metadata.create_all(engine)
