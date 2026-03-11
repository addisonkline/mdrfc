from datetime import datetime
from typing import Any

from pydantic import BaseModel

from mdrfc.backend.comment import CommentThread
from mdrfc.backend.document import (
    RFCDocument,
    RFCDocumentSummary,
    RFCRevision,
    RFCRevisionSummary
)


class GetRootResponse(BaseModel):
    """
    HTTP response object for `GET /`.
    """
    name: str
    version: str
    status: str
    uptime: float
    metadata: dict[str, Any]

#
# AUTH endpoints
#
class PostSignupResponse(BaseModel):
    """
    HTTP response object for `POST /signup`.
    """
    username: str
    email: str
    created_at: datetime
    metadata: dict[str, Any]


class PostVerifyEmailResponse(BaseModel):
    """
    HTTP response object for `POST /verify-email`.
    """
    username: str
    email: str
    verified_at: datetime
    metadata: dict[str, Any]

#
# RFC endpoints
#
class GetRfcsResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs`.
    """
    rfcs: list[RFCDocumentSummary]
    metadata: dict[str, Any]


class PostRfcResponse(BaseModel):
    """
    HTTP response object for `POST /rfc`.
    """
    rfc_id: int
    created_at: datetime
    metadata: dict[str, Any]


class GetRfcResponse(BaseModel):
    """
    HTTP response object for `GET /rfc/{rfc_id}`.
    """
    rfc: RFCDocument
    metadata: dict[str, Any]


class PatchRfcResponse(BaseModel):
    """
    HTTP response object for `PATCH /rfc/{rfc_id}`.
    """
    rfc: RFCDocument
    metadata: dict[str, Any]


#
# REVISION endpoints
#
class GetRfcRevisionsResponse(BaseModel):
    """
    HTTP response object for `GET /rfc/{rfc_id}/revs`.
    """
    revisions: list[RFCRevisionSummary]
    metadata: dict[str, Any]


class GetRfcRevisionResponse(BaseModel):
    """
    HTTP response object for `GET /rfc/{rfc_id}/rev/{rev_id}`.
    """
    revision: RFCRevision
    metadata: dict[str, Any]


class PostRfcRevisionResponse(BaseModel):
    """
    HTTP response object for `POST /rfc/{rfc_id}/rev`.
    """
    revision: RFCRevision
    metadata: dict[str, Any]


#
# COMMENT endpoints
#
class PostRfcCommentResponse(BaseModel):
    """
    HTTP response object for `POST /rfc/comment`.
    """
    comment_id: int
    created_at: datetime
    metadata: dict[str, Any]


class GetRfcCommentsResponse(BaseModel):
    """
    HTTP response object for `GET /rfc/{rfc_id}/comments`.
    """
    comment_threads: list[CommentThread]
    metadata: dict[str, Any]


class GetRfcCommentResponse(BaseModel):
    """
    HTTP response object for `GET /rfc/{rfc_id}/comment/{comment_id}`.
    """
    comment: CommentThread
    metadata: dict[str, Any]
