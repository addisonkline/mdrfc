from datetime import datetime
from typing import Literal

from pydantic import BaseModel

RFCStatus = Literal["draft", "open", "accepted", "rejected"]

class RFCDocument(BaseModel):
    id: int
    author_name_last: str
    author_name_first: str
    created_at: datetime
    updated_at: datetime
    title: str
    slug: str
    status: RFCStatus
    content: str
    summary: str


class RFCDocumentSummary(BaseModel):
    id: int
    author_name_last: str
    author_name_first: str
    created_at: datetime
    updated_at: datetime
    title: str
    slug: str
    status: RFCStatus
    summary: str


class RFCDocumentInDB(BaseModel):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    title: str
    slug: str
    status: RFCStatus
    content: str
    summary: str