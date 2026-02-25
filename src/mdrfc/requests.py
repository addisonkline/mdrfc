from pydantic import BaseModel


class PostSignupRequest(BaseModel):
    """
    HTTP request object for `POST /signup`.
    """
    username: str
    email: str
    password: str
