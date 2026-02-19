import datetime

from pydantic import BaseModel


class RFCDocument(BaseModel):
    rfc_id: int
    author_username: str
    author_email: str
    created_at: datetime.datetime
    summary: str
    content: str


class RFCDocumentSummary(BaseModel):
    rfc_id: int
    author_username: str
    created_at: datetime.datetime
    summary: str