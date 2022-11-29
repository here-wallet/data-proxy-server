from fastapi import APIRouter, Depends
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from configs import APPLE_APP_SITE_ASSOCIATION
from connection_manager import get_connection_manager, ConnectionManager
from models import ResponseInModel, RequestInModel

router = APIRouter()


@router.post("/{request_id}/request")
def put_request(
    request_id: str,
    d: RequestInModel,
    cm: ConnectionManager = Depends(get_connection_manager()),
):
    cm.put_request(request_id, d.data, d.topic_id)
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


@router.websocket("/ws/{request_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    request_id: str,
    cm: ConnectionManager = Depends(get_connection_manager()),
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


@router.get("/")
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
