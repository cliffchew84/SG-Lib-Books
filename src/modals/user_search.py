from typing import ClassVar

from pydantic import BaseModel

from src.modals.base import ResponseBase, CreateBase, UpdateBase


class UserSearchBase(BaseModel):
    """User Search Table"""

    """Username (PK)"""
    UserName: str

    """Database insert time (milliseconds after utc)"""
    search_time: int

    """Search title"""
    Title: str

    """Search author"""
    Author: str


class UserSearch(ResponseBase, UserSearchBase):
    table_name: ClassVar[str] = "user_search"
    pk: ClassVar[str] = "UserName"


class UserSearchCreate(CreateBase, UserSearch):
    """UserSearch model for creating new user-book relationship"""


class UserSearchUpdate(UpdateBase, UserSearchBase):
    """UserSearch model for updating user-book relationship"""
