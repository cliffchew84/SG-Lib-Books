from datetime import time
from typing import ClassVar

from pydantic import BaseModel
from src.modals.base import ResponseBase, CreateBase, UpdateBase


class LibraryBase(BaseModel):
    """Library Info"""

    name: str
    opening_status: str
    start_hour: time | None
    end_hour: time | None
    opening_description: str | None
    address: str | None
    cover_url: str | None


class Library(ResponseBase, LibraryBase):
    table_name: ClassVar[str] = "libraries"
    pk: ClassVar[str] = "name"


class LibraryCreate(CreateBase, LibraryBase):
    """Framework model for creating new book_info"""


class LibraryUpdateBase(BaseModel):
    name: str
    opening_status: str | None = None
    start_hour: time | None = None
    end_hour: time | None = None
    opening_description: str | None = None
    address: str | None = None
    cover_url: str | None = None


class LibraryUpdate(UpdateBase, LibraryUpdateBase):
    """Framework model for updating existing book info"""
