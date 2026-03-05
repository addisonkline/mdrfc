from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    email: str
    name_last: str
    name_first: str
    created_at: datetime


class UserInDB(User):
    password_argon2: str