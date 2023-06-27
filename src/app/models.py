from typing import Optional, List

from pydantic import BaseModel


class ResponseInModel(BaseModel):
    data: Optional[str]


class SSEEventModel(BaseModel):
    near_account_id: Optional[str]
    data: Optional[str]


class SSEInModel(SSEEventModel):
    key: str


class SSEIEventsInModel(BaseModel):
    key: str
    events: List[SSEEventModel]


class RequestInModel(BaseModel):
    data: Optional[str]
    type: str = "login"
    topic_id: Optional[str]
    ttl: Optional[int]
    encrypted: bool = False


class RequestOutModel(BaseModel):
    data: Optional[str]
    encrypted: bool = False
