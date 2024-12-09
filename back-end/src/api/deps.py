"""
FastAPI dependencies
"""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from gotrue import User
from gotrue.errors import AuthApiError
from nlb_catalogue_client import AuthenticatedClient
from supabase import create_client, Client

from src.config import settings


super_client: Client | None = None


async def init_super_client() -> None:
    """for validation access_token init at life span event"""
    global super_client  # pylint: disable=global-statement
    super_client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
    )


def get_sdb():
    """Return supabase db client connection with service key"""
    client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    try:
        yield client
    finally:
        client.auth.sign_out()


SDBDep = Annotated[Client, Depends(get_sdb)]

# auto get access_token from header
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="please login by supabase-js to get token", auto_error=False
)
AccessTokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(access_token: AccessTokenDep) -> User:
    """get current user from access_token and  validate same time"""
    if not super_client:
        raise HTTPException(status_code=500, detail="Super client not initialized")

    if not access_token:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    try:
        user_rsp = super_client.auth.get_user(jwt=access_token)
    except AuthApiError as e:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        ) from e
    if not user_rsp:
        raise HTTPException(status_code=404, detail="User not found")
    return user_rsp.user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_nlb_api_client():
    """Return authenticated client to access NLB API"""
    yield AuthenticatedClient(
        base_url="https://openweb.nlb.gov.sg/api/v2/Catalogue/",
        auth_header_name="X-API-KEY",
        token=settings.nlb_rest_api_key,
        prefix="",
        headers={"X-APP-Code": settings.nlb_rest_app_id},
    )


NLBClientDep = Annotated[AuthenticatedClient, Depends(get_nlb_api_client)]
