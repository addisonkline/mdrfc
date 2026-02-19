from argparse import Namespace
from contextlib import asynccontextmanager
import time

from fastapi import FastAPI
import uvicorn

import mdrfc.api as api
import mdrfc.responses as res_types


async def _server_startup(app: FastAPI):
    """
    Server startup handler.
    """
    app.state.time_start = time.time()


async def _server_shutdown(app: FastAPI):
    """
    Server shutdown handler.
    """
    print("server shutdown complete")


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


def run_server(
    args: Namespace
) -> None:
    """
    Run the mdrfc server via the CLI.
    """
    uvicorn.run(
        "mdrfc.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )