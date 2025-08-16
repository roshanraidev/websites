from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import init_db
from route.categories import router as categories_router
from route.blog import router as posts_router

app = FastAPI()

# Initialize DB
init_db()

# Routers
app.include_router(categories_router)
app.include_router(posts_router)

# Mount uploads (images)
Path("uploads/categories").mkdir(parents=True, exist_ok=True)
Path("uploads/posts").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount templates directory
templates = Jinja2Templates(directory="templates")

# Root route → render admin.html
@app.get("/")
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
