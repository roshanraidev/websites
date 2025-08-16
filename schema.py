from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel

class CategoryRead(SQLModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    created_at: datetime
    updated_at: datetime

class PostRead(SQLModel):
    id: int
    title: str
    slug: str
    category_id: Optional[int]
    cover_url: Optional[str]
    status: str
    excerpt: Optional[str]
    content: Optional[str]
    read_time: int
    views: int
    created_at: datetime
    updated_at: datetime
