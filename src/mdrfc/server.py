from argparse import Namespace

from fastapi import FastAPI
import uvicorn


app = FastAPI()


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