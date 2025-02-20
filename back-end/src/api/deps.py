"""
FastAPI dependencies
"""

from typing import Annotated, Literal

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from gotrue import User
from gotrue.errors import AuthApiError
from nlb_catalogue_client import AuthenticatedClient
from supabase import create_client, Client

from src.config import settings
from src.services.cloud_task import CloudTask
from src.services.firebase_messaging import FirebaseMessaging
from src.services.mailer import Mailer


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


async def get_current_user(
    access_token: AccessTokenDep,
) -> User | Literal["super"] | None:
    """get current user from access_token and validate same time. Accept service_role token"""
    if not super_client:
        raise HTTPException(status_code=500, detail="Super client not initialized")

    if not access_token:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    if access_token == settings.SUPABASE_KEY:
        return "super"
    try:
        user_rsp = super_client.auth.get_user(jwt=access_token)
    except AuthApiError as e:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        ) from e
    if not user_rsp:
        raise HTTPException(status_code=404, detail="User not found")
    return user_rsp.user


CurrentUser = Annotated[User | None, Depends(get_current_user)]


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


# External Services
def get_cloud_task():
    """Return cloud task client"""
    yield CloudTask(
        project=settings.GC_PROJECT_ID,
        location=settings.GC_LOCATION,
        queue=settings.GC_QUEUE,
        url=settings.GC_BACKEND_URI,
    )


CloudTaskDep = Annotated[CloudTask, Depends(get_cloud_task)]


def get_firebase_messaging():
    """Return firebase messaging client"""
    yield FirebaseMessaging(settings.GC_FIREBASE_SA_DICT)


MessagingDep = Annotated[FirebaseMessaging, Depends(get_firebase_messaging)]


def get_mailer():
    """Return mailer client"""
    yield Mailer(
        api_key=settings.MAILERSEND_API_KEY,
        sender_email=settings.MAILERSEND_EMAIL,
        sender_name=settings.MAILERSEND_NAME,
    )


MailerDep = Annotated[Mailer, Depends(get_mailer)]
