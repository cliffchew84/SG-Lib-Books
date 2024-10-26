from typing import ClassVar, Optional

from pydantic import BaseModel

from src.modals.base import ResponseBase, CreateBase, UpdateBase


class UserBase(BaseModel):
    """User Mapping Table"""

    """Username"""
    UserName: str
    email_address: str
    HashedPassword: Optional[str] = None
    latest_login: Optional[int] = None
    preferred_lib: Optional[str] = (
        None  # TODO: Create static modal after clarify naming requirement
    )
    pw_qn: Optional[str] = None
    pw_ans: Optional[str] = None
    books_updated: Optional[float] = None
    registered_time: Optional[int] = None


class User(ResponseBase, UserBase):
    table_name: ClassVar[str] = "users"
    pk: ClassVar[str] = "UserName"


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
