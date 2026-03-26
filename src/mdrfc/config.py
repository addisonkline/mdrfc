from typing import Literal

from pydantic import BaseModel


class ClientAlias(BaseModel):
    alias: str
    command: str


class MDRFCClientConfig(BaseModel):
    version: Literal["0.5.0"] = "0.5.0"
    aliases: list[ClientAlias] = []
