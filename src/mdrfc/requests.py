from pydantic import BaseModel


class PostSignupRequest(BaseModel):
    """
    HTTP request object for `POST /signup`.
    """
    username: str
    email: str
    password: str


class PostRfcRequest(BaseModel):
    """
    HTTP request object for `POST /rfc`.
    """
    summary: str
    content: str