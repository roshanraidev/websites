from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import init_db
from route.categories import router as categories_router
from route.blog import router as posts_router

app = FastAPI()

# Initialize database
init_db()

# API Routers
app.include_router(categories_router)
app.include_router(posts_router)

# Serve uploaded images
Path("uploads").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
