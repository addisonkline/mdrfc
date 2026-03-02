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


class PostRfcCommentRequest(BaseModel):
    """
    HTTP request object for `POST /rfc/comment`.
    """
    rfc_id: int
    parent_comment_id: int | None
    content: str