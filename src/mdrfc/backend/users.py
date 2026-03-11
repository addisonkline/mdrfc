from datetime import datetime
import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel

import mdrfc.backend.constants as consts


USERNAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*[a-z0-9]$|^[a-z0-9]$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_username(username: str) -> str:
    if len(username) < consts.LEN_USERNAME_MIN:
        raise ValueError(f"username must be at least {consts.LEN_USERNAME_MIN} characters long")
    if len(username) > consts.LEN_USERNAME_MAX:
        raise ValueError(f"username must be no greater than {consts.LEN_USERNAME_MAX} characters long")
    username = username.lower()
    if not USERNAME_RE.fullmatch(username):
        raise ValueError("invalid username schema")
    return username


def validate_email(email: str) -> str:
    if len(email) < consts.LEN_EMAIL_MIN:
        raise ValueError(f"email must be at least {consts.LEN_EMAIL_MIN} characters long")
    if len(email) > consts.LEN_EMAIL_MAX:
        raise ValueError(f"email must be no greater than {consts.LEN_EMAIL_MAX} characters long")
    email = email.lower()
    if not EMAIL_RE.fullmatch(email):
        raise ValueError("invalid email schema")
    return email


def validate_password(password: str) -> str:
    if len(password) < consts.LEN_PASSWORD_PLAIN_MIN:
        raise ValueError(f"password must be at least {consts.LEN_PASSWORD_PLAIN_MIN} characters long")
    if not password.strip():
        raise ValueError("password must not be all whitespace")
    return password


def validate_name_last(name: str) -> str:
    if len(name) < consts.LEN_NAME_LAST_MIN:
        raise ValueError(f"last name must be at least {consts.LEN_NAME_LAST_MIN} characters long")
    if len(name) > consts.LEN_NAME_LAST_MAX:
        raise ValueError(f"last name must be no greater than {consts.LEN_NAME_LAST_MAX} characters long")
    return name


def validate_name_first(name: str) -> str:
    if len(name) < consts.LEN_NAME_FIRST_MIN:
        raise ValueError(f"first name must be at least {consts.LEN_NAME_FIRST_MIN} characters long")
    if len(name) > consts.LEN_NAME_FIRST_MAX:
        raise ValueError(f"first name must be no greater than {consts.LEN_NAME_FIRST_MAX} characters long")
    return name


class User(BaseModel):
    id: int
    username: Annotated[str, AfterValidator(validate_username)]
    email: Annotated[str, AfterValidator(validate_email)]
    name_last: Annotated[str, AfterValidator(validate_name_last)]
    name_first: Annotated[str, AfterValidator(validate_name_first)]
    is_verified: bool
    verified_at: datetime | None
    created_at: datetime
    is_admin: bool = False


class UserInDB(User):
    password_argon2: str
    verification_token_hash: str | None
    verification_token_expires_at: datetime | None
