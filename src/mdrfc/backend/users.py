from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    email: str
    name_last: str
    name_first: str
    is_verified: bool
    verified_at: datetime | None
    created_at: datetime


class UserInDB(User):
    password_argon2: str
    verification_token_hash: str | None
    verification_token_expires_at: datetime | None
