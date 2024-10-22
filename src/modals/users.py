from typing import ClassVar, Optional

from pydantic import BaseModel

from src.modals.base import ResponseBase, CreateBase, UpdateBase


class UserBase(BaseModel):
    """User Mapping Table"""

    """Username"""
    UserName: str
    email_address: str
    HashedPassword: Optional[str]
    latest_login: Optional[int]
    preferred_lib: Optional[
        str
    ]  # TODO: Create static modal after clarify naming requirement
    pw_qn: Optional[str]
    pw_ans: Optional[str]
    books_updated: Optional[float]
    registered_time: Optional[int]


class User(ResponseBase, UserBase):
    table_name: ClassVar[str] = "users"


class UserCreate(CreateBase, User):
    """User model for creating new user"""


class UserUpdateBase(BaseModel):
    UserName: str
    email_address: Optional[str]
    HashedPassword: Optional[str]
    latest_login: Optional[int]
    preferred_lib: Optional[
        str
    ]  # TODO: Create static modal after clarify naming requirement
    pw_qn: Optional[str]
    pw_ans: Optional[str]
    books_updated: Optional[float]
    registered_time: Optional[int]


class UserUpdate(UpdateBase, UserUpdateBase):
    """User model for updating user"""
