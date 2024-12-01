"""
FastAPI dependencies
"""

from typing import Annotated

from fastapi import Cookie, Depends
from pymongo import MongoClient
from supabase import create_client, Client
from nlb_catalogue_client import AuthenticatedClient

from src.config import settings


def get_sdb():
    """Return supabase db client connection"""
    client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    try:
        yield client
    finally:
        client.auth.sign_out()


SDBDep = Annotated[Client, Depends(get_sdb)]


def username_email_resol(user_info: Annotated[str | None, Cookie()] = None):
    """In the current new flow, username == email
    To cover legacy situation where username != email
    """
    if not user_info:
        return None
    email, username = user_info.split(" | ")
    return username if username else email


UsernameDep = Annotated[str | None, Depends(username_email_resol)]


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
