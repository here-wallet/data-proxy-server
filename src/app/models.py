from typing import Optional

from pydantic import BaseModel


class ResponseInModel(BaseModel):
    data: str


class SSEInModel(BaseModel):
    data: str
    near_account_id: Optional[str]
    key: str


class RequestInModel(BaseModel):
    data: str
    type: str = "login"
    topic_id: Optional[str]
    ttl: Optional[int]
    encrypted: bool = False


class RequestOutModel(BaseModel):
    data: str
    type: Optional[str] = "login"
    encrypted: bool = False
