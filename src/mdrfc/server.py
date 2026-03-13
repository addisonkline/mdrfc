from argparse import Namespace
from contextlib import asynccontextmanager
from datetime import timedelta
from os import getenv
from typing import Annotated
import logging
import time

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Depends, HTTPException, Request
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
    get_current_active_user,
    get_current_active_user_if_one,
    verify_user_email,
)
from mdrfc.backend.comment import RFCComment
import mdrfc.backend.constants as consts
from mdrfc.backend.db import (
    init_db,
    close_db
)
from mdrfc.backend.document import RFCDocument
from mdrfc.backend.email import send_verification_email_task
from mdrfc.backend.rate_limit import SlidingWindowRateLimiter
from mdrfc.utils.logging import init_logger
import mdrfc.api as api
import mdrfc.requests as req_types
import mdrfc.responses as res_types


logger = logging.getLogger(__name__)

load_dotenv()
token_expiry_time = getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if token_expiry_time is None:
    raise RuntimeError("environment variable ACCESS_TOKEN_EXPIRE_MINUTES is required but was not found")
ACCESS_TOKEN_EXPIRE_MINUTES = int(token_expiry_time)


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


app = FastAPI(lifespan=lifespan)
signup_rate_limiter = SlidingWindowRateLimiter()


@app.get("/", response_model=res_types.GetRootResponse)
async def get_root() -> res_types.GetRootResponse:
    """
    `GET /`: Obtain basic server information and metadata.
    """
    return api.get_root(app.state.time_start)


#
# AUTH endpoints
#
@app.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
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
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # type: ignore
    access_token = create_access_token(
        data={"sub": user.username}, # type: ignore
        expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@app.post("/signup", response_model=res_types.PostSignupResponse)
async def post_new_user(
    background_tasks: BackgroundTasks,
    http_request: Request,
    payload: Annotated[req_types.PostSignupRequest, Depends(req_types.validate_post_signup_request)],
) -> res_types.PostSignupResponse:
    """
    `POST /signup`: Attempt to create a new user with the provided credentials.
    """
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
        password=payload.password
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
            "verification_token": signup_result.verification_token if DEBUG_RETURN_VERIFICATION_TOKEN else None,
        }
    )


@app.post("/verify-email", response_model=res_types.PostVerifyEmailResponse)
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



@app.get("/users/me", response_model=User)
async def get_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    `GET /users/me`: Get information on the current user.
    """
    return current_user


#
# RFC endpoints
#
@app.get("/rfcs", response_model=res_types.GetRfcsResponse)
async def get_rfcs(
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)]
) -> res_types.GetRfcsResponse:
    """
    `GET /rfcs`: Obtain a list of all current RFCs.
    """
    return await api.get_rfcs(
        current_user=current_user,
    )


@app.post("/rfc", response_model=res_types.PostRfcResponse)
async def post_rfc(
    request: Annotated[req_types.PostRfcRequest, Depends(req_types.validate_post_rfc_request)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> res_types.PostRfcResponse:
    """
    `POST /rfc`: Upload a new RFC document.
    """
    return await api.post_rfc(
        user=current_user,
        request=request,
    )


@app.get("/rfc/{rfc_id}/rev/current", response_model=res_types.GetRfcResponse)
@app.get("/rfc/{rfc_id}", response_model=res_types.GetRfcResponse)
async def get_rfc_by_id(
    rfc_id: int,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)]
) -> res_types.GetRfcResponse:
    """
    `GET /rfc/{rfc_id}`: Get the existing RFC document by ID.
    """
    return await api.get_rfc(
        rfc_id=rfc_id,
        current_user=current_user,
    )


#
# REVISION endpoints
#
@app.get("/rfc/{rfc_id}/revs", response_model=res_types.GetRfcRevisionsResponse)
async def get_rfc_revisions(
    rfc_id: int,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcRevisionsResponse:
    """
    `GET /rfc/{rfc_id}/revs`: Get all revisions for the given RFC.
    """
    return await api.get_rfc_revisions(
        rfc_id=rfc_id,
        current_user=current_user
    )


@app.get("/rfc/{rfc_id}/rev/{rev_id}", response_model=res_types.GetRfcRevisionResponse)
async def get_rfc_revision(
    rfc_id: int,
    rev_id: str,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)],
) -> res_types.GetRfcRevisionResponse:
    """
    `GET /rfc/{rfc_id}/rev/{rev_id}`: Get a specific revision by ID for the given RFC.
    """
    return await api.get_rfc_revision(
        rfc_id=rfc_id,
        revision_id=rev_id,
        current_user=current_user
    )


@app.post("/rfc/{rfc_id}/rev", response_model=res_types.PostRfcRevisionResponse)
async def post_rfc_revision(
    rfc_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Annotated[req_types.PostRfcRevisionRequest, Depends(req_types.validate_post_rfc_revision_request)]
) -> res_types.PostRfcRevisionResponse:
    """
    `POST /rfc/{rfc_id}/rev`: Update an existing RFC with a new revision.
    """
    return await api.post_rfc_revision(
        rfc_id=rfc_id,
        user=current_user,
        request=request
    )


#
# COMMENT endpoints
#
@app.post("/rfc/{rfc_id}/comment", response_model=res_types.PostRfcCommentResponse)
async def post_rfc_comment(
    rfc_id: int,
    request: Annotated[req_types.PostRfcCommentRequest, Depends(req_types.validate_post_rfc_comment_request)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> res_types.PostRfcCommentResponse:
    """
    `POST /rfc/comment`: Post a new comment on an existing RFC.
    """
    return await api.post_rfc_comment(
        rfc_id=rfc_id,
        user=current_user,
        request=request
    )


@app.get("/rfc/{rfc_id}/comments", response_model=res_types.GetRfcCommentsResponse)
async def get_rfc_comments(
    rfc_id: int,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)]
) -> res_types.GetRfcCommentsResponse:
    """
    `GET /rfc/{rfc_id}/comments`: Get all comments on an existing RFC.
    """
    return await api.get_rfc_comments(
        rfc_id=rfc_id,
        current_user=current_user
    )


@app.get("/rfc/{rfc_id}/comment/{comment_id}", response_model=res_types.GetRfcCommentResponse)
async def get_rfc_comment(
    rfc_id: int,
    comment_id: int,
    current_user: Annotated[User | None, Depends(get_current_active_user_if_one)]
) -> res_types.GetRfcCommentResponse:
    """
    `GET /rfc/{rfc_id}/comment/{comment_id}`: Get a specific comment on a specific RFC.
    """
    return await api.get_rfc_comment(
        rfc_id=rfc_id,
        comment_id=comment_id,
        current_user=current_user
    )


def run_server(
    args: Namespace
) -> None:
    """
    Run the mdrfc server via the CLI.
    """
    init_logger(
        args.log_file,
        args.log_level_file,
        args.log_level_console
    )

    uvicorn.run(
        "mdrfc.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_config=None
    )
