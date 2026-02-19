from pydantic import BaseModel


class GetRootResponse(BaseModel):
    """
    HTTP response object for `GET /`.
    """
    name: str
    version: str
    status: str
    uptime: float