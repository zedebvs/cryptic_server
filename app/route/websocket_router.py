import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.security.jwt_auth import valid_token
from app.getElements import updateElements
from app.utils import user_online, active_connections
import logging
from app.getElements import chat
import uuid
from app.utils.active_connections import active_connections

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
        
        session_id = str(uuid.uuid4()) 
        if user_id not in active_connections:
            active_connections[user_id] = {}
            
        active_connections[user_id][session_id] = websocket

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
            elif action == "loadMessages":
                await chat.load_messages(user_id, json_data, websocket) #json_data  должна быть примерно такого формата {recipient_id = f'{id}'} ну и потом парсим json и выводим список.
            elif action == "sendMessage":
                await chat.send_message(user_id, json_data, websocket)
                ''' добавил на будущее, пока что просто чаты
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
        
        if user_id in active_connections.active_connections:
            for session_id, ws in active_connections.active_connections[user_id].items():
                if ws == websocket:
                    del active_connections.active_connections[user_id][session_id]
                    logger.info(f"[WebSocket] Пользователь {user_id} с session_id {session_id} отключился")
                    break
        
        await user_online.offline(user_id)
        user_online.last_online(user_id)
        logger.info(f"[WebSocket] Пользователь {user_id} отключился")
    except Exception as e:
        print(f"Ошибка: {e}")
        await websocket.close()
        

