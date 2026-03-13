import time
from datetime import datetime, timezone
from typing import Any, Literal
import uuid

from fastapi import HTTPException

import mdrfc.requests as req_types
import mdrfc.responses as res_types
from mdrfc.backend.comment import RFCComment, RFCCommentInDB, build_comment_threads, find_comment_thread
from mdrfc.backend.db import (
    get_revision_from_db,
    get_revisions_from_db,
    get_rfc_from_db,
    get_rfcs_from_db,
    register_revision_in_db,
    register_rfc_in_db,
    register_comment_in_db,
    get_rfc_comments_from_db,
    check_comment_is_on_rfc
)
from mdrfc.backend.document import AgentContributor, RFCDocumentInDB, RFCRevisionInDB
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


#
# RFC endpoints
#
async def get_rfcs(
    current_user: User | None,
) -> res_types.GetRfcsResponse:
    """
    Handle a request to the endpoint `GET /rfcs`.
    """
    result = await get_rfcs_from_db()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC documents found"
        )
    
    if current_user is None:
        result = [summary for summary in result if summary.public]
    
    return res_types.GetRfcsResponse(
        rfcs=result,
        metadata={}
    )


async def post_rfc(
    user: User,
    request: req_types.PostRfcRequest    
) -> res_types.PostRfcResponse:
    """
    Handle a request to the endpoint `POST /rfc`.
    """
    timestamp = datetime.now(timezone.utc)

    first_revision_id = uuid.uuid4()
    agent_contributions = {
        first_revision_id: request.agent_contributors
    }

    document = RFCDocumentInDB(
        id=-1, # this will not be used
        created_by=user.id,
        created_at=timestamp,
        updated_at=timestamp,
        title=request.title,
        slug=request.slug,
        status=request.status,
        content=request.content,
        summary=request.summary,
        revisions=[first_revision_id],
        current_revision=first_revision_id,
        agent_contributions=agent_contributions, # type: ignore
        public=request.public,
    )

    rfc_id = await register_rfc_in_db(document)

    return res_types.PostRfcResponse(
        rfc_id=rfc_id,
        created_at=timestamp,
        metadata={}
    )


async def get_rfc(
    rfc_id: int,
    current_user: User | None,
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
    
    if (current_user is None) and (not document.public):
        raise HTTPException(
            status_code=401,
            detail="unable to get this RFC"
        )
    
    return res_types.GetRfcResponse(
        rfc=document,
        metadata={}
    )


#
# REVISION endpoints
#
async def get_rfc_revisions(
    rfc_id: int,
    current_user: User | None,
) -> res_types.GetRfcRevisionsResponse:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}/revs`.
    """
    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC document with the given ID found"
        )
    
    if (current_user is None) and (not rfc.public):
        raise HTTPException(
            status_code=401,
            detail="unable to access this RFC"
        )
    
    revisions = await get_revisions_from_db(rfc_id)

    if revisions is None:
        raise HTTPException(
            status_code=404,
            detail="no revisions for the given RFC document ID found"
        )
    
    return res_types.GetRfcRevisionsResponse(
        revisions=revisions,
        metadata={}
    )


async def get_rfc_revision(
    rfc_id: int,
    revision_id: str,
    current_user: User | None
) -> res_types.GetRfcRevisionResponse:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}/rev/{revision_id}`.    
    """
    revision = await get_revision_from_db(
        rfc_id=rfc_id,
        revision_id=revision_id,
    )

    if revision is None:
        raise HTTPException(
            status_code=404,
            detail="revision not found"
        )
    
    if (current_user is None) and (not revision.public):
        raise HTTPException(
            status_code=401,
            detail="unable to get this revision"
        )
    
    return res_types.GetRfcRevisionResponse(
        revision=revision,
        metadata={}
    )


async def post_rfc_revision(
    rfc_id: int,
    user: User,
    request: req_types.PostRfcRevisionRequest
) -> res_types.PostRfcRevisionResponse:
    """
    Handle a request to the endpoint `POST /rfc/{rfc_id}/rev`.
    """
    timestamp = datetime.now(timezone.utc)
    rev_id = uuid.uuid4()

    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(
            status_code=404,
            detail="RFC not found"
        )
    
    to_update: dict[str, Any] = {
        "title": request.update.title or rfc.title,
        "slug": request.update.slug or rfc.slug,
        "status": request.update.status or rfc.status,
        "content": request.update.content or rfc.content,
        "summary": request.update.summary or rfc.summary,
        "agent_contributors": request.update.agent_contributors or [],
        "public": request.update.public or rfc.public,
    }

    revision = RFCRevisionInDB(
        id=rev_id, # not used
        rfc_id=rfc_id,
        created_at=timestamp,
        created_by=user.id,
        agent_contributors=to_update.get("agent_contributors"), # type: ignore
        title=to_update.get("title"), # type: ignore
        slug=to_update.get("slug"), # type: ignore
        status=to_update.get("status"), # type: ignore
        content=to_update.get("content"), # type: ignore
        summary=to_update.get("summary"), # type: ignore
        public=to_update.get("public"), # type: ignore
        message=request.message
    )

    rfc.revisions.append(rev_id)
    rfc.agent_contributions[rev_id] = to_update.get("agent_contributors") or [] # type: ignore[index]

    new_revision = await register_revision_in_db(
        rfc_id=rfc_id,
        user=user,
        request=revision,
        new_revisions=rfc.revisions,
        new_contributions=rfc.agent_contributions
    )
    if new_revision is None:
        raise HTTPException(
            status_code=400,
            detail="unable to revise RFC"
        )

    return res_types.PostRfcRevisionResponse(
        revision=new_revision,
        metadata={}
    )


#
# COMMENT endpoints
#
async def post_rfc_comment(
    rfc_id: int,
    user: User,
    request: req_types.PostRfcCommentRequest
) -> res_types.PostRfcCommentResponse:
    """
    Handle a request to the endpoint `POST /rfc/comment`.
    """
    timestamp = datetime.now(timezone.utc)

    comment = RFCCommentInDB(
        id=-1, # this will not be used
        parent_id=request.parent_comment_id,
        rfc_id=rfc_id,
        created_by=user.id,
        created_at=timestamp,
        content=request.content
    )

    comment_id = await register_comment_in_db(comment)

    return res_types.PostRfcCommentResponse(
        comment_id=comment_id,
        created_at=timestamp,
        metadata={}
    )


async def get_rfc_comments(
    rfc_id: int,
    current_user: User | None,
) -> res_types.GetRfcCommentsResponse:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}/comments`.
    """
    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC document with the given ID found"
        )
    
    if (current_user is None) and (not rfc.public):
        raise HTTPException(
            status_code=401,
            detail="unable to access this RFC"
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
    current_user: User | None,
) -> res_types.GetRfcCommentResponse:
    """
    Handle a request to the endpoint `GET /rfc/{rfc_id}/comment/{comment_id}`.
    """
    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(
            status_code=404,
            detail="no RFC document with the given ID found"
        )
    
    if (current_user is None) and (not rfc.public):
        raise HTTPException(
            status_code=401,
            detail="unable to access this RFC"
        )
    
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
