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


class GetRfcsResponse(BaseModel):
    """
    HTTP response object for `GET /rfcs`.
    """
    rfcs: list[RFCDocumentSummary]