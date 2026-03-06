from argparse import Namespace
from contextlib import asynccontextmanager
from datetime import timedelta
from os import getenv
from typing import Annotated
import logging
import time

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn

from mdrfc.backend.auth import (
    Token,
    User,
    authenticate_user,
    create_access_token,
    create_new_user,
    get_current_active_user
)
from mdrfc.backend.comment import RFCComment
from mdrfc.backend.db import (
    init_db,
    close_db
)
from mdrfc.backend.document import RFCDocument
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
    request: req_types.PostSignupRequest,
) -> res_types.PostSignupResponse:
    """
    `POST /signup`: Attempt to create a new user with the provided credentials.
    """
    timestamp = await create_new_user(
        username=request.username,
        email=request.email,
        name_last=request.name_last,
        name_first=request.name_first,
        password=request.password
    )

    return res_types.PostSignupResponse(
        username=request.username,
        email=request.email,
        created_at=timestamp,
        metadata={}
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
async def get_rfcs() -> res_types.GetRfcsResponse:
    """
    `GET /rfcs`: Obtain a list of all current RFCs.
    """
    return await api.get_rfcs()


@app.post("/rfc", response_model=res_types.PostRfcResponse)
async def post_rfc(
    request: req_types.PostRfcRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> res_types.PostRfcResponse:
    """
    `POST /rfc`: Upload a new RFC document.
    """
    return await api.post_rfc(
        user=current_user,
        title=request.title,
        slug=request.slug,
        status=request.status,
        summary=request.summary,
        content=request.content,
    )


@app.get("/rfc/{rfc_id}", response_model=res_types.GetRfcResponse)
async def get_rfc_by_id(
    request: Request
) -> res_types.GetRfcResponse:
    """
    `GET /rfc/{rfc_id}`: Get the existing RFC document by ID.
    """
    if request.path_params.get("rfc_id") is None:
        raise HTTPException(
            status_code=400,
            detail="rfc_id must be a valid integer"
        )
    
    rfc_id = int(request.path_params.get("rfc_id")) # type: ignore

    return await api.get_rfc(
        rfc_id=rfc_id,
    )


@app.patch("/rfc/{rfc_id}")
async def patch_rfc_by_id(
    rfc_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: req_types.PatchRfcRequest
) -> res_types.PatchRfcResponse:
    """
    `PATCH /rfc/{rfc_id}`: Update an existing RFC.
    """
    return await api.patch_rfc(
        rfc_id=rfc_id,
        user=current_user,
        request=request
    )


@app.post("/rfc/comment", response_model=res_types.PostRfcCommentResponse)
async def post_rfc_comment(
    request: req_types.PostRfcCommentRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> res_types.PostRfcCommentResponse:
    """
    `POST /rfc/comment`: Post a new comment on an existing RFC.
    """
    return await api.post_rfc_comment(
        rfc_id=request.rfc_id,
        parent_comment_id=request.parent_comment_id,
        content=request.content,
        user=current_user
    )


@app.get("/rfc/{rfc_id}/comments", response_model=res_types.GetRfcCommentsResponse)
async def get_rfc_comments(
    request: Request,
) -> res_types.GetRfcCommentsResponse:
    """
    `GET /rfc/{rfc_id}/comments`: Get all comments on an existing RFC.
    """
    if request.path_params.get("rfc_id") is None:
        raise HTTPException(
            status_code=400,
            detail="rfc_id must be a valid integer"
        )
    
    rfc_id = int(request.path_params.get("rfc_id")) # type: ignore

    return await api.get_rfc_comments(
        rfc_id=rfc_id
    )


@app.get("/rfc/{rfc_id}/comment/{comment_id}", response_model=res_types.GetRfcCommentResponse)
async def get_rfc_comment(
    request: Request,
) -> res_types.GetRfcCommentResponse:
    """
    `GET /rfc/{rfc_id}/comment/{comment_id}`: Get a specific comment on a specific RFC.
    """
    if request.path_params.get("rfc_id") is None:
        raise HTTPException(
            status_code=400,
            detail="rfc_id must be a valid integer"
        )
    if request.path_params.get("comment_id") is None:
        raise HTTPException(
            status_code=400,
            detail="comment_id must be a valid integer"
        )
    
    rfc_id = int(request.path_params.get("rfc_id")) # type: ignore
    comment_id = int(request.path_params.get("comment_id")) # type: ignore

    return await api.get_rfc_comment(
        rfc_id=rfc_id,
        comment_id=comment_id
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