import datetime

from pydantic import BaseModel


class RFCDocument(BaseModel):
    id: int
    created_by: int # user ID
    created_at: datetime.datetime
    content: str
    summary: str


class RFCDocumentSummary(BaseModel):
    id: int
    created_by: int # user ID
    created_at: datetime.datetime
    summary: str