from fastapi import APIRouter

from src.api.auth import router as auth_router

api = APIRouter()
api.include_router(auth_router, prefix="/auth", tags=["auth"])
