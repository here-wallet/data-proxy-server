from typing import Dict, List

from starlette.requests import Request
from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.requests = dict()
        self.response = dict()
        self.requests_by_topic = dict()
        self.topic_by_request = dict()

    def put_request(self, id_, request, topic_id):
        self.requests[id_] = request
        if topic_id:
            self.requests_by_topic[topic_id] = id_
            self.topic_by_request[id_] = topic_id

    def delete_request(self, id_):
        self.requests.pop(id_)
        self.response.pop(id_)
        if id_ in self.topic_by_request:
            self.requests_by_topic.pop(self.topic_by_request[id_])
            self.topic_by_request.pop(id_)

    def put_response(self, id_, response):
        self.response[id_] = response

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


def get_connection_manager(websocket=False):
    async def app_conf(request: Request) -> ConnectionManager:
        return request.app.extra.get("connection_manager")

    async def app_conf_ws(ws: WebSocket) -> ConnectionManager:
        return ws.app.extra.get("connection_manager")

    if websocket:
        return app_conf_ws
    return app_conf
