from datetime import datetime, timedelta, timezone
import hashlib
from os import getenv
import secrets
from typing import Annotated, Any

import dotenv
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

from mdrfc.backend.db import (
    get_user_from_db,
    register_user_in_db,
    verify_user_by_token_in_db,
)
import mdrfc.backend.constants as consts
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

EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES = int(
    getenv(
        "EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES",
        str(consts.MINUTES_EMAIL_VERIFICATION_TOKEN_EXPIRE),
    )
)
DEBUG_RETURN_VERIFICATION_TOKEN = getenv("AUTH_DEBUG_RETURN_VERIFICATION_TOKEN", "false").lower() == "true"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class SignupResult(BaseModel):
    created_at: datetime
    verification_expires_at: datetime
    verification_token: str


class EmailVerificationResult(BaseModel):
    username: str
    email: str
    verified_at: datetime


password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def normalize_username(username: str) -> str:
    return username.strip().lower()


def hash_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


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
    user = await get_user_from_db(normalize_username(username))
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.password_argon2):
        return False
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="email address not verified",
        )
    
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


async def get_current_user_if_one(
    token: Annotated[str | None, Depends(optional_oauth2_scheme)],
) -> UserInDB | None:
    if token is None:
        return None
    return await get_current_user(token)


async def get_current_active_user_if_one(
    current_user: Annotated[User | None, Depends(get_current_user_if_one)]
) -> User | None:
    return current_user


async def create_new_user(
    username: str,
    email: str,
    name_last: str,
    name_first: str,
    password: str
) -> SignupResult:
    timestamp = _utcnow()
    verification_token = generate_verification_token()
    verification_expires_at = timestamp + timedelta(minutes=EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES)

    user_in_db = UserInDB(
        id=-1,
        username=normalize_username(username),
        email=email.strip().lower(),
        name_last=name_last,
        name_first=name_first,
        password_argon2=get_password_hash(password),
        is_verified=False,
        verified_at=None,
        verification_token_hash=hash_verification_token(verification_token),
        verification_token_expires_at=verification_expires_at,
        created_at=timestamp
    )

    await register_user_in_db(user_in_db)

    return SignupResult(
        created_at=timestamp,
        verification_expires_at=verification_expires_at,
        verification_token=verification_token,
    )


async def verify_user_email(
    token: str,
) -> EmailVerificationResult:
    verified_at = _utcnow()
    user = await verify_user_by_token_in_db(
        verification_token_hash=hash_verification_token(token),
        verified_at=verified_at,
    )
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="verification token is invalid or expired",
        )

    return EmailVerificationResult(
        username=user.username,
        email=user.email,
        verified_at=verified_at,
    )
