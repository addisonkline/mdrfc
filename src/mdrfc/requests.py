import re
from typing import Annotated, Literal

from fastapi import HTTPException
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, SecretStr, field_validator

import mdrfc.backend.constants as consts


USERNAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*[a-z0-9]$|^[a-z0-9]$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_username(username: str) -> str:
    if len(username) < consts.LEN_USERNAME_MIN:
        raise HTTPException(
            status_code=422,
            detail=f"username must be at least {consts.LEN_USERNAME_MIN} characters"
        )
    if len(username) > consts.LEN_USERNAME:
        raise HTTPException(
            status_code=422,
            detail=f"username must be {consts.LEN_USERNAME} characters or less"
        )
    username = username.lower()
    if not USERNAME_RE.fullmatch(username):
        raise HTTPException(
            status_code=422,
            detail="username must contain only lowercase letters, digits, '.', '_' or '-'"
        )
    return username


def validate_email(email: str) -> str:
    if len(email) > consts.LEN_EMAIL:
        raise HTTPException(
            status_code=422,
            detail=f"email must be {consts.LEN_EMAIL} characters or less"
        )
    email = email.lower()
    if not EMAIL_RE.fullmatch(email):
        raise HTTPException(
            status_code=422,
            detail="email must be a valid email address"
        )
    return email


def validate_name_last(name: str) -> str:
    if len(name) == 0:
        raise HTTPException(
            status_code=422,
            detail="last name must not be empty"
        )
    if len(name) > consts.LEN_NAME_LAST:
        raise HTTPException(
            status_code=422,
            detail=f"last name must be {consts.LEN_NAME_LAST} characters or less"
        )
    return name


def validate_name_first(name: str) -> str:
    if len(name) == 0:
        raise HTTPException(
            status_code=422,
            detail="first name must not be empty"
        )
    if len(name) > consts.LEN_NAME_FIRST:
        raise HTTPException(
            status_code=422,
            detail=f"first name must be {consts.LEN_NAME_FIRST} characters or less"
        )
    return name


def validate_password(password: SecretStr) -> SecretStr:
    value = password.get_secret_value()
    if len(value) < consts.LEN_PASSWORD_PLAIN_MIN:
        raise HTTPException(
            status_code=422,
            detail=f"password must be at least {consts.LEN_PASSWORD_PLAIN_MIN} characters"
        )
    if len(value) > consts.LEN_PASSWORD_PLAIN:
        raise HTTPException(
            status_code=422,
            detail=f"password must be {consts.LEN_PASSWORD_PLAIN} characters or less"
        )
    if value.isspace():
        raise HTTPException(
            status_code=422,
            detail="password must not be whitespace only"
        )
    return password


class PostSignupRequest(BaseModel):
    """
    HTTP request object for `POST /signup`.
    """
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    username: Annotated[
        str,
        Field(min_length=consts.LEN_USERNAME_MIN, max_length=consts.LEN_USERNAME),
        AfterValidator(validate_username),
    ]
    email: Annotated[
        str,
        Field(min_length=3, max_length=consts.LEN_EMAIL),
        AfterValidator(validate_email),
    ]
    name_last: Annotated[
        str,
        Field(min_length=1, max_length=consts.LEN_NAME_LAST),
        AfterValidator(validate_name_last),
    ]
    name_first: Annotated[
        str,
        Field(min_length=1, max_length=consts.LEN_NAME_FIRST),
        AfterValidator(validate_name_first),
    ]
    password: Annotated[
        SecretStr,
        AfterValidator(validate_password),
    ]

    @field_validator("name_first", "name_last")
    @classmethod
    def validate_name_whitespace(cls, value: str) -> str:
        if not value:
            raise HTTPException(
                status_code=422,
                detail="name fields must not be empty"
            )
        return value


def validate_verification_token(token: SecretStr) -> SecretStr:
    value = token.get_secret_value()
    if len(value) < 32:
        raise HTTPException(
            status_code=422,
            detail="verification token is invalid"
        )
    return token


class PostVerifyEmailRequest(BaseModel):
    """
    HTTP request object for `POST /verify-email`.
    """
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    token: Annotated[SecretStr, AfterValidator(validate_verification_token)]


def validate_rfc_title(title: str) -> str:
    if len(title) > consts.LEN_RFC_TITLE:
        raise HTTPException(
            status_code=422,
            detail=f"title must be {consts.LEN_RFC_TITLE} characters or less"
        )
    return title


def validate_rfc_slug(slug: str) -> str:
    if len(slug) > consts.LEN_RFC_SLUG:
        raise HTTPException(
            status_code=422,
            detail=f"slug must be {consts.LEN_RFC_SLUG} characters or less"
        )
    return slug


def validate_rfc_status(status: str) -> Literal["draft", "open"]:
    if status == "draft":
        return "draft"
    elif status == "open":
        return "open"
    else:
        raise HTTPException(
            status_code=400,
            detail="status must be either 'draft' or 'open'"
        )


def validate_rfc_summary(summary: str) -> str:
    if len(summary) > consts.LEN_RFC_SUMMARY:
        raise HTTPException(
            status_code=422,
            detail=f"summary must be {consts.LEN_RFC_SUMMARY} characters or less"
        )
    return summary


def validate_rfc_content(content: str) -> str:
    if len(content) > consts.LEN_RFC_CONTENT:
        raise HTTPException(
            status_code=422,
            detail=f"content must be {consts.LEN_RFC_CONTENT} characters or less"
        )
    return content


class PostRfcRequest(BaseModel):
    """
    HTTP request object for `POST /rfc`.
    """
    title: Annotated[str, AfterValidator(validate_rfc_title)]
    slug: Annotated[str, AfterValidator(validate_rfc_slug)]
    status: Annotated[Literal["draft", "open"], AfterValidator(validate_rfc_status)]
    summary: Annotated[str, AfterValidator(validate_rfc_summary)]
    content: Annotated[str, AfterValidator(validate_rfc_content)]


class PatchRfcRequest(BaseModel):
    """
    HTTP request object for `PATCH /rfc`.
    """
    title: Annotated[str, AfterValidator(validate_rfc_title)] | None = None
    slug: Annotated[str, AfterValidator(validate_rfc_slug)] | None = None
    status: Annotated[Literal["draft", "open"], AfterValidator(validate_rfc_status)] | None = None
    summary: Annotated[str, AfterValidator(validate_rfc_summary)] | None = None
    content: Annotated[str, AfterValidator(validate_rfc_content)] | None = None


def validate_comment_content(content: str) -> str:
    if len(content) > consts.LEN_COMMENT_CONTENT:
        raise HTTPException(
            status_code=422,
            detail=f"content must be {consts.LEN_COMMENT_CONTENT} or less"
        )
    return content


class PostRfcCommentRequest(BaseModel):
    """
    HTTP request object for `POST /rfc/comment`.
    """
    rfc_id: int
    parent_comment_id: int | None
    content: Annotated[str, AfterValidator(validate_comment_content)]
    
