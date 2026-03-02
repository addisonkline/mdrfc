import time
from datetime import datetime

from fastapi import HTTPException

import mdrfc.responses as res_types
from mdrfc.backend.comment import RFCComment
from mdrfc.backend.db import (
    get_rfc_from_db,
    get_rfcs_from_db,
    register_rfc_in_db,
    register_comment_in_db,
    get_rfc_comments_from_db,
    get_comment_from_db,
    check_comment_is_on_rfc
)
from mdrfc.backend.document import RFCDocument
from mdrfc.backend.users import User
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
    result = await get_rfcs_from_db()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC documents found"
        )
    
    return res_types.GetRfcsResponse(
        rfcs=result
    )


async def post_rfc(
    content: str,
    summary: str,
    user: User,    
) -> res_types.PostRfcResponse:
    """
    Handle a request to the endpoint `POST /rfc`.
    """
    timestamp = datetime.now()

    document = RFCDocument(
        id=-1, # this will not be used
        created_by=user.id,
        created_at=timestamp,
        content=content,
        summary=summary     
    )

    rfc_id = await register_rfc_in_db(document)

    return res_types.PostRfcResponse(
        rfc_id=rfc_id,
        created_at=timestamp,
    )


async def get_rfc(
    rfc_id: int,
) -> RFCDocument:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}`.
    """
    document = await get_rfc_from_db(rfc_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC document with the given ID found"
        )
    
    return document


async def post_rfc_comment(
    rfc_id: int,
    parent_comment_id: int | None,
    content: str,
    user: User,
) -> res_types.PostRfcCommentResponse:
    """
    Handle a request to the endpoint `POST /rfc/comment`.
    """
    timestamp = datetime.now()

    comment = RFCComment(
        id=-1, # this will not be used
        parent_id=parent_comment_id,
        rfc_id=rfc_id,
        created_by=user.id,
        created_at=timestamp,
        content=content
    )

    comment_id = await register_comment_in_db(comment)

    return res_types.PostRfcCommentResponse(
        comment_id=comment_id,
        created_at=timestamp
    )


async def get_rfc_comments(
    rfc_id: int,
) -> list[RFCComment]:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}/comments`.
    """
    if await get_rfc_from_db(rfc_id) is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC document with the given ID found"
        )
    
    return await get_rfc_comments_from_db(rfc_id)


async def get_rfc_comment(
    rfc_id: int,
    comment_id: int,
) -> RFCComment:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}/comment/{comment_id}`.
    """
    if not await check_comment_is_on_rfc(comment_id, rfc_id):
        raise HTTPException(
            status_code=400,
            detail="comment_id does not match rfc_id"
        )
    
    result = await get_comment_from_db(comment_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="comment with given ID not found"
        )
    
    return result