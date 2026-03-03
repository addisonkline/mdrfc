from typing import Annotated

from fastapi import HTTPException
from pydantic import AfterValidator, BaseModel

import mdrfc.backend.constants as consts


def validate_username(username: str) -> str:
    if len(username) > consts.LEN_USERNAME:
        raise HTTPException(
            status_code=422,
            detail=f"username must be {consts.LEN_USERNAME} characters or less"
        )
    return username


def validate_email(email: str) -> str:
    if len(email) > consts.LEN_EMAIL:
        raise HTTPException(
            status_code=422,
            detail=f"email must be {consts.LEN_EMAIL} characters or less"
        )
    return email


class PostSignupRequest(BaseModel):
    """
    HTTP request object for `POST /signup`.
    """
    username: Annotated[str, AfterValidator(validate_username)]
    email: Annotated[str, AfterValidator(validate_email)]
    password: str


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
    summary: Annotated[str, AfterValidator(validate_rfc_summary)]
    content: Annotated[str, AfterValidator(validate_rfc_content)]


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