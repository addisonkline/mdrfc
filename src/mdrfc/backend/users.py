from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class UserInDB(User):
    password_argon2: str