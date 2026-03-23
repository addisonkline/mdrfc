from argparse import Namespace
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import json
from os import getenv
from typing import Annotated
import logging
import time
from uuid import UUID

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn

from mdrfc.backend.auth import (
    DEBUG_RETURN_VERIFICATION_TOKEN,
    EmailVerificationResult,
    Token,
    User,
    authenticate_user,
    create_access_token,
    create_new_user,
    get_current_active_admin,
    get_current_active_user,
    get_current_active_user_if_one,
    verify_user_email,
)
from mdrfc.backend.comment import validate_quarantine_comment_reason
import mdrfc.backend.constants as consts
from mdrfc.backend.db import init_db, close_db
from mdrfc.backend.document import validate_quarantine_rfc_reason
from mdrfc.backend.email import check_valid_email, send_verification_email_task
from mdrfc.backend.rate_limit import SlidingWindowRateLimiter
from mdrfc.utils.llms_txt import LLMS_TXT
from mdrfc.utils.logging import init_logger
import mdrfc.api as api
import mdrfc.requests as req_types
import mdrfc.responses as res_types
from mdrfc.utils.version import get_mdrfc_version


logger = logging.getLogger(__name__)

load_dotenv()
token_expiry_time = getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if token_expiry_time is None:
    raise RuntimeError(
        "environment variable ACCESS_TOKEN_EXPIRE_MINUTES is required but was not found"
    )
ACCESS_TOKEN_EXPIRE_MINUTES = int(token_expiry_time)

_llms_txt = LLMS_TXT


async def _server_startup(app: FastAPI):
    """
    Server startup handler.
    """
    logger.info("server starting up...")

    await init_db()

    app.state.time_start = time.time()

    logger.info("server startup complete")


async def _server_shutdown(app: FastAPI):
    """
    Server shutdown handler.
    """
    logger.info("server shutting down...")

    await close_db()

    logger.info("server shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler for the FastAPI app.
    """
    await _server_startup(app)

    yield

    await _server_shutdown(app)


app = FastAPI(
    title="MDRFC",
    summary="Markdown-formatted RFC server",
    description="A server for hosting Markdown RFCs",
    version=get_mdrfc_version(),
    lifespan=lifespan
)
signup_rate_limiter = SlidingWindowRateLimiter()

DEPRECATED_ROUTE_REPLACEMENTS = {
    "/rfc": "/rfcs",
    "/rfc/{rfc_id}/rev/current": "/rfcs/{rfc_id}",
    "/rfc/{rfc_id}": "/rfcs/{rfc_id}",
    "/rfc/{rfc_id}/revs": "/rfcs/{rfc_id}/revs",
    "/rfc/{rfc_id}/rev/{rev_id}": "/rfcs/{rfc_id}/revs/{rev_id}",
    "/rfc/{rfc_id}/rev": "/rfcs/{rfc_id}/revs",
    "/rfc/{rfc_id}/comment": "/rfcs/{rfc_id}/comments",
    "/rfc/{rfc_id}/comments": "/rfcs/{rfc_id}/comments",
    "/rfc/{rfc_id}/comments/quarantined": "/rfcs/{rfc_id}/comments/quarantined",
    "/rfc/{rfc_id}/comments/quarantined/{quarantine_id}": "/rfcs/{rfc_id}/comments/quarantined/{quarantine_id}",
    "/rfc/{rfc_id}/comment/{comment_id}": "/rfcs/{rfc_id}/comments/{comment_id}",
}


def _format_route_path(path_template: str, path_params: dict[str, object]) -> str:
    path = path_template
    for key, value in path_params.items():
        path = path.replace(f"{{{key}}}", str(value))
    return path


def _add_deprecation_headers(request: Request, response: Response) -> None:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    if route_path is None:
        return

    replacement_template = DEPRECATED_ROUTE_REPLACEMENTS.get(route_path)
    if replacement_template is None:
        return

    replacement_path = _format_route_path(replacement_template, request.path_params)
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = f'<{replacement_path}>; rel="alternate"'
    logger.warning(
        "deprecated endpoint requested: %s %s -> %s",
        request.method,
        request.url.path,
        replacement_path,
    )


@app.get(
    "/", 
    response_model=res_types.GetRootResponse,
    tags=["basic"]
)
async def get_root() -> res_types.GetRootResponse:
    """
    `GET /`: Obtain basic server information and metadata.
    """
    return await api.get_root(app.state.time_start)


@app.get(
    "/llms.txt",
    tags=["basic"]
)
async def get_llms_txt() -> res_types.GetLlmsTxtResponse:
    """
    `GET /llms.txt`: Obtain server information in an LLM-friendly format.
    """
    global _llms_txt
    return await api.get_llms_txt(
        llms_txt=_llms_txt,
    )


#
# AUTH endpoints
#
@app.post(
    "/login", 
    response_model=Token,
    tags=["auth"]
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    `POST /login`: Log in using OAuth2 and obtain an access token.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # type: ignore
    access_token = create_access_token(
        data={"sub": user.username},  # type: ignore
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post(
    "/signup", 
    response_model=res_types.PostSignupResponse,
    tags=["auth"]
)
async def post_new_user(
    background_tasks: BackgroundTasks,
    http_request: Request,
    payload: Annotated[
        req_types.PostSignupRequest, Depends(req_types.validate_post_signup_request)
    ],
) -> res_types.PostSignupResponse:
    """
    `POST /signup`: Attempt to create a new user with the provided credentials.
    """
    check_valid_email(payload.email)

    client_host = "unknown"
    if http_request.client is not None and http_request.client.host:
        client_host = http_request.client.host

    ip_retry_after = await signup_rate_limiter.check_and_record(
        ("ip", client_host),
        limit=consts.SIGNUP_RATE_LIMIT_MAX_ATTEMPTS_PER_IP,
        window_seconds=consts.SIGNUP_RATE_LIMIT_WINDOW_SECONDS,
    )
    if ip_retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="too many signup attempts",
            headers={"Retry-After": str(ip_retry_after)},
        )

    identity_retry_after = await signup_rate_limiter.check_and_record(
        ("identity", payload.username, payload.email),
        limit=consts.SIGNUP_RATE_LIMIT_MAX_ATTEMPTS_PER_IDENTITY,
        window_seconds=consts.SIGNUP_RATE_LIMIT_WINDOW_SECONDS,
    )
    if identity_retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="too many signup attempts",
            headers={"Retry-After": str(identity_retry_after)},
        )

    signup_result = await create_new_user(
        username=payload.username,
        email=payload.email,
        name_last=payload.name_last,
        name_first=payload.name_first,
        password=payload.password,
    )

    if not DEBUG_RETURN_VERIFICATION_TOKEN:
        logger.info("sending email...")
        background_tasks.add_task(
            send_verification_email_task,
            to_email=payload.email,
            username=payload.username,
            verification_token=signup_result.verification_token,
            expires_at=signup_result.verification_expires_at,
        )

    return res_types.PostSignupResponse(
        username=payload.username,
        email=payload.email,
        created_at=signup_result.created_at,
        metadata={
            "verification_required": True,
            "verification_expires_at": signup_result.verification_expires_at.isoformat(),
            "verification_token": signup_result.verification_token
            if DEBUG_RETURN_VERIFICATION_TOKEN
            else None,
        },
    )


@app.post(
    "/verify-email", 
    response_model=res_types.PostVerifyEmailResponse,
    tags=["auth"]
)
async def post_verify_email(
    payload: req_types.PostVerifyEmailRequest,
) -> res_types.PostVerifyEmailResponse:
    """
    `POST /verify-email`: Verify a pending account email address.
    """
    verification_result: EmailVerificationResult = await verify_user_email(
        payload.token.get_secret_value()
    )

    return res_types.PostVerifyEmailResponse(
        username=verification_result.username,
        email=verification_result.email,
        verified_at=verification_result.verified_at,
        metadata={},
    )


@app.get(
    "/users/me",
    response_model=User,
    tags=["auth", "users"]
)
async def get_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    `GET /users/me`: Get information on the current user.
    """
    return current_user


#
# RFC endpoints
#
@app.get(
    "/rfcs/README",
    tags=["basic", "rfcs"]
)
async def get_rfcs_readme(
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)]
) -> res_types.GetRfcsReadmeResponse:
    """
    `GET /rfcs/README`: Get the README document for this server.
    """
    return await api.get_rfcs_readme(
        user=current_user,
    )


@app.get(
    "/rfcs/README/revs",
    response_model=res_types.GetRfcsReadmeRevsResponse,
    tags=["rfcs", "rev"]
)
async def get_rfcs_readme_revs(
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcsReadmeRevsResponse:
    """
    `GET /rfcs/README/revs`: Get all revisions on the RFC README file.
    """
    return await api.get_rfcs_readme_revs(user=current_user)


@app.get(
    "/rfcs/README/revs/{revision_id}",
    response_model=res_types.GetRfcsReadmeRevResponse,
    tags=["rfcs", "rev"]
)
async def get_rfcs_readme_rev(
    revision_id: UUID,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcsReadmeRevResponse:
    """
    `GET /rfcs/README/revs/{revision_id}`: Get a specific revision on the RFC README file.
    """
    return await api.get_rfcs_readme_rev(
        user=current_user,
        revision_id=revision_id,
    )


@app.post(
    "/rfcs/README/revs",
    response_model=res_types.PostRfcsReadmeRevResponse,
    tags=["rfcs", "rev", "admin"]
)
async def post_rfcs_readme_rev(
    current_admin: Annotated[User, Depends(get_current_active_admin)],
    payload: Annotated[req_types.PostRfcsReadmeRevRequest, Depends(req_types.validate_post_rfcs_readme_rev_request)],
) -> res_types.PostRfcsReadmeRevResponse:
    """
    `POST /rfcs/README/revs`: Post a new revision on the RFC README file.
    """
    return await api.post_rfcs_readme_rev(
        admin=current_admin,
        payload=payload,
    )


@app.get(
    "/rfcs",
    response_model=res_types.GetRfcsResponse,
    tags=["rfcs"]
)
async def get_rfcs(
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcsResponse:
    """
    `GET /rfcs`: Obtain a list of all current RFCs.
    """
    return await api.get_rfcs(
        current_user=current_user,
    )


@app.get(
    "/rfcs/quarantined",
    response_model=res_types.GetQuarantinedRfcsResponse,
    tags=["rfcs", "admin"]
)
async def get_rfcs_quarantined(
    current_admin: Annotated[User, Depends(get_current_active_admin)],
) -> res_types.GetQuarantinedRfcsResponse:
    """
    `GET /rfcs/quarantined`: Obtain the list of currently-quarantined RFCs.
    """
    return await api.get_rfcs_quarantined()


@app.delete(
    "/rfcs/quarantined/{quarantine_id}",
    response_model=res_types.DeleteQuarantinedRfcResponse,
    tags=["rfcs", "admin"]
)
async def delete_rfc(
    quarantine_id: int,
    current_admin: Annotated[User, Depends(get_current_active_admin)],
) -> res_types.DeleteQuarantinedRfcResponse:
    """
    `DELETE /rfcs/quarantined/{quarantine_id}`: Fully delete a quarantined RFC.
    """
    return await api.delete_rfc_quarantined(quarantine_id=quarantine_id)


@app.post(
    "/rfcs/quarantined/{quarantine_id}",
    response_model=res_types.PostQuarantinedRfcResponse,
    tags=["rfcs", "admin"]
)
async def unquarantine_rfc(
    quarantine_id: int,
    current_admin: Annotated[User, Depends(get_current_active_admin)],
) -> res_types.PostQuarantinedRfcResponse:
    """
    `POST /rfcs/quarantined/{quarantine_id}`: Republish a quarantined RFC.
    """
    return await api.post_rfc_quarantined(quarantine_id=quarantine_id)


@app.post("/rfc", response_model=res_types.PostRfcResponse, deprecated=True)
@app.post(
    "/rfcs",
    response_model=res_types.PostRfcResponse,
    tags=["rfcs", "user"]
)
async def post_rfc(
    http_request: Request,
    response: Response,
    request: Annotated[
        req_types.PostRfcRequest, Depends(req_types.validate_post_rfc_request)
    ],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> res_types.PostRfcResponse:
    """
    `POST /rfcs`: Upload a new RFC document.
    """
    _add_deprecation_headers(http_request, response)
    return await api.post_rfc(
        user=current_user,
        request=request,
    )


@app.get(
    "/rfc/{rfc_id}/rev/current",
    response_model=res_types.GetRfcResponse,
    deprecated=True,
)
@app.get("/rfc/{rfc_id}", response_model=res_types.GetRfcResponse, deprecated=True)
@app.get(
    "/rfcs/{rfc_id}",
    response_model=res_types.GetRfcResponse,
    tags=["rfcs"]
)
async def get_rfc_by_id(
    http_request: Request,
    response: Response,
    rfc_id: int,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcResponse:
    """
    `GET /rfcs/{rfc_id}`: Get the existing RFC document by ID.
    """
    _add_deprecation_headers(http_request, response)
    return await api.get_rfc(
        rfc_id=rfc_id,
        current_user=current_user,
    )


@app.delete(
    "/rfc/{rfc_id}", response_model=res_types.DeleteRfcResponse, deprecated=True
)
@app.delete(
    "/rfcs/{rfc_id}",
    response_model=res_types.DeleteRfcResponse,
    tags=["rfcs", "user"]
)
async def quarantine_rfc(
    http_request: Request,
    response: Response,
    rfc_id: int,
    reason: Annotated[str, Depends(validate_quarantine_rfc_reason)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> res_types.DeleteRfcResponse:
    """
    `DELETE /rfcs/{rfc_id}`: Delete an existing RFC (soft delete; add to quarantine).
    """
    _add_deprecation_headers(http_request, response)
    return await api.delete_rfc(
        rfc_id=rfc_id,
        reason=reason,
        user=current_user,
    )


@app.post(
    "/rfcs/{rfc_id}/review",
    response_model=res_types.PostRfcReviewResponse,
    tags=["rfcs", "user"]
)
async def post_rfc_review_req(
    rfc_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> res_types.PostRfcReviewResponse:
    """
    `POST /rfcs/{rfc_id}/review`: Request admin review on a specific RFC.
    """
    return await api.post_rfc_review_req(
        rfc_id=rfc_id,
        user=current_user,
    )


@app.patch(
    "/rfcs/{rfc_id}/status",
    response_model=res_types.PatchRfcStatusResponse,
    tags=["rfcs", "admin"]
)
async def patch_rfc_status(
    rfc_id: int,
    current_admin: Annotated[User, Depends(get_current_active_admin)],
    payload: Annotated[req_types.PatchRfcStatusRequest, Depends(req_types.validate_patch_rfc_status_request)]
) -> res_types.PatchRfcStatusResponse:
    """
    `PATCH /rfcs/{rfc_id}/status`: Update an RFC's status to `accepted` or `rejected` following admin review.
    """
    return await api.patch_rfc_status(
        rfc_id=rfc_id,
        admin=current_admin,
        payload=payload
    )


#
# REVISION endpoints
#
@app.get(
    "/rfc/{rfc_id}/revs",
    response_model=res_types.GetRfcRevisionsResponse,
    deprecated=True,
)
@app.get(
    "/rfcs/{rfc_id}/revs",
    response_model=res_types.GetRfcRevisionsResponse,
    tags=["rfcs", "revs"]
)
async def get_rfc_revisions(
    http_request: Request,
    response: Response,
    rfc_id: int,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcRevisionsResponse:
    """
    `GET /rfcs/{rfc_id}/revs`: Get all revisions for the given RFC.
    """
    _add_deprecation_headers(http_request, response)
    return await api.get_rfc_revisions(rfc_id=rfc_id, current_user=current_user)


@app.get(
    "/rfc/{rfc_id}/rev/{rev_id}",
    response_model=res_types.GetRfcRevisionResponse,
    deprecated=True,
)
@app.get(
    "/rfcs/{rfc_id}/revs/{rev_id}",
    response_model=res_types.GetRfcRevisionResponse,
    tags=["rfcs", "revs"]
)
async def get_rfc_revision(
    http_request: Request,
    response: Response,
    rfc_id: int,
    rev_id: str,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcRevisionResponse:
    """
    `GET /rfcs/{rfc_id}/revs/{rev_id}`: Get a specific revision by ID for the given RFC.
    """
    _add_deprecation_headers(http_request, response)
    return await api.get_rfc_revision(
        rfc_id=rfc_id, revision_id=rev_id, current_user=current_user
    )


@app.post(
    "/rfc/{rfc_id}/rev",
    response_model=res_types.PostRfcRevisionResponse,
    deprecated=True,
)
@app.post(
    "/rfcs/{rfc_id}/revs",
    response_model=res_types.PostRfcRevisionResponse,
    tags=["rfcs", "revs"]
)
async def post_rfc_revision(
    http_request: Request,
    response: Response,
    rfc_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Annotated[
        req_types.PostRfcRevisionRequest,
        Depends(req_types.validate_post_rfc_revision_request),
    ],
) -> res_types.PostRfcRevisionResponse:
    """
    `POST /rfcs/{rfc_id}/revs`: Update an existing RFC with a new revision.
    """
    _add_deprecation_headers(http_request, response)
    return await api.post_rfc_revision(
        rfc_id=rfc_id, user=current_user, request=request
    )


#
# COMMENT endpoints
#
@app.post(
    "/rfc/{rfc_id}/comment",
    response_model=res_types.PostRfcCommentResponse,
    deprecated=True,
)
@app.post(
    "/rfcs/{rfc_id}/comments",
    response_model=res_types.PostRfcCommentResponse,
    tags=["rfcs", "comments", "user"]
)
async def post_rfc_comment(
    http_request: Request,
    response: Response,
    rfc_id: int,
    request: Annotated[
        req_types.PostRfcCommentRequest,
        Depends(req_types.validate_post_rfc_comment_request),
    ],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> res_types.PostRfcCommentResponse:
    """
    `POST /rfcs/{rfc_id}/comments`: Post a new comment on an existing RFC.
    """
    _add_deprecation_headers(http_request, response)
    return await api.post_rfc_comment(rfc_id=rfc_id, user=current_user, request=request)


@app.get(
    "/rfc/{rfc_id}/comments",
    response_model=res_types.GetRfcCommentsResponse,
    deprecated=True,
)
@app.get(
    "/rfcs/{rfc_id}/comments",
    response_model=res_types.GetRfcCommentsResponse,
    tags=["rfcs", "comments"]
)
async def get_rfc_comments(
    http_request: Request,
    response: Response,
    rfc_id: int,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcCommentsResponse:
    """
    `GET /rfcs/{rfc_id}/comments`: Get all comments on an existing RFC.
    """
    _add_deprecation_headers(http_request, response)
    return await api.get_rfc_comments(rfc_id=rfc_id, current_user=current_user)


@app.get(
    "/rfc/{rfc_id}/comments/quarantined",
    response_model=res_types.GetQuarantinedCommentsResponse,
    deprecated=True,
)
@app.get(
    "/rfcs/{rfc_id}/comments/quarantined",
    response_model=res_types.GetQuarantinedCommentsResponse,
    tags=["rfcs", "comments", "admin"]
)
async def get_quarantined_comments(
    http_request: Request,
    response: Response,
    rfc_id: int,
    current_admin: Annotated[User, Depends(get_current_active_admin)],
) -> res_types.GetQuarantinedCommentsResponse:
    """
    `GET /rfcs/{rfc_id}/comments/quarantined`: Get a list of all quarantined comments on a given RFC.
    """
    _add_deprecation_headers(http_request, response)
    return await api.get_rfc_comments_quarantined(rfc_id=rfc_id)


@app.delete(
    "/rfc/{rfc_id}/comments/quarantined/{quarantine_id}",
    response_model=res_types.DeleteQuarantinedCommentResponse,
    deprecated=True,
)
@app.delete(
    "/rfcs/{rfc_id}/comments/quarantined/{quarantine_id}",
    response_model=res_types.DeleteQuarantinedCommentResponse,
    tags=["rfcs", "comments", "admin"]
)
async def delete_comment(
    http_request: Request,
    response: Response,
    rfc_id: int,
    quarantine_id: int,
    current_admin: Annotated[User, Depends(get_current_active_admin)],
) -> res_types.DeleteQuarantinedCommentResponse:
    """
    `DELETE /rfcs/{rfc_id}/comments/quarantined/{quarantine_id}`: Fully delete a quarantined comment.
    """
    _add_deprecation_headers(http_request, response)
    return await api.delete_rfc_comment_quarantined(
        rfc_id=rfc_id, quarantine_id=quarantine_id
    )


@app.post(
    "/rfc/{rfc_id}/comments/quarantined/{quarantine_id}",
    response_model=res_types.PostQuarantinedCommentResponse,
    deprecated=True,
)
@app.post(
    "/rfcs/{rfc_id}/comments/quarantined/{quarantine_id}",
    response_model=res_types.PostQuarantinedCommentResponse,
    tags=["rfcs", "comments", "admin"]
)
async def unquarantine_comment(
    http_request: Request,
    response: Response,
    rfc_id: int,
    quarantine_id: int,
    current_admin: Annotated[User, Depends(get_current_active_admin)],
) -> res_types.PostQuarantinedCommentResponse:
    """
    `POST /rfcs/{rfc_id}/comments/quarantined/{quarantine_id}`: Unquarantine and reupload a comment.
    """
    _add_deprecation_headers(http_request, response)
    return await api.post_rfc_comment_quarantined(
        rfc_id=rfc_id,
        quarantine_id=quarantine_id,
    )


@app.get(
    "/rfc/{rfc_id}/comment/{comment_id}",
    response_model=res_types.GetRfcCommentResponse,
    deprecated=True,
)
@app.get(
    "/rfcs/{rfc_id}/comments/{comment_id}",
    response_model=res_types.GetRfcCommentResponse,
    tags=["rfcs", "comments"]
)
async def get_rfc_comment(
    http_request: Request,
    response: Response,
    rfc_id: int,
    comment_id: int,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcCommentResponse:
    """
    `GET /rfcs/{rfc_id}/comments/{comment_id}`: Get a specific comment on a specific RFC.
    """
    _add_deprecation_headers(http_request, response)
    return await api.get_rfc_comment(
        rfc_id=rfc_id, comment_id=comment_id, current_user=current_user
    )


@app.delete(
    "/rfc/{rfc_id}/comment/{comment_id}",
    response_model=res_types.DeleteRfcCommentResponse,
    deprecated=True,
)
@app.delete(
    "/rfcs/{rfc_id}/comments/{comment_id}",
    response_model=res_types.DeleteRfcCommentResponse,
    tags=["rfcs", "comments", "user"]
)
async def quarantine_comment(
    http_request: Request,
    response: Response,
    rfc_id: int,
    comment_id: int,
    reason: Annotated[str, Depends(validate_quarantine_comment_reason)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> res_types.DeleteRfcCommentResponse:
    """
    `DELETE /rfcs/{rfc_id}/comments/{comment_id}`: Quarantine (soft-delete) an existing comment.
    """
    _add_deprecation_headers(http_request, response)
    return await api.delete_rfc_comment(
        rfc_id=rfc_id,
        comment_id=comment_id,
        reason=reason,
        user=current_user,
    )


def _load_llms_txt(file: str) -> None:
    """
    Load a new `llms.txt` from the given file.
    """
    with open(file) as llms_txt_file:
        global _llms_txt
        _llms_txt = llms_txt_file.read()


def run_server(args: Namespace) -> None:
    """
    Run the mdrfc server via the CLI.
    """
    init_logger(args.log_file, args.log_level_file, args.log_level_console)

    if args.llms_txt:
        _load_llms_txt(args.llms_txt)

    uvicorn.run(
        "mdrfc.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_config=None,
    )
