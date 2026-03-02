from datetime import datetime

from pydantic import BaseModel

from mdrfc.backend.document import RFCDocumentSummary


class GetRootResponse(BaseModel):
    """
    HTTP response object for `GET /`.
    """
    name: str
    version: str
    status: str
    uptime: float


class PostSignupResponse(BaseModel):
    """
    HTTP response object for `POST /signup`.
    """
    username: str
    email: str
    created_at: datetime


class GetRfcsResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs`.
    """
    rfcs: list[RFCDocumentSummary]


class PostRfcResponse(BaseModel):
    """
    HTTP response object for `POST /rfc`.
    """
    rfc_id: int
    created_at: datetime


class PostRfcCommentResponse(BaseModel):
    """
    HTTP response object for `POST /rfc/comment`.
    """
    comment_id: int
    created_at: datetime