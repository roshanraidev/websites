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
    

class BannerRead(SQLModel):
    id: int
    image1_url: Optional[str] = None
    image2_url: Optional[str] = None
    heading: Optional[str] = None
    content: Optional[str] = None
    btn1_text: Optional[str] = None
    btn1_link: Optional[str] = None
    btn2_text: Optional[str] = None
    btn2_link: Optional[str] = None

class BannerUpdate(SQLModel):
    image1_url: Optional[str] = None
    image2_url: Optional[str] = None
    heading: Optional[str] = None
    content: Optional[str] = None
    btn1_text: Optional[str] = None
    btn1_link: Optional[str] = None
    btn2_text: Optional[str] = None
    btn2_link: Optional[str] = None
