from fastapi import FastAPI
from categories import router as categories_router
from posts import router as posts_router

app = FastAPI()
app.include_router(categories_router)
app.include_router(posts_router)
