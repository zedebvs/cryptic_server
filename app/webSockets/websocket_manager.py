from typing import Dict
from fastapi import WebSocket
from starlette.websockets import WebSocketState
import logging

logger = logging.getLogger("uvicorn.error")

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"[WebSocket] Пользователь {user_id} подключился")
        
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"[WebSocket] Пользователь {user_id} отключился")
            
    async def send_message(self, user_id: int, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket and websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for ws in self.active_connections.values():
            if ws.application_state == WebSocketState.CONNECTED:
                await ws.send_text(message)