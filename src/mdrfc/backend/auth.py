from datetime import datetime, timedelta, timezone
from os import getenv
from typing import Annotated, Any

import dotenv
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

from mdrfc.backend.db import (
    get_user_from_db
)
from mdrfc.backend.users import (
    User,
    UserInDB
)


dotenv.load_dotenv()
SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("JWT_ALGORITHM")

if SECRET_KEY is None:
    raise RuntimeError("environment variable SECRET_KEY is required but was not found")
if ALGORITHM is None:
    raise RuntimeError("environment variable JWT_ALGORITHM is required but was not found")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(
    password_plain: str,
    password_hashed: str,
) -> bool:
    return password_hash.verify(password_plain, password_hashed)


def get_password_hash(
    password_plain: str
) -> str:
    return password_hash.hash(password_plain)


async def authenticate_user(
    username: str,
    password: str,
) -> UserInDB | bool:
    user = await get_user_from_db(username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.password_argon2):
        return False
    
    return user


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=401,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # type: ignore
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    if token_data.username is None:
        raise credentials_exception
    user = await get_user_from_db(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


