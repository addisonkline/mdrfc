from argparse import Namespace
from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI
import uvicorn

from mdrfc.backend.cache import MdrfcCache
from mdrfc.utils.logging import init_logger
import mdrfc.api as api
import mdrfc.responses as res_types


logger = logging.getLogger(__name__)


async def _server_startup(app: FastAPI):
    """
    Server startup handler.
    """
    logger.info("server starting up...")

    cache = MdrfcCache()
    await cache.setup()

    app.state.cache = cache
    app.state.time_start = time.time()

    logger.info("server startup complete")


async def _server_shutdown(app: FastAPI):
    """
    Server shutdown handler.
    """
    logger.info("server shutting down...")

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


@app.get("/rfcs", response_model=res_types.GetRfcsResponse)
async def get_rfcs() -> res_types.GetRfcsResponse:
    """
    `GET /rfcs`: Obtain a list of all current RFCs.
    """
    return await api.get_rfcs()


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