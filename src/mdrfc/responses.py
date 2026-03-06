from datetime import datetime
from typing import Any

from pydantic import BaseModel

from mdrfc.backend.comment import CommentThread
from mdrfc.backend.document import (
    RFCDocument,
    RFCDocumentSummary
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


class PostSignupResponse(BaseModel):
    """
    HTTP response object for `POST /signup`.
    """
    username: str
    email: str
    created_at: datetime
    metadata: dict[str, Any]


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