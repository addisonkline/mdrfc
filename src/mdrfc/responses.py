from datetime import datetime
from typing import Any, Literal

from fastapi import Response
from pydantic import BaseModel

from mdrfc.backend.comment import CommentThread, QuarantinedComment
from mdrfc.backend.document import (
    QuarantinedRFCSummary,
    RFCDocument,
    RFCDocumentSummary,
    RFCReadme,
    RFCReadmeRevision,
    RFCReadmeRevisionSummary,
    RFCRevision,
    RFCRevisionSummary,
)


#
# BASIC endpoints
#
class GetRootResponse(BaseModel):
    """
    HTTP response object for `GET /`.
    """

    name: str
    version: str
    status: str
    uptime: float
    metadata: dict[str, Any]


class GetLlmsTxtResponse(Response):
    """
    HTTP response object for `GET /llms.txt`.
    """

    media_type: str = "text/plain"
    content: str


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
class GetRfcsReadmeResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/README`.
    """

    message: str
    readme: RFCReadme
    metadata: dict[str, Any]


class PatchRfcsReadmeResponse(BaseModel):
    """
    HTTP response object for `PATCH /rfcs/README`.
    """

    message: str
    readme: RFCReadme
    metadata: dict[str, Any]


class GetRfcsReadmeRevsResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/README/revs`.
    """

    message: str
    revisions: list[RFCReadmeRevisionSummary]
    metadata: dict[str, Any]


class GetRfcsReadmeRevResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/README/rev/{revision_id}`.
    """

    message: str
    revision: RFCReadmeRevision
    metadata: dict[str, Any]


class PostRfcsReadmeRevResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/README/rev/{revision_id}`.
    """

    message: str
    revision: RFCReadmeRevision
    metadata: dict[str, Any]


class PaginationMetadata(BaseModel):
    """
    Pagination metadata for list responses.
    """

    limit: int
    offset: int
    returned: int
    total: int
    has_more: bool


class EmptyFiltersMetadata(BaseModel):
    """
    Empty filter metadata for list responses with no server-side filters.
    """


class GetRfcsFiltersMetadata(BaseModel):
    """
    Filter metadata for `GET /rfcs`.
    """

    status: Literal["draft", "open", "accepted", "rejected"] | None = None
    public: bool | None = None
    author_id: int | None = None
    review_requested: bool | None = None


class GetRfcsMetadata(BaseModel):
    """
    Metadata payload for `GET /rfcs`.
    """

    pagination: PaginationMetadata
    filters: GetRfcsFiltersMetadata
    sort: str


class GetRfcCommentsMetadata(BaseModel):
    """
    Metadata payload for `GET /rfcs/{rfc_id}/comments`.
    """

    pagination: PaginationMetadata
    filters: EmptyFiltersMetadata
    sort: str


class GetRfcsResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs`.
    """

    rfcs: list[RFCDocumentSummary]
    metadata: GetRfcsMetadata


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


class GetRfcsReviewNeededResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs/review-needed`.
    """

    message: str
    rfcs: list[RFCDocumentSummary]
    metadata: dict[str, Any]


class PostRfcReviewResponse(BaseModel):
    """
    HTTP response object for `POST /rfcs/{rfc_id}/review`.
    """

    message: str
    requested_at: datetime
    metadata: dict[str, Any]


class PatchRfcStatusResponse(BaseModel):
    """
    HTTP response object for `PATCH /rfcs/{rfc_id}/status`.
    """

    message: str
    updated_at: datetime
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
    metadata: GetRfcCommentsMetadata


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
