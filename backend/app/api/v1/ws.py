import uuid
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from app.core.security import decode_token
from app.core.ws import ws_manager

logger = logging.getLogger("collabai.ws")
router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/projects/{project_id}")
async def websocket_project_chat(
    websocket: WebSocket,
    project_id: str,
    token: Optional[str] = Query(None)
):
    """
    Real-time bidirectional WebSocket endpoint for project rooms:
    - Broadcasts chat messages, task movements, team updates, and file uploads.
    """
    user_id = "anonymous"
    if token:
        payload = decode_token(token)
        if payload and payload.get("sub"):
            user_id = payload.get("sub")

    await ws_manager.connect_project(websocket, project_id, user_id)
    try:
        while True:
            # Keep-alive ping/pong or client action
            data = await websocket.receive_text()
            # If client sends a ping or echo
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect_project(websocket, project_id, user_id)
    except Exception as e:
        logger.warning(f"WebSocket error in project {project_id}: {e}")
        ws_manager.disconnect_project(websocket, project_id, user_id)


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    Dedicated WebSocket endpoint for real-time in-app notifications (mentions, invites, task assignments).
    """
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    await ws_manager.connect_user_notifications(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect_user_notifications(websocket, user_id)
    except Exception as e:
        logger.warning(f"Notification WS error for user {user_id}: {e}")
        ws_manager.disconnect_user_notifications(websocket, user_id)
