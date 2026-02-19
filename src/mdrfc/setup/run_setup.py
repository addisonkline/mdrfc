from argparse import Namespace
import asyncio


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
    print("Hello, world!")