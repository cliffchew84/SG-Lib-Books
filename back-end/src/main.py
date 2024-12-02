from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
)
from fastapi.middleware.cors import CORSMiddleware


from src.api.main import api_router
from src.api.deps import init_super_client
from src.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan for FastAPI Server"""
    # Initialise supabase connection
    await init_super_client()

    # Yield server to receive requests
    yield


# Application code
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)
