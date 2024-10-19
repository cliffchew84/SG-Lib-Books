from functools import lru_cache
from typing import Annotated

from pydantic import computed_field
from pydantic.networks import MultiHostUrl, UrlConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict

MongoSRVDsn = Annotated[MultiHostUrl, UrlConstraints(allowed_schemes=["mongodb+srv"])]


class Settings(BaseSettings):
    """Default configs for FastAPI server and environment variables"""

    APP_NAME: str = "SG Library Books"
    DESCRIPTION: str = (
        "View the availability of library books from the Singapore libraries"
    )
    VERSION: str = "0.1"

    # NLB API Key
    nlb_rest_app_id: str = "NLB_APP_ID"
    nlb_rest_api_key: str = "NLB_API_KEY"

    # MongoDB API Key
    mongo_pw: str = "MONGO_SECRET_KEY"

    @computed_field
    @property
    def MONGO_URL(self) -> MongoSRVDsn:
        """Return computed url for mongo db"""
        return MultiHostUrl(
            f"mongodb+srv://cliffchew84:{self.mongo_pw}@cliff-nlb.t0whddv.mongodb.net/?retryWrites=true&w=majority"
        )

    # Supabase API Key
    SUPABASE_URL: str = "http://127.0.0.1:54321"
    SUPABASE_KEY: str = ""

    SUPA_DB_HOST: str = "127.0.0.1"
    SUPA_DB_PORT: str = "54322"
    SUPA_DB_NAME: str = "postgres"
    SUPA_DB_USER: str = "postgres"
    SUPA_DB_PASSWORD: str = "postgres"

    SUPABASE_JWT_SECRET: str = ""

    # Google OAuth Secrets
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    # Fill up setting properties using .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
