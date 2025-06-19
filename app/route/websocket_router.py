import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.security.jwt_auth import valid_token
from app.getElements import updateElements
from app.utils.active_connections import active_connections
import logging
from app.utils import user_online
from app.getElements.chats import give_chats, load_messages, send_message, message_read
import uuid
import time#
from app.utils.AES_256 import decrypt_AES_256_ECB
from app.config import AES_KEY_1
from app.data_base.db_setup import SessionLocal
from app.data_base.models import UserKeyAES

logger = logging.getLogger("uvicorn.error")

router = APIRouter()
last_ping = {}

#active_connections = {} #

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close()
        return HTTPException(status_code=401, detail="Invalid token")
    try:
        payload = valid_token(token)
        user_id = payload["id"]
        with SessionLocal() as db:
            for_encrypt = db.query(UserKeyAES).filter(UserKeyAES.id == user_id).first()
            key_encrypt = for_encrypt.key_aes
            key_encrypt = bytes.fromhex(key_encrypt)
            key_for_encrypt = decrypt_AES_256_ECB(AES_KEY_1, key_encrypt)

        session_id = str(uuid.uuid4()) 
        if user_id not in active_connections:
            active_connections[user_id] = {}
            
        active_connections[user_id][session_id] = websocket

        await user_online.online(user_id)
        logger.info(f"[WebSocket] Пользователь {user_id} подключился")
        
        last_ping[session_id] = time.time()#
        
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)
            action = json_data.get("action")
            ##
            if action == "ping":
                last_ping[session_id] = time.time()
                print(f'PING от пользователя {user_id}')
                continue
            ##
            if action == "changeName":
                await updateElements.change_name(user_id, json_data, websocket)
            elif action == "giveChats":
                await give_chats(user_id, websocket, key_for_encrypt)
            elif action == "loadMessages":
                await load_messages(user_id, json_data, websocket, key_for_encrypt)
            elif action == "sendMessage":
                await send_message(user_id, json_data, websocket, key_for_encrypt)
            elif action == "mark_as_read":
                await message_read(json_data, websocket, key_for_encrypt)
            else:
                await websocket.send_text("Unknown action")

    except WebSocketDisconnect:

        if user_id in active_connections:
            for session_id, ws in active_connections[user_id].items():
                if ws == websocket:
                    del active_connections[user_id][session_id]
                    logger.info(f"[WebSocket] Пользователь {user_id} с session_id {session_id} отключился")
                    break

        await user_online.offline(user_id)
        user_online.last_online(user_id)
        logger.info(f"[WebSocket] Пользователь {user_id} отключился")
    except Exception as e:
        print(f"Ошибка: {e}")
        if user_id in active_connections:
            for session_id, ws in active_connections[user_id].items():
                if ws == websocket:
                    del active_connections[user_id][session_id]
                    logger.info(f"[WebSocket] Пользователь {user_id} с session_id {session_id} отключился")
                    break
        await websocket.close()
        await user_online.offline(user_id)
        user_online.last_online(user_id)
        return
        ##
    finally:
        if session_id in last_ping:
            del last_ping[session_id]
