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
    asyncio.run(_run_setup(args))


async def _run_setup(
    args: Namespace,
) -> None:
    """
    Run the MDRFC setup process (postgres, etc).
    """
    await _run_postgres_setup(args)

    print("finished MDRFC environment setup successfully")


async def _run_postgres_setup(
    args: Namespace,
) -> None:
    """
    Attempt to connect to the Postgres DB and create the necessary tables.
    """
    if DATABASE_URL is None:
        print("the environment variable DATABASE_URL was not found; it must be set to ensure Posgres works properly")
        exit(1)

    if args.verbose:
        print("attempting to connect to Postgres DB...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"failed to connect to the Posgres DB, exiting: {e}")
        exit(1)
    
    await conn.close()