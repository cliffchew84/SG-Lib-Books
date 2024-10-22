from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class CreateBase(BaseModel):
    """Properties to receive on item creation"""


class UpdateBase(BaseModel):
    """Properties to receive on item update"""


class ResponseBase(BaseModel):
    """Properties to return to client"""

    table_name: ClassVar[str] = "ResponseBase".lower()
    pk: ClassVar[str] = "id"
    Config: ClassVar[ConfigDict] = ConfigDict(
        extra="ignore", arbitrary_types_allowed=True
    )
