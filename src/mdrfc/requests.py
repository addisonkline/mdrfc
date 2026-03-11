import re
from typing import Annotated, Literal

from fastapi import HTTPException, Request
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, SecretStr, ValidationError, field_validator

from mdrfc.backend.comment import validate_comment_content
import mdrfc.backend.constants as consts
from mdrfc.backend.document import (
    validate_agent_contributors,
    validate_rfc_content,
    validate_rfc_slug,
    validate_rfc_status,
    validate_rfc_summary,
    validate_rfc_title
)
from mdrfc.backend.users import (
    validate_email,
    validate_name_first,
    validate_name_last,
    validate_username
)


class PostSignupRequest(BaseModel):
    """
    HTTP request object for `POST /signup`.
    """
    username: Annotated[str, AfterValidator(validate_username)]
    email: Annotated[str, AfterValidator(validate_email)]
    name_last: Annotated[str, AfterValidator(validate_name_last)]
    name_first: Annotated[str, AfterValidator(validate_name_first)]
    password: Annotated[SecretStr, AfterValidator(validate_password)]


async def validate_post_signup_request(request: Request) -> PostSignupRequest:
    try:
        request_json = await request.json()
        return PostSignupRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"request validation failed: {e}"
        )


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


class PostRfcRequest(BaseModel):
    """
    HTTP request object for `POST /rfc`.
    """
    title: Annotated[str, AfterValidator(validate_rfc_title)]
    slug: Annotated[str, AfterValidator(validate_rfc_slug)]
    status: Annotated[Literal["draft", "open"], AfterValidator(validate_rfc_status)]
    summary: Annotated[str, AfterValidator(validate_rfc_summary)]
    content: Annotated[str, AfterValidator(validate_rfc_content)]
    agent_contributors = Annotated[list[str], AfterValidator(validate_agent_contributors)]


async def validate_post_rfc_request(request: Request) -> PostRfcRequest:
    try:
        request_json = await request.json()
        return PostRfcRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"request validation failed: {e}"
        )


class PatchRfcRequest(BaseModel):
    """
    HTTP request object for `PATCH /rfc`.
    """
    title: Annotated[str, AfterValidator(validate_rfc_title)] | None = None
    slug: Annotated[str, AfterValidator(validate_rfc_slug)] | None = None
    status: Annotated[Literal["draft", "open"], AfterValidator(validate_rfc_status)] | None = None
    summary: Annotated[str, AfterValidator(validate_rfc_summary)] | None = None
    content: Annotated[str, AfterValidator(validate_rfc_content)] | None = None
    agent_contributors: Annotated[list[str], AfterValidator(validate_agent_contributors)] | None = None


async def validate_patch_rfc_request(request: Request) -> PatchRfcRequest:
    try:
        request_json = await request.json()
        return PatchRfcRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"request validation failed: {e}"
        )


class PostRfcCommentRequest(BaseModel):
    """
    HTTP request object for `POST /rfc/comment`.
    """
    rfc_id: int
    parent_comment_id: int | None
    content: Annotated[str, AfterValidator(validate_comment_content)]
    

async def validate_post_rfc_comment_request(request: Request) -> PostRfcCommentRequest:
    try:
        request_json = await request.json()
        return PostRfcCommentRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"request validation failed: {e}"
        )