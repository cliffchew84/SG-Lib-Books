from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.books import router as books_router
from src.api.search import router as search_router
from src.api.user import router as user_router

api = APIRouter()
api.include_router(auth_router, prefix="/auth", tags=["auth"])
api.include_router(books_router, prefix="/books", tags=["books"])
api.include_router(search_router, prefix="/search", tags=["search"])
api.include_router(user_router, prefix="/user", tags=["user"])
