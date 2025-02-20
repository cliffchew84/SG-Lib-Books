from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Default configs for FastAPI server and environment variables"""

    APP_NAME: str = "SG Library Books"
    DESCRIPTION: str = (
        "View the availability of library books from the Singapore libraries"
    )
    VERSION: str = "1.0"
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
        "https://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4173",
        "http://localhost:5173",
        "localhost",
        "https://sg-nlb-available-books.onrender.com",
        "https://sg-lib-books.web.app",
    ]

    # NLB API Key
    nlb_rest_app_id: str = "NLB_APP_ID"
    nlb_rest_api_key: str = "NLB_API_KEY"

    # Supabase API Key
    SUPABASE_URL: str = "http://127.0.0.1:54321"
    SUPABASE_KEY: str = ""

    SUPA_DB_HOST: str = "127.0.0.1"
    SUPA_DB_PORT: str = "54322"
    SUPA_DB_NAME: str = "postgres"
    SUPA_DB_USER: str = "postgres"
    SUPA_DB_PASSWORD: str = "postgres"

    # Google Cloud Configs
    GC_PROJECT_ID: str = ""
    GC_LOCATION: str = "asia-southeast1"
    GC_QUEUE: str = ""
    GC_BACKEND_URI: str = ""
    GC_FIREBASE_SA_DICT: dict = {}

    # Mailersend API Key
    MAILERSEND_API_KEY: str = ""
    MAILERSEND_EMAIL: str = ""
    MAILERSEND_NAME: str = "SG Lib Books"

    # Fill up setting properties using .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
