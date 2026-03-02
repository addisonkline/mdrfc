import datetime

from pydantic import BaseModel


class RFCComment(BaseModel):
    id: int
    parent_id: int | None
    rfc_id: int
    created_by: int
    created_at: datetime.datetime
    content: str