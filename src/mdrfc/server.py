from argparse import Namespace
from contextlib import asynccontextmanager
from datetime import timedelta
from os import getenv
from typing import Annotated
import logging
import time

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn

from mdrfc.backend.auth import (
    Token,
    User,
    authenticate_user,
    create_access_token,
    get_current_active_user
)
from mdrfc.backend.cache import MdrfcCache
from mdrfc.backend.db import (
    init_db,
    close_db
)
from mdrfc.utils.logging import init_logger
import mdrfc.api as api
import mdrfc.responses as res_types


logger = logging.getLogger(__name__)

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if ACCESS_TOKEN_EXPIRE_MINUTES is None:
    raise RuntimeError("environment variable ACCESS_TOKEN_EXPIRE_MINUTES is required but was not found")


async def _server_startup(app: FastAPI):
    """
    Server startup handler.
    """
    logger.info("server starting up...")

    cache = MdrfcCache()
    await cache.setup()
    app.state.cache = cache

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
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    `POST /token`: Log in using OAuth2 and obtain an access token.
    """
    user = authenticate_user(form_data.username, form_data.password)
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


@app.get("/users/me", response_model=User)
async def get_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    `GET /users/me`: Get information on the current user.
    """
    return current_user


@app.get("/rfcs", response_model=res_types.GetRfcsResponse)
async def get_rfcs() -> res_types.GetRfcsResponse:
    """
    `GET /rfcs`: Obtain a list of all current RFCs.
    """
    return await api.get_rfcs(app.state.cache)


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