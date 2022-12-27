import json
import time
from queue import Queue
from threading import Thread

import jwt
from hyper import HTTPConnection
from loguru import logger
from pydantic import BaseModel


class Task(BaseModel):
    device_token: str
    title: str
    body: str
    push_type: int = 1


class ApnsPusher:
    def __init__(
        self,
        key_id,
        key,
        team_id,
        topic,
        use_sandbox: bool = False,
    ):
        self.key_id = key_id
        with open(key, "r") as f:
            self.secret = f.read()
        self.team_id = team_id
        self.topic = topic
        self.use_sandbox = use_sandbox
        self._task_queue = Queue()

    def _get_request_headers(self, background=False):
        token = jwt.encode(
            {"iss": self.team_id, "iat": time.time()},
            self.secret,
            algorithm="ES256",
            headers={
                "alg": "ES256",
                "kid": self.key_id,
            },
        )

        resp = {
            "apns-expiration": "0",
            "apns-push-type": "alert",
            "apns-priority": "5",
            "apns-topic": self.topic,
            "authorization": "bearer {0}".format(token),
        }
        if background:
            resp["apns-push-type"] = "background"
        return resp

    def _send_push(
        self,
        device_token,
        title,
        body,
        push_type=0,
        payload: dict = None,
        badge=None,
    ):
        path = "/3/device/{0}".format(device_token)

        if self.use_sandbox:
            conn = HTTPConnection("api.development.push.apple.com:443")
        else:
            conn = HTTPConnection("api.push.apple.com:443")

        payload_data = {
            "aps": {
                "alert": {"title": title, "body": body},
                "sound": "default",
                "content-available": 1,
            },
            "push_type": push_type,
        }
        if payload:
            payload_data.update(payload)

        if badge is not None:
            payload_data["aps"]["badge"] = int(badge)

        payload = json.dumps(payload_data).encode("utf-8")

        conn.request("POST", path, payload, headers=self._get_request_headers())
        resp = conn.get_response()
        logger.info("Apn notification resp: " + str(resp.read()))

    def send_notification(self, task: Task):
        self._task_queue.put_nowait(task)

    def _task(self):
        while True:
            t: Task = self._task_queue.get()
            self._send_push(t.device_token, t.title, t.body, t.push_type)

    def run(self, n=10):
        tasks = []
        for i in range(n):
            t = Thread(target=self._task)
            t.start()
            tasks.append(t)
