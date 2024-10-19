"""
FastAPI dependencies
"""

from typing import Annotated

from fastapi import Depends
from supabase import Client

from src import supa_db


async def get_sdb():
    yield supa_db.connect_sdb()


SDBDep = Annotated[Client, Depends(get_sdb)]
