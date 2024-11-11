"""
FastAPI dependencies
"""

from typing import Annotated

from fastapi import Cookie, Depends
from pymongo import MongoClient
from supabase import create_client, Client

from src import m_db
from src.config import settings


def get_sdb():
    """Return supabase db client connection"""
    client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    try:
        yield client
    finally:
        client.auth.sign_out()


SDBDep = Annotated[Client, Depends(get_sdb)]


async def get_mdb():
    """Return mongo db client connection"""
    yield m_db.connect_mdb()


MDBDep = Annotated[MongoClient, Depends(get_mdb)]


def username_email_resol(user_info: Annotated[str | None, Cookie()] = None):
    """In the current new flow, username == email
    To cover legacy situation where username != email
    """
    if not user_info:
        return None
    email, username = user_info.split(" | ")
    return username if username else email


UsernameDep = Annotated[str | None, Depends(username_email_resol)]
