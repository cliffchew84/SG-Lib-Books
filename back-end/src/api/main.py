from fastapi import (
    APIRouter,
)

from src.api.routes.books import router as books_router
from src.api.routes.library import router as library_router
from src.api.routes.search import router as search_router
from src.api.routes.user import router as user_router

api_router = APIRouter()
api_router.include_router(books_router, prefix="/books", tags=["books"])
api_router.include_router(library_router, prefix="/lib", tags=["lib"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
