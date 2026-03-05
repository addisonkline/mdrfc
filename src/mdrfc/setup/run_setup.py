from argparse import Namespace
from os import getenv
from sys import exit
import asyncio

import dotenv
import asyncpg # type: ignore


dotenv.load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")


def run_setup_sync(
    args: Namespace,
) -> None:
    """
    Run the async setup process (postgres, etc) using asyncio.
    """
    print("TODO")