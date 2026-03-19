from datetime import datetime
from typing import Any

from pydantic import BaseModel

from mdrfc.backend.comment import CommentThread, QuarantinedComment
from mdrfc.backend.document import (
    QuarantinedRFC,
    QuarantinedRFCSummary,
    RFCDocument,
    RFCDocumentSummary,
    RFCRevision,
    RFCRevisionSummary,
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


class GetQuarantinedRfcsResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/quarantined`.
    """

    quarantined_rfcs: list[QuarantinedRFCSummary]
    metadata: dict[str, Any]


class DeleteQuarantinedRfcResponse(BaseModel):
    """
    HTTP response object for `DELETE /rfcs/quarantined/{quarantine_id}`.
    """

    message: str
    deleted_at: datetime
    metadata: dict[str, Any]


class PostQuarantinedRfcResponse(BaseModel):
    """
    HTTP response object for `POST /rfcs/quarantined/{quarantine_id}`.
    """

    message: str
    unquarantined_at: datetime
    metadata: dict[str, Any]


class PostRfcResponse(BaseModel):
    """
    HTTP response object for `POST /rfcs`.
    """

    rfc_id: int
    created_at: datetime
    metadata: dict[str, Any]


class GetRfcResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/{rfc_id}`.
    """

    rfc: RFCDocument
    metadata: dict[str, Any]


class DeleteRfcResponse(BaseModel):
    """
    HTTP response object for `DELETE /rfcs/{rfc_id}`.
    """

    message: str
    quarantined_at: datetime
    metadata: dict[str, Any]


#
# REVISION endpoints
#
class GetRfcRevisionsResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/{rfc_id}/revs`.
    """

    revisions: list[RFCRevisionSummary]
    metadata: dict[str, Any]


class GetRfcRevisionResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/{rfc_id}/revs/{rev_id}`.
    """

    revision: RFCRevision
    metadata: dict[str, Any]


class PostRfcRevisionResponse(BaseModel):
    """
    HTTP response object for `POST /rfcs/{rfc_id}/revs`.
    """

    revision: RFCRevision
    metadata: dict[str, Any]


#
# COMMENT endpoints
#
class PostRfcCommentResponse(BaseModel):
    """
    HTTP response object for `POST /rfcs/{rfc_id}/comments`.
    """

    comment_id: int
    created_at: datetime
    metadata: dict[str, Any]


class GetRfcCommentsResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/{rfc_id}/comments`.
    """

    comment_threads: list[CommentThread]
    metadata: dict[str, Any]


class GetQuarantinedCommentsResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/{rfc_id}/comments/quarantined`.
    """

    quarantined_comments: list[QuarantinedComment]
    metadata: dict[str, Any]


class DeleteQuarantinedCommentResponse(BaseModel):
    """
    HTTP response object for `DELETE /rfcs/{rfc_id}/comments/quarantined/{quarantine_id}`.
    """

    message: str
    deleted_at: datetime
    metadata: dict[str, Any]


class PostQuarantinedCommentResponse(BaseModel):
    """
    HTTP response object for `POST /rfcs/{rfc_id}/comments/quarantined/{quarantine_id}`.
    """

    message: str
    unquarantined_at: datetime
    metadata: dict[str, Any]


class GetRfcCommentResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/{rfc_id}/comments/{comment_id}`.
    """

    comment: CommentThread
    metadata: dict[str, Any]


class DeleteRfcCommentResponse(BaseModel):
    """
    HTTP response object for `DELETE /rfcs/{rfc_id}/comments/{comment_id}`
    """

    message: str
    quarantined_at: datetime
    metadata: dict[str, Any]
