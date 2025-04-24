import json
from app.webSockets.websocket_manager import WebSocketManager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.security.jwt_auth import valid_token
from app.getElements import updateElements
from app.utils import user_online
import logging
from app.getElements import chat


logger = logging.getLogger("uvicorn.error")

router = APIRouter()

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
        await user_online.online(user_id)
        logger.info(f"[WebSocket] Пользователь {user_id} подключился")
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)
            action = json_data.get("action")

            if action == "changeName":
                await updateElements.change_name(user_id, json_data, websocket)
            elif action == "giveChats":
                await chat.give_chats(user_id, websocket)
                
                ''' добавил на будущее, пока что просто чаты
            elif action == "sendMessage":
                await chat.send_message(user_id, json_data, websocket)
            elif action == "deleteMessage":
                await chat.delete_message(user_id, json_data, websocket)
            elif action == "editMessage":
                await chat.edit_message(user_id, json_data, websocket)
            elif action == "readMessage":
                await chat.read_message(user_id, json_data, websocket)
            elif action == "reaction":
                await chat.reaction(user_id, json_data, websocket)'''
                
            else:
                await websocket.send_text("Unknown action")

    except WebSocketDisconnect:
        await user_online.offline(user_id)
        user_online.last_online(user_id)
        logger.info(f"[WebSocket] Пользователь {user_id} отключился")
    except Exception as e:
        print(f"Ошибка: {e}")
        await websocket.close()
        

