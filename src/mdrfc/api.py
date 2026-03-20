import time
from datetime import datetime, timezone
from typing import Any
import uuid

from fastapi import HTTPException

import mdrfc.requests as req_types
import mdrfc.responses as res_types
from mdrfc.backend.comment import (
    RFCCommentInDB,
    build_comment_threads,
    find_comment_thread,
)
from mdrfc.backend.db import (
    delete_comment_from_db,
    delete_rfc_from_db,
    get_comments_quarantined_in_db,
    get_rfcs_readme_in_db,
    get_revision_from_db,
    get_revisions_from_db,
    get_rfc_from_db,
    get_rfcs_from_db,
    get_rfcs_quarantined_from_db,
    get_rfcs_readme_rev_in_db,
    get_rfcs_readme_revs_in_db,
    quarantine_comment_in_db,
    quarantine_rfc_in_db,
    register_revision_in_db,
    register_rfc_in_db,
    register_comment_in_db,
    get_rfc_comments_from_db,
    check_comment_is_on_rfc,
    register_rfcs_readme_rev_in_db,
    unquarantine_comment_in_db,
    unquarantine_rfc_in_db,
)
from mdrfc.backend.document import (
    RFCDocumentInDB,
    RFCReadme,
    RFCReadmeRevisionInDB,
    RFCRevisionInDB,
)
from mdrfc.backend.users import User
from mdrfc.utils.version import get_mdrfc_version

#
# BASIC endpoints
#
async def get_root(
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
        metadata={},
    )


async def get_llms_txt(
    llms_txt: str,
) -> res_types.GetLlmsTxtResponse:
    """
    Handle a request to the endpoint `GET /llms.txt`.
    """
    return res_types.GetLlmsTxtResponse(
        content=llms_txt
    )


#
# RFC endpoints
#
def _check_rfcs_readme_visibility(
    user: User | None,
    rfcs_readme: RFCReadme,
) -> None:
    if (user is None) and (not rfcs_readme.public):
        raise HTTPException(
            status_code=401,
            detail="unauthorized",
        )


async def _get_current_rfcs_readme() -> RFCReadme:
    rfcs_readme = await get_rfcs_readme_in_db()
    if rfcs_readme is None:
        raise HTTPException(
            status_code=404,
            detail="RFC README not found",
        )
    return rfcs_readme


async def _build_rfcs_readme_revision(
    admin: User,
    reason: str,
    content: str | None,
    public: bool | None,
) -> RFCReadmeRevisionInDB:
    current_readme = await get_rfcs_readme_in_db()

    if current_readme is None:
        if content is None:
            raise HTTPException(
                status_code=400,
                detail="content is required for the initial RFC README revision",
            )
        next_content = content
        next_public = public if public is not None else False
    else:
        next_content = content if content is not None else current_readme.content
        next_public = public if public is not None else current_readme.public

    return RFCReadmeRevisionInDB(
        revision_id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        created_by=admin.id,
        reason=reason,
        content=next_content,
        public=next_public,
    )


async def get_rfcs_readme(
    user: User | None,
) -> res_types.GetRfcsReadmeResponse:
    """
    Handle a request to the endpoint `GET /rfcs/README`.
    """
    rfcs_readme = await _get_current_rfcs_readme()
    _check_rfcs_readme_visibility(user=user, rfcs_readme=rfcs_readme)

    return res_types.GetRfcsReadmeResponse(
        message="success",
        readme=rfcs_readme,
        metadata={},
    )


async def get_rfcs_readme_revs(
    user: User | None,
) -> res_types.GetRfcsReadmeRevsResponse:
    """
    Handle a request to the endpoint `GET /rfcs/README/revs`.
    """
    current_readme = await _get_current_rfcs_readme()
    _check_rfcs_readme_visibility(user=user, rfcs_readme=current_readme)
    revs = await get_rfcs_readme_revs_in_db()

    return res_types.GetRfcsReadmeRevsResponse(
        message="success",
        revisions=revs,
        metadata={},
    )


async def get_rfcs_readme_rev(
    user: User | None,
    revision_id: uuid.UUID,
) -> res_types.GetRfcsReadmeRevResponse:
    """
    Handle a request to the endpoint `GET /rfcs/README/rev`.
    """
    current_readme = await _get_current_rfcs_readme()
    _check_rfcs_readme_visibility(user=user, rfcs_readme=current_readme)

    rev = await get_rfcs_readme_rev_in_db(
        revision_id=revision_id,
    )
    if rev is None:
        raise HTTPException(
            status_code=404,
            detail="RFC README revision not found",
        )

    return res_types.GetRfcsReadmeRevResponse(
        message="success",
        revision=rev,
        metadata={},
    )


async def post_rfcs_readme_rev(
    admin: User,
    payload: req_types.PostRfcsReadmeRevRequest,
) -> res_types.PostRfcsReadmeRevResponse:
    """
    Handle a request to the endpoint `POST /rfcs/README/revs`.
    """
    rfcs_readme_rev_in_db = await _build_rfcs_readme_revision(
        admin=admin,
        reason=payload.reason,
        content=payload.content,
        public=payload.public,
    )

    rev = await register_rfcs_readme_rev_in_db(
        admin=admin,
        revision=rfcs_readme_rev_in_db,
    )

    return res_types.PostRfcsReadmeRevResponse(
        message="success",
        revision=rev,
        metadata={},
    )


async def get_rfcs(
    current_user: User | None,
) -> res_types.GetRfcsResponse:
    """
    Handle a request to the endpoint `GET /rfcs`.
    """
    result = await get_rfcs_from_db()

    if result is None:
        raise HTTPException(status_code=404, detail="no RFC documents found")

    if current_user is None:
        result = [summary for summary in result if summary.public]

    return res_types.GetRfcsResponse(rfcs=result, metadata={})


async def get_rfcs_quarantined() -> res_types.GetQuarantinedRfcsResponse:
    """
    Get a list of all quarantined RFCs.
    Specifically, all RFCs that have been soft-deleted (made invisible).
    """
    result = await get_rfcs_quarantined_from_db()

    return res_types.GetQuarantinedRfcsResponse(quarantined_rfcs=result, metadata={})


async def delete_rfc_quarantined(
    quarantine_id: int,
) -> res_types.DeleteQuarantinedRfcResponse:
    """
    Permanently delete a quarantined RFC.
    """
    await delete_rfc_from_db(quarantine_id=quarantine_id)

    return res_types.DeleteQuarantinedRfcResponse(
        message="success", deleted_at=datetime.now(timezone.utc), metadata={}
    )


async def post_rfc_quarantined(
    quarantine_id: int,
) -> res_types.PostQuarantinedRfcResponse:
    """
    Unquarantine and reupload an RFC.
    """
    await unquarantine_rfc_in_db(quarantine_id=quarantine_id)

    return res_types.PostQuarantinedRfcResponse(
        message="success", unquarantined_at=datetime.now(timezone.utc), metadata={}
    )


async def post_rfc(
    user: User, request: req_types.PostRfcRequest
) -> res_types.PostRfcResponse:
    """
    Handle a request to the endpoint `POST /rfcs`.
    """
    timestamp = datetime.now(timezone.utc)

    first_revision_id = uuid.uuid4()
    agent_contributions = {first_revision_id: request.agent_contributors}

    document = RFCDocumentInDB(
        id=-1,  # this will not be used
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
        agent_contributions=agent_contributions,  # type: ignore
        public=request.public,
    )

    rfc_id = await register_rfc_in_db(document)

    return res_types.PostRfcResponse(rfc_id=rfc_id, created_at=timestamp, metadata={})


async def get_rfc(
    rfc_id: int,
    current_user: User | None,
) -> res_types.GetRfcResponse:
    """
    Handle a request to the endpoint `GET /rfcs/{rfc_id}`.
    """
    document = await get_rfc_from_db(rfc_id)

    if document is None:
        raise HTTPException(
            status_code=404, detail="no RFC document with the given ID found"
        )

    if (current_user is None) and (not document.public):
        raise HTTPException(status_code=401, detail="unable to get this RFC")

    return res_types.GetRfcResponse(rfc=document, metadata={})


async def delete_rfc(
    rfc_id: int,
    reason: str,
    user: User,
) -> res_types.DeleteRfcResponse:
    """
    Quarantine (soft-delete) an existing RFC.
    """
    await quarantine_rfc_in_db(rfc_id=rfc_id, reason=reason, user=user)

    return res_types.DeleteRfcResponse(
        message="success", quarantined_at=datetime.now(timezone.utc), metadata={}
    )


#
# REVISION endpoints
#
async def get_rfc_revisions(
    rfc_id: int,
    current_user: User | None,
) -> res_types.GetRfcRevisionsResponse:
    """
    Handle a request to the endpoint `GET /rfcs/{rfc_id}/revs`.
    """
    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(
            status_code=404, detail="no RFC document with the given ID found"
        )

    if (current_user is None) and (not rfc.public):
        raise HTTPException(status_code=401, detail="unable to access this RFC")

    revisions = await get_revisions_from_db(rfc_id)

    if revisions is None:
        raise HTTPException(
            status_code=404, detail="no revisions for the given RFC document ID found"
        )

    return res_types.GetRfcRevisionsResponse(revisions=revisions, metadata={})


async def get_rfc_revision(
    rfc_id: int, revision_id: str, current_user: User | None
) -> res_types.GetRfcRevisionResponse:
    """
    Handle a request to the endpoint `GET /rfcs/{rfc_id}/revs/{revision_id}`.
    """
    revision = await get_revision_from_db(
        rfc_id=rfc_id,
        revision_id=revision_id,
    )

    if revision is None:
        raise HTTPException(status_code=404, detail="revision not found")

    if (current_user is None) and (not revision.public):
        raise HTTPException(status_code=401, detail="unable to get this revision")

    return res_types.GetRfcRevisionResponse(revision=revision, metadata={})


async def post_rfc_revision(
    rfc_id: int, user: User, request: req_types.PostRfcRevisionRequest
) -> res_types.PostRfcRevisionResponse:
    """
    Handle a request to the endpoint `POST /rfcs/{rfc_id}/revs`.
    """
    timestamp = datetime.now(timezone.utc)
    rev_id = uuid.uuid4()

    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(status_code=404, detail="RFC not found")

    to_update: dict[str, Any] = {
        "title": request.update.title or rfc.title,
        "slug": request.update.slug or rfc.slug,
        "status": request.update.status or rfc.status,
        "content": request.update.content or rfc.content,
        "summary": request.update.summary or rfc.summary,
        "agent_contributors": request.update.agent_contributors or [],
        "public": request.update.public
        if request.update.public is not None
        else rfc.public,
    }

    revision = RFCRevisionInDB(
        id=rev_id,  # not used
        rfc_id=rfc_id,
        created_at=timestamp,
        created_by=user.id,
        agent_contributors=to_update.get("agent_contributors"),  # type: ignore
        title=to_update.get("title"),  # type: ignore
        slug=to_update.get("slug"),  # type: ignore
        status=to_update.get("status"),  # type: ignore
        content=to_update.get("content"),  # type: ignore
        summary=to_update.get("summary"),  # type: ignore
        public=to_update.get("public"),  # type: ignore
        message=request.message,
    )

    rfc.revisions.append(rev_id)
    rfc.agent_contributions[rev_id] = to_update.get("agent_contributors") or []  # type: ignore[index]

    new_revision = await register_revision_in_db(
        rfc_id=rfc_id,
        user=user,
        request=revision,
        new_revisions=rfc.revisions,
        new_contributions=rfc.agent_contributions,
    )
    if new_revision is None:
        raise HTTPException(status_code=400, detail="unable to revise RFC")

    return res_types.PostRfcRevisionResponse(revision=new_revision, metadata={})


#
# COMMENT endpoints
#
async def post_rfc_comment(
    rfc_id: int, user: User, request: req_types.PostRfcCommentRequest
) -> res_types.PostRfcCommentResponse:
    """
    Handle a request to the endpoint `POST /rfcs/{rfc_id}/comments`.
    """
    timestamp = datetime.now(timezone.utc)

    comment = RFCCommentInDB(
        id=-1,  # this will not be used
        parent_id=request.parent_comment_id,
        rfc_id=rfc_id,
        created_by=user.id,
        created_at=timestamp,
        content=request.content,
    )

    comment_id = await register_comment_in_db(comment)

    return res_types.PostRfcCommentResponse(
        comment_id=comment_id, created_at=timestamp, metadata={}
    )


async def get_rfc_comments(
    rfc_id: int,
    current_user: User | None,
) -> res_types.GetRfcCommentsResponse:
    """
    Handle a request to the endpoint `GET /rfcs/{rfc_id}/comments`.
    """
    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(
            status_code=404, detail="no RFC document with the given ID found"
        )

    if (current_user is None) and (not rfc.public):
        raise HTTPException(status_code=401, detail="unable to access this RFC")

    comment_rows = await get_rfc_comments_from_db(rfc_id)
    comment_threads = build_comment_threads(comment_rows)

    return res_types.GetRfcCommentsResponse(
        comment_threads=comment_threads, metadata={}
    )


async def get_rfc_comments_quarantined(
    rfc_id: int,
) -> res_types.GetQuarantinedCommentsResponse:
    """
    Get a list of all quarantined comments on a given RFC.
    """
    comments = await get_comments_quarantined_in_db(rfc_id=rfc_id)

    return res_types.GetQuarantinedCommentsResponse(
        quarantined_comments=comments, metadata={}
    )


async def delete_rfc_comment_quarantined(
    rfc_id: int,
    quarantine_id: int,
) -> res_types.DeleteQuarantinedCommentResponse:
    """
    Fully delete a quarantined comment.
    """
    await delete_comment_from_db(rfc_id=rfc_id, quarantine_id=quarantine_id)

    return res_types.DeleteQuarantinedCommentResponse(
        message="success", deleted_at=datetime.now(timezone.utc), metadata={}
    )


async def post_rfc_comment_quarantined(
    rfc_id: int,
    quarantine_id: int,
) -> res_types.PostQuarantinedCommentResponse:
    """
    Unquarantine and reupload a comment.
    """
    await unquarantine_comment_in_db(rfc_id=rfc_id, quarantine_id=quarantine_id)

    return res_types.PostQuarantinedCommentResponse(
        message="success", unquarantined_at=datetime.now(timezone.utc), metadata={}
    )


async def get_rfc_comment(
    rfc_id: int,
    comment_id: int,
    current_user: User | None,
) -> res_types.GetRfcCommentResponse:
    """
    Handle a request to the endpoint `GET /rfcs/{rfc_id}/comments/{comment_id}`.
    """
    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(
            status_code=404, detail="no RFC document with the given ID found"
        )

    if (current_user is None) and (not rfc.public):
        raise HTTPException(status_code=401, detail="unable to access this RFC")

    if not await check_comment_is_on_rfc(comment_id, rfc_id):
        raise HTTPException(status_code=400, detail="comment_id does not match rfc_id")

    comment_rows = await get_rfc_comments_from_db(rfc_id)
    comment_threads = build_comment_threads(comment_rows)
    comment_thread = find_comment_thread(comment_threads, comment_id)

    if comment_thread is None:
        raise HTTPException(status_code=404, detail="comment with given ID not found")

    return res_types.GetRfcCommentResponse(comment=comment_thread, metadata={})


async def delete_rfc_comment(
    rfc_id: int,
    comment_id: int,
    reason: str,
    user: User,
) -> res_types.DeleteRfcCommentResponse:
    """
    Handle a request to the endpoint `DELETE /rfcs/{rfc_id}/comments/{comment_id}`.
    """
    await quarantine_comment_in_db(
        rfc_id=rfc_id, comment_id=comment_id, reason=reason, user=user
    )

    return res_types.DeleteRfcCommentResponse(
        message="success", quarantined_at=datetime.now(timezone.utc), metadata={}
    )
