from app.data_base.db_setup import SessionLocal
from app.utils.active_connections import active_connections
from app.getElements.chats import get_chat_item
from app.getElements.profile import getPublic_profile
from datetime import datetime

from app.data_base.models import UserKeyAES
from app.utils.AES_256 import decrypt_AES_256_ECB
from app.config import AES_KEY_1

from app.utils import AES_GCM

async def send_chat_item_to_related_users(user_id):
    with SessionLocal() as db:
        active_user_ids = list(active_connections.keys())
        for active_user_id in active_user_ids:
            if active_user_id == user_id:
                continue 
            try:
                for_decrypt = db.query(UserKeyAES).filter(UserKeyAES.id == active_user_id).first()
                key_rec = bytes.fromhex(for_decrypt.key_aes)
                key_rec = decrypt_AES_256_ECB(AES_KEY_1, key_rec)
            except Exception as e:
                print(f"Не удалось получить ключ пользователя {active_user_id} [флаг онлайна]")
                continue
            
            chat_item = get_chat_item(db, active_user_id, user_id)
            
            if not chat_item:
                continue
            message_decrypt = chat_item["text"]
            
            try:
                message_encrypt, iv, tag = AES_GCM.encrypt(message_decrypt, key_rec)
                chat_item["text"] = message_encrypt
                chat_item["iv"] = iv
                chat_item["tag"] = tag
            except Exception as e:
                print(f"При попытке зашифровать сообщение для пользователя {active_user_id} возникла ошибка [флаг онлайна]")
            
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
