from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from pydantic.types import conint

#
# users
#


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):  # Need password for user creation
    password: str


class UserOut(UserBase):  # Remove password field from response
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


#
# posts
#


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True


#
# auth
#


class UserLogin(UserCreate):  # email + password
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]


#
# votes
#


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)  # Contraint to an integer of max 1


#
# Status
#

class StatusMessage(BaseModel):
    message: str

class StatusOut(StatusMessage):
    status: str
    version: conint(ge=0)
