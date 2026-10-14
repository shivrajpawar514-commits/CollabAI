import asyncio
import json
import logging
import re
import uuid
from typing import Dict, Set, Optional, List, Any
from fastapi import WebSocket

logger = logging.getLogger("collabai.ws")


class ConnectionManager:
    def __init__(self):
        # project_id -> Set[WebSocket]
        self.project_rooms: Dict[str, Set[WebSocket]] = {}
        # user_id -> Set[WebSocket] (for direct notifications)
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_client = None
        self._pubsub_task = None

    async def connect_project(self, websocket: WebSocket, project_id: str, user_id: str):
        await websocket.accept()
        if project_id not in self.project_rooms:
            self.project_rooms[project_id] = set()
        self.project_rooms[project_id].add(websocket)

        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)

        logger.info(f"User {user_id} connected to project room {project_id}")

    def disconnect_project(self, websocket: WebSocket, project_id: str, user_id: str):
        if project_id in self.project_rooms:
            self.project_rooms[project_id].discard(websocket)
            if not self.project_rooms[project_id]:
                del self.project_rooms[project_id]

        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"User {user_id} disconnected from project room {project_id}")

    async def connect_user_notifications(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected to notifications channel")

    def disconnect_user_notifications(self, websocket: WebSocket, user_id: str):
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        logger.info(f"User {user_id} disconnected from notifications channel")

    async def broadcast_to_project(self, project_id: str, event_type: str, data: Dict[str, Any]):
        message = json.dumps({"type": event_type, "data": data})
        if project_id in self.project_rooms:
            dead_sockets = set()
            for ws in self.project_rooms[project_id]:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead_sockets.add(ws)
            for ws in dead_sockets:
                self.project_rooms[project_id].discard(ws)

    async def send_to_user(self, user_id: str, event_type: str, data: Dict[str, Any]):
        message = json.dumps({"type": event_type, "data": data})
        if user_id in self.user_connections:
            dead_sockets = set()
            for ws in self.user_connections[user_id]:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead_sockets.add(ws)
            for ws in dead_sockets:
                self.user_connections[user_id].discard(ws)


def parse_mentions(text: str) -> List[str]:
    """Extracts @username mentions from text."""
    return re.findall(r"@([a-zA-Z0-9_-]+)", text)


ws_manager = ConnectionManager()
