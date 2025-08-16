from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from categories import router as categories_router
from blog import router as posts_router

app = FastAPI()

# Routers
app.include_router(categories_router)
app.include_router(posts_router)

# Ensure uploads dir exists and mount it (for /uploads/categories/... etc.)
Path("uploads").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
