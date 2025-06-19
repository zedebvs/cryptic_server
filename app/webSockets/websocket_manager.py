from typing import Dict
from fastapi import WebSocket
from starlette.websockets import WebSocketState
import logging
from app.data_base.db_setup import SessionLocal
from app.data_base.models import Messages
from app.getElements.chats import get_chat_item
import json


logger = logging.getLogger("uvicorn.error")

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        user_online.online(user_id)
        logger.info(f"[WebSocket] Пользователь {user_id} подключился")
        
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            user_online.onffline(user_id)
            logger.info(f"[WebSocket] Пользователь {user_id} отключился")
            
    async def send_message(self, user_id: int, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket and websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for ws in self.active_connections.values():
            if ws.application_state == WebSocketState.CONNECTED:
                await ws.send_text(message)
                
    async def send_chat_item_to_related_users(self, updated_user_id: int):
        with SessionLocal() as db:
            related_user_ids = db.query(Messages.sender_id).filter(Messages.recipient_id == updated_user_id)\
                .union(
                    db.query(Messages.recipient_id).filter(Messages.sender_id == updated_user_id)
                ).distinct().all()

            related_user_ids = [row[0] for row in related_user_ids if row[0] != updated_user_id]

            for user_id in related_user_ids:
                item = get_chat_item(db, peer_id=updated_user_id, for_user_id=user_id)
                if item:
                    await self.send_message(user_id, json.dumps({
                        "action": "update_chat",
                        "data": item
                    }))
