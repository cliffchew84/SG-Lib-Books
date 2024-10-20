"""
FastAPI dependencies
"""

from typing import Annotated

from fastapi import Cookie, Depends
from supabase import Client
from pymongo import MongoClient

from src import supa_db
from src import m_db


def get_sdb():
    """Return supabase db client connection"""
    client = supa_db.connect_sdb()
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


UsernameDep = Annotated[str, Depends(username_email_resol)]
