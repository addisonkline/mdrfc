import re
from typing import Annotated, Literal

from fastapi import HTTPException, Request
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    ValidationError,
    field_validator,
)

from mdrfc.backend.comment import validate_comment_content
import mdrfc.backend.constants as consts
from mdrfc.backend.document import (
    RFCRevisionRequest,
    validate_agent_contributors,
    validate_patch_readme_content,
    validate_patch_readme_reason,
    validate_quarantine_rfc_reason,
    validate_revision_message,
    validate_rfc_content,
    validate_rfc_slug,
    validate_rfc_status,
    validate_rfc_summary,
    validate_rfc_title,
)
from mdrfc.backend.users import (
    validate_email,
    validate_name_first,
    validate_name_last,
    validate_password,
    validate_username,
)


#
# AUTH endpoints
#
class PostSignupRequest(BaseModel):
    """
    HTTP request object for `POST /signup`.
    """

    username: Annotated[str, AfterValidator(validate_username)]
    email: Annotated[str, AfterValidator(validate_email)]
    name_last: Annotated[str, AfterValidator(validate_name_last)]
    name_first: Annotated[str, AfterValidator(validate_name_first)]
    password: Annotated[str, AfterValidator(validate_password)]


async def validate_post_signup_request(request: Request) -> PostSignupRequest:
    try:
        request_json = await request.json()
        return PostSignupRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"request validation failed: {e}")


def validate_verification_token(token: SecretStr) -> SecretStr:
    value = token.get_secret_value()
    if len(value) < 32:
        raise HTTPException(status_code=422, detail="verification token is invalid")
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


#
# RFC endpoints
#
class PatchRfcsReadmeRequest(BaseModel):
    """
    HTTP request object for `PATCH /rfcs/README`.
    """

    reason: Annotated[str, AfterValidator(validate_patch_readme_reason)]
    content: Annotated[str, AfterValidator(validate_patch_readme_content)] | None = None
    public: bool | None = None


async def validate_patch_rfcs_readme_request(request: Request) -> PatchRfcsReadmeRequest:
    try:
        request_json = await request.json()
        return PatchRfcsReadmeRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"request validation failed: {e}")


class PostRfcsReadmeRevRequest(BaseModel):
    """
    HTTP request object for `POST /rfcs/README/revs`.
    """

    reason: Annotated[str, AfterValidator(validate_patch_readme_reason)]
    content: Annotated[str, AfterValidator(validate_patch_readme_content)] | None = None
    public: bool | None = None


async def validate_post_rfcs_readme_rev_request(
    request: Request,
) -> PostRfcsReadmeRevRequest:
    try:
        request_json = await request.json()
        return PostRfcsReadmeRevRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"request validation failed: {e}")


class PostRfcRequest(BaseModel):
    """
    HTTP request object for `POST /rfcs`.
    """

    title: Annotated[str, AfterValidator(validate_rfc_title)]
    slug: Annotated[str, AfterValidator(validate_rfc_slug)]
    status: Annotated[Literal["draft", "open"], AfterValidator(validate_rfc_status)]
    summary: Annotated[str, AfterValidator(validate_rfc_summary)]
    content: Annotated[str, AfterValidator(validate_rfc_content)]
    agent_contributors: Annotated[
        list[str], AfterValidator(validate_agent_contributors)
    ]
    public: bool = False


async def validate_post_rfc_request(request: Request) -> PostRfcRequest:
    try:
        request_json = await request.json()
        return PostRfcRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"request validation failed: {e}")


class DeleteRfcRequest(BaseModel):
    """
    HTTP request object for `DELETE /rfcs/{rfc_id}`.
    """

    reason: Annotated[str, AfterValidator(validate_quarantine_rfc_reason)]


async def validate_delete_rfc_request(request: Request) -> DeleteRfcRequest:
    try:
        request_json = await request.json()
        return DeleteRfcRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"request validation failed: {e}")


#
# REVISION endpoints
#
class PostRfcRevisionRequest(BaseModel):
    """
    HTTP request object for `POST /rfcs/{rfc_id}/revs`.
    """

    update: RFCRevisionRequest
    message: Annotated[str, AfterValidator(validate_revision_message)]


async def validate_post_rfc_revision_request(
    request: Request,
) -> PostRfcRevisionRequest:
    try:
        request_json = await request.json()
        return PostRfcRevisionRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"request validation failed: {e}")


#
# COMMENT endpoints
#
class PostRfcCommentRequest(BaseModel):
    """
    HTTP request object for `POST /rfcs/{rfc_id}/comments`.
    """

    parent_comment_id: int | None
    content: Annotated[str, AfterValidator(validate_comment_content)]


async def validate_post_rfc_comment_request(request: Request) -> PostRfcCommentRequest:
    try:
        request_json = await request.json()
        return PostRfcCommentRequest.model_validate(request_json)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"request validation failed: {e}")
