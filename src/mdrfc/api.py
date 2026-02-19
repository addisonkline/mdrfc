import time

from fastapi import HTTPException

import mdrfc.responses as res_types
from mdrfc.backend.cache import MdrfcCache
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


async def get_rfcs(
    cache: MdrfcCache
) -> res_types.GetRfcsResponse:
    """
    Handle a request to the endpoint `GET /rfcs`.
    """
    rfcs = await cache.get_rfcs()

    if rfcs is None:
        raise HTTPException(status_code=404, detail="no RFCs found")
    
    return res_types.GetRfcsResponse(
        rfcs=rfcs,
    )