from pydantic import BaseModel
from typing import Optional, List


class Book(BaseModel):
    BookTitle: Optional[str]
    BID: Optional[str]
    BranchName: str
    CallNumber: str
    StatusDesc: str
    DueDate: str
    InsertTime: int


class Library(BaseModel):
    Library: List[Book]


# Models for interacting with database
# I need to create a read and write class... (from udemy course)
class BookInfo(BaseModel):
    BID: str
    BookTitle: str

    class Config:
        orm_mode = True

class BookInfoCreate(BookInfo):
    pass

class BookAvail(BaseModel):
    BID: str
    ItemNo: str
    BranchName: str
    CallNumber: str
    StatusDesc: str
    DueDate: str
    InsertTime: int

    class Config:
        orm_mode = True

class BookAvailCreate(BookAvail):
    pass


class UserBook(BaseModel):
    user_book_id: str
    UserName: str
    BID: str

    class Config:
        orm_mode = True


class UserBookCreate(UserBook):
    pass


class User(BaseModel):
    ID: str
    UserName: str
    HashedPassword: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    UserName: str
    HashedPassword: str
