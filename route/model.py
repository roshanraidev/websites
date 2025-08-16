from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column, String


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    # unique, indexed slug
    slug: str = Field(sa_column=Column(String, unique=True, index=True))

    description: Optional[str] = None
    thumbnail_url: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    slug: str = Field(sa_column=Column(String, unique=True, index=True))

    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")

    cover_url: Optional[str] = None
    status: str = Field(default="active")  # "active" | "inactive"
    excerpt: Optional[str] = None
    content: Optional[str] = None

    read_time: int = Field(default=5)
    views: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Banner(SQLModel, table=True):
    __tablename__ = "banners"

    id: Optional[int] = Field(default=None, primary_key=True)

    image1_url: Optional[str] = None
    image2_url: Optional[str] = None
    heading: Optional[str] = None
    content: Optional[str] = None

    # dynamic buttons (text + URL)
    btn1_text: Optional[str] = None
    btn1_url: Optional[str] = None
    btn2_text: Optional[str] = None
    btn2_url: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
