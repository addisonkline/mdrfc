from typing import Annotated, Literal

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


def validate_name_last(name: str) -> str:
    if len(name) > consts.LEN_NAME_LAST:
        raise HTTPException(
            status_code=422,
            detail=f"last name must be {consts.LEN_NAME_LAST} characters or less"
        )
    return name


def validate_name_first(name: str) -> str:
    if len(name) > consts.LEN_NAME_FIRST:
        raise HTTPException(
            status_code=422,
            detail=f"first name must be {consts.LEN_NAME_FIRST} characters or less"
        )
    return name


class PostSignupRequest(BaseModel):
    """
    HTTP request object for `POST /signup`.
    """
    username: Annotated[str, AfterValidator(validate_username)]
    email: Annotated[str, AfterValidator(validate_email)]
    name_last: Annotated[str, AfterValidator(validate_name_last)]
    name_first: Annotated[str, AfterValidator(validate_name_first)]
    password: str


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
    