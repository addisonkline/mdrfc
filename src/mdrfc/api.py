import time
from datetime import datetime
from typing import Literal
import uuid

from fastapi import HTTPException

import mdrfc.requests as req_types
import mdrfc.responses as res_types
from mdrfc.backend.comment import RFCComment, build_comment_threads, find_comment_thread
from mdrfc.backend.db import (
    get_rfc_from_db,
    get_rfcs_from_db,
    patch_rfc_in_db,
    register_rfc_in_db,
    register_comment_in_db,
    get_rfc_comments_from_db,
    check_comment_is_on_rfc
)
from mdrfc.backend.document import AgentContributor, RFCDocumentInDB, RFCDocumentUpdate
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
        uptime=(time_now - time_start),
        metadata={}
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
        rfcs=result,
        metadata={}
    )


async def post_rfc(
    user: User,
    title: str,
    slug: str,
    status: Literal["draft", "open"],
    summary: str,
    content: str,
    agent_contributors: list[AgentContributor]    
) -> res_types.PostRfcResponse:
    """
    Handle a request to the endpoint `POST /rfc`.
    """
    timestamp = datetime.now()

    first_revision_id = uuid.uuid4()
    agent_contributions = {
        first_revision_id: agent_contributors
    }

    document = RFCDocumentInDB(
        id=-1, # this will not be used
        created_by=user.id,
        created_at=timestamp,
        updated_at=timestamp,
        title=title,
        slug=slug,
        status=status,
        content=content,
        summary=summary,
        revisions=[first_revision_id],
        current_revision=first_revision_id,
        agent_contributions=agent_contributions   
    )

    rfc_id = await register_rfc_in_db(document)

    return res_types.PostRfcResponse(
        rfc_id=rfc_id,
        created_at=timestamp,
        metadata={}
    )


async def get_rfc(
    rfc_id: int,
) -> res_types.GetRfcResponse:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}`.
    """
    document = await get_rfc_from_db(rfc_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC document with the given ID found"
        )
    
    return res_types.GetRfcResponse(
        rfc=document,
        metadata={}
    )


async def patch_rfc(
    rfc_id: int,
    user: User,
    request: req_types.PatchRfcRequest
) -> res_types.PatchRfcResponse:
    """
    Handle a request to the endpoint `PATCH /rfc/{rfc_id}`.
    """
    update = RFCDocumentUpdate(
        title=request.title,
        slug=request.slug,
        status=request.status,
        content=request.content,
        summary=request.summary,
        agent_contributors=request.agent_contributors
    )

    document = await patch_rfc_in_db(
        rfc_id=rfc_id,
        user=user,
        update=update,
    )
    if document is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC document with the given ID found"
        )

    return res_types.PatchRfcResponse(
        rfc=document,
        metadata={}
    )


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
        created_at=timestamp,
        metadata={}
    )


async def get_rfc_comments(
    rfc_id: int,
) -> res_types.GetRfcCommentsResponse:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}/comments`.
    """
    if await get_rfc_from_db(rfc_id) is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC document with the given ID found"
        )

    comment_rows = await get_rfc_comments_from_db(rfc_id)
    comment_threads = build_comment_threads(comment_rows)

    return res_types.GetRfcCommentsResponse(
        comment_threads=comment_threads,
        metadata={}
    )


async def get_rfc_comment(
    rfc_id: int,
    comment_id: int,
) -> res_types.GetRfcCommentResponse:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}/comment/{comment_id}`.
    """
    if not await check_comment_is_on_rfc(comment_id, rfc_id):
        raise HTTPException(
            status_code=400,
            detail="comment_id does not match rfc_id"
        )

    comment_rows = await get_rfc_comments_from_db(rfc_id)
    comment_threads = build_comment_threads(comment_rows)
    comment_thread = find_comment_thread(comment_threads, comment_id)

    if comment_thread is None:
        raise HTTPException(
            status_code=404,
            detail="comment with given ID not found"
        )

    return res_types.GetRfcCommentResponse(
        comment=comment_thread,
        metadata={}
    )
