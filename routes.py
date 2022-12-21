import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Header
from loguru import logger
from pynear import transactions
from pynear.constants import TGAS
from pynear.utils import actions_to_link
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from sse_starlette import EventSourceResponse

from configs import APPLE_APP_SITE_ASSOCIATION, APY_KEY
from connection_manager import (
    get_connection_manager,
    ConnectionManager,
    get_push_manager,
)
from models import ResponseInModel, RequestInModel, SSEInModel, RequestOutModel
from push_notification import ApnsPusher, Task

router = APIRouter()


@router.post("/{request_id}/request")
def put_request(
    request_id: str,
    d: RequestInModel,
    cm: ConnectionManager = Depends(get_connection_manager()),
):
    cm.put_request(request_id, d.dict(), d.topic_id)
    return {"status": "ok"}


@router.post("/{request_id}/response")
def put_response(
    request_id: str,
    d: ResponseInModel,
    cm: ConnectionManager = Depends(get_connection_manager()),
):
    cm.put_response(request_id, d.data)
    return {"status": "ok"}


@router.get("/{request_id}/response")
def get_response(
    request_id: str, cm: ConnectionManager = Depends(get_connection_manager())
):
    return {"data": cm.get_response(request_id)}


@router.get("/{request_id}/request", response_model=RequestOutModel)
def get_request(
    request_id: str, cm: ConnectionManager = Depends(get_connection_manager())
):
    return cm.get_request(request_id)


@router.websocket("/ws/{request_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    request_id: str,
    cm: ConnectionManager = Depends(get_connection_manager(True)),
):
    await cm.connect(request_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        cm.disconnect(request_id)


@router.delete("/{request_id}")
def delete_response(
    request_id: str, cm: ConnectionManager = Depends(get_connection_manager())
):
    cm.delete_request(request_id)
    return {"status": "ok"}


@router.get("/by_topic")
def get_request(
    topic_ids: str, cm: ConnectionManager = Depends(get_connection_manager())
):
    requests = cm.get_requests_by_topics(topic_ids.split(";"))
    return {"ids": requests}


@router.get("/apple-app-site-association")
def get_apple_app_clip():
    return HTMLResponse(
        content=APPLE_APP_SITE_ASSOCIATION,
        status_code=200,
        headers={
            "Content-Type": "application/octet-stream",
        },
    )


@router.post("/sse_event")
def put_response(
    d: SSEInModel,
    cm: ConnectionManager = Depends(get_connection_manager()),
):
    if d.key != APY_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    cm.send_sse_for_user(d.near_account_id, d.data)
    return {"status": "ok"}


@router.post("/push_notification")
def push_notification(
    task: Task,
    authorization: str = Header(),
    ap: ApnsPusher = Depends(get_push_manager()),
):
    if authorization != APY_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    ap.send_notification(task)
    return {"status": "ok"}


@router.get("/notificator_stream")
async def message_stream(
    request: Request,
    near_account_id: str,
    cm: ConnectionManager = Depends(get_connection_manager()),
):

    cm.connect_sse(near_account_id)
    logger.info(f"Connect SSE {near_account_id}")

    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                logger.info("Client disconnected")
                cm.disconnect_sse(near_account_id)
                break

            # Checks for new messages and return them to client if any
            for mes in cm.get_sse_for_user(near_account_id):
                if isinstance(mes, dict):
                    mes = json.dumps(mes)
                yield mes

            await asyncio.sleep(0.1)

    return EventSourceResponse(event_generator())


@router.get("/{request}")
def redirect_to_web(
    request: str,
):
    return RedirectResponse(url=f"https://my.herewallet.app/approve/{request}")


@router.get("/a/{linkdrop}")
def redirect_to_linkdrop(
    linkdrop: str,
):
    return RedirectResponse(url=f"https://phone.herewallet.app/a/{linkdrop}")


@router.get("/keypom/{password}")
def redirect_to_keypom(
    password: str,
):
    link = actions_to_link(
        "keypom.near",
        [
            transactions.create_function_call_action(
                "claim",
                json.dumps({"password": password}).encode("utf8"),
                50 * TGAS,
                0,
            )
        ],
    )
    return RedirectResponse(url=link)
