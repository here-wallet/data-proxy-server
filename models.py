from typing import Optional

from pydantic import BaseModel


class ResponseInModel(BaseModel):
    data: str


class RequestInModel(BaseModel):
    data: str
    topic_id: Optional[str]
    ttl: Optional[int]
    encrypted: bool = False
