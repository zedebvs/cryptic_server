import json
from app.webSockets import websocket_manager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.security.jwt_auth import valid_token
from app.getElemets import updateElements
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
        print(f"[WebSocket] Пользователь {user_id} подключился")
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)
            action = json_data.get("action")

            if action == "changeName":
                await updateElements.change_name(user_id, json_data, websocket)

            else:
                await websocket.send_text("Unknown action")

    except WebSocketDisconnect:
        print(f"[WebSocket] Пользователь {user_id} отключился")
    except Exception as e:
        print(f"Ошибка: {e}")
        await websocket.close()