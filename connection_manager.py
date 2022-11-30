import collections
from enum import Enum
from typing import Dict, List, Union

from starlette.requests import Request
from starlette.websockets import WebSocket
from pydantic import BaseModel


class ClientNotificationEnum(int, Enum):
    PUSH = 1
    RATES_UPDATE = 2
    REFRESH = 3
    REFRESH_BALANCE = 4


class ClientNotificationData(BaseModel):
    event_type: ClientNotificationEnum = ClientNotificationEnum.PUSH
    payload: Union[dict, None] = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.requests = dict()
        self.response = dict()
        self.requests_by_topic = dict()
        self.topic_by_request = dict()

        self._connected_sse_users = set()
        self.notifications: Dict[
            str, List[ClientNotificationData]
        ] = collections.defaultdict(list)

    def connect(self, request_id, websocket):
        self.active_connections[request_id] = websocket

    def disconnect(self, request_id):
        self.active_connections.pop(request_id, None)

    def put_request(self, id_, request, topic_id):
        self.requests[id_] = request
        if topic_id:
            self.requests_by_topic[topic_id] = id_
            self.topic_by_request[id_] = topic_id
        if id_ in self.active_connections:
            self.active_connections[id_].send_json(
                {
                    "type": "request",
                    "data": request,
                }
            )

    def delete_request(self, id_):
        self.requests.pop(id_)
        self.response.pop(id_)
        if id_ in self.topic_by_request:
            self.requests_by_topic.pop(self.topic_by_request[id_])
            self.topic_by_request.pop(id_)
        if id_ in self.active_connections:
            self.active_connections[id_].send_json(
                {
                    "type": "delete",
                }
            )

    def put_response(self, id_, response):
        self.response[id_] = response
        if id_ in self.active_connections:
            self.active_connections[id_].send_json(
                {"type": "response", "data": response}
            )

    def get_request(self, id_):
        return self.requests.get(id_, None)

    def get_response(self, id_):
        return self.response.get(id_, None)

    def get_requests_by_topics(self, topic_ids: List[str]):
        res = []
        for tid in topic_ids:
            if tid in self.requests_by_topic:
                res.append(self.requests_by_topic[tid])
        return res

    def connect_sse(self, near_account_id):
        self._connected_sse_users.add(near_account_id)

    def disconnect_sse(self, near_account_id):
        if near_account_id in self._connected_sse_users:
            self._connected_sse_users.remove(near_account_id)

    def get_sse_for_user(self, near_account_id):
        return self.notifications.pop(near_account_id, [])

    def send_sse_for_user(self, near_account_id, data):
        if near_account_id not in self._connected_sse_users:
            return
        return self.notifications[near_account_id].append(data)


def get_connection_manager(websocket=False):
    async def app_conf(request: Request) -> ConnectionManager:
        return request.app.extra.get("connection_manager")

    async def app_conf_ws(ws: WebSocket) -> ConnectionManager:
        return ws.app.extra.get("connection_manager")

    if websocket:
        return app_conf_ws
    return app_conf
