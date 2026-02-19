import time

import mdrfc.responses as res_types
from mdrfc.utils.version import get_mdrfc_version


def get_root(
    time_start: float,
) -> res_types.GetRootResponse:
    """
    Handle a request to the endpoint `GET /`.
    """
    time_now = time.time()

    return res_types.GetRootResponse(
        name="mdrfc",
        version=get_mdrfc_version(),
        status="ok",
        uptime=(time_now - time_start)
    )


async def get_rfcs() -> res_types.GetRfcsResponse:
    """
    Handle a request to the endpoint `GET /rfcs`.
    """
    raise NotImplementedError