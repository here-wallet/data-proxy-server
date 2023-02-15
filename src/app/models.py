from typing import Optional, List

from pydantic import BaseModel


class ResponseInModel(BaseModel):
    data: str


class SSEEventModel(BaseModel):
    near_account_id: Optional[str]
    data: str


class SSEInModel(SSEEventModel):
    key: str


class SSEIEventsInModel(BaseModel):
    key: str
    events: List[SSEEventModel]


class RequestInModel(BaseModel):
    data: str
    type: str = "login"
    topic_id: Optional[str]
    ttl: Optional[int]
    encrypted: bool = False


class RequestOutModel(BaseModel):
    data: str
    encrypted: bool = False
