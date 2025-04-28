from app.data_base.db_setup import SessionLocal
from app.utils.active_connections import active_connections
from app.getElements.chats import get_chat_item
from app.getElements.profile import getPublic_profile

async def send_chat_item_to_related_users(user_id: int):
    with SessionLocal() as db:
        active_user_ids = list(active_connections.keys())
        for active_user_id in active_user_ids:
            if active_user_id == user_id:
                continue 
            chat_item = get_chat_item(db, active_user_id, user_id)
            if chat_item:
                for session_id, websocket in active_connections[active_user_id].items():
                    await websocket.send_json({
                        "action": "updateChat",
                        "data": chat_item
                    })


async def send_new_chat_item(user_id: int, recipient_id: int, websocket):
    with SessionLocal() as db:
        profile = getPublic_profile(db, recipient_id)
        if profile["online"] == 0:
            return
        chat_item = get_chat_item(db, recipient_id, user_id)
        await websocket.send_json({
                        "action": "updateChat",
                        "data": chat_item
                    })
