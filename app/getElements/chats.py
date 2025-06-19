
from sqlalchemy import or_, func, and_
from app.getElements.profile import getPublic_profile
from app.data_base.db_setup import SessionLocal
from app.data_base.models import Messages, UserKeyAES
from datetime import datetime
from app.data_base.models import MessageStatus
#from app.utils.send_online import send_new_chat_item
from app.utils.active_connections import active_connections

from app.utils import AES_GCM 
from app.utils.AES_256 import decrypt_AES_256_ECB
from app.config import AES_KEY_1

async def give_chats(user_id: int, websocket, user_key_hex):
    with SessionLocal() as db:

        last_messages = (
            db.query(Messages)
            .distinct(
                func.least(Messages.sender_id, Messages.recipient_id),
                func.greatest(Messages.sender_id, Messages.recipient_id)
            )
            .filter(or_(Messages.sender_id == user_id, Messages.recipient_id == user_id))
            .order_by(
                func.least(Messages.sender_id, Messages.recipient_id),
                func.greatest(Messages.sender_id, Messages.recipient_id),
                Messages.timestamp.desc()
            )
            .all()
        )

        response_data = []

        for msg in last_messages:
            peer_id = msg.recipient_id if msg.sender_id == user_id else msg.sender_id
            profile = getPublic_profile(db, peer_id)
            
            if msg.sender_id != user_id:
                try:
                    for_encrypt = db.query(UserKeyAES).filter(UserKeyAES.id == msg.sender_id).first()
                    key_sender = bytes.fromhex(for_encrypt.key_aes)
                    key_sender = decrypt_AES_256_ECB(AES_KEY_1, key_sender)
                    message = AES_GCM.decrypt(msg.message, msg.iv, msg.tag, key_sender)
                    message_encrypt, iv, tag = AES_GCM.encrypt(message, user_key_hex)
                except Exception as e:
                    print(f'Ошибка при расшифровании последнего сообщения ID: {msg.id}')
                    message_encrypt = msg.message
                    iv = msg.iv
                    tag = msg.tag
            else:
                message_encrypt = msg.message
                iv = msg.iv
                tag = msg.tag

            if profile:
                combined_data = {
                    "id": str(msg.id),
                    "text": message_encrypt,
                    "timestamp":  msg.timestamp.isoformat() if msg.timestamp else None,
                    "status": msg.status.value,
                    "sender_id": msg.sender_id,
                    "recipient_id": msg.recipient_id,
                    "iv": iv,
                    "tag": tag,
                    "profile_id": profile["id"],
                    "name": profile["name"],
                    "avatar": profile["avatar"],
                    "profile_status": profile["status"],
                    "online": profile["online"],
                    "lastonline": profile["lastonline"].isoformat() if profile["lastonline"] else None
                }
                response_data.append(combined_data)
        print(f'пользователь {user_id} получил список своих чатов')
        await websocket.send_json({
            "action": "chats",
            "data": response_data
        })


def get_chat_item(db, peer_id, for_user_id):
    msg = (
        db.query(Messages)
        .filter(
            or_(
                (Messages.sender_id == peer_id) & (Messages.recipient_id == for_user_id),
                (Messages.sender_id == for_user_id) & (Messages.recipient_id == peer_id)
            )
        )
        .order_by(Messages.timestamp.desc())
        .first()
    )
    if not msg:
        return None

    try:
        for_decrypt = db.query(UserKeyAES).filter(UserKeyAES.id == msg.sender_id).first()
        key_sender = bytes.fromhex(for_decrypt.key_aes)
        key_sender = decrypt_AES_256_ECB(AES_KEY_1, key_sender)
        
        message = AES_GCM.decrypt(msg.message, msg.iv, msg.tag, key_sender)
        
    except Exception as e:
        print(f'Ошибка при расшифровании экземпляра измененного сообщения ID: {msg.id}sender: {msg.sender_id}')

        
    profile = getPublic_profile(db, for_user_id)
    if not profile:
        return None

    return {
        "id": str(msg.id),
        "text": message,
        "tag": msg.tag,
        "iv": msg.iv,
        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
        "status": msg.status.value,
        "sender_id": msg.sender_id,
        "recipient_id": msg.recipient_id,
        "profile_id": profile["id"],
        "name": profile["name"],
        "avatar": profile["avatar"],
        "profile_status": profile["status"],
        "online": profile["online"],
        "lastonline": profile["lastonline"].isoformat() if profile["lastonline"] else None
    }


async def load_messages(user_id, json_data, websocket, user_aes_key):
    recipient_id = json_data.get("recipient_id")
    if not recipient_id:
        await websocket.send_json({"error": "recipient_id required"})
        return

    with SessionLocal() as db:
        profile = getPublic_profile(db, recipient_id)
        if not profile:
            await websocket.send_json({"error": "Profile not found"})
            return
        
        profile_user = {
        "profile_id": profile["id"],
        "name": profile["name"],
        "avatar": profile["avatar"],
        "profile_status": profile["status"],
        "online": profile["online"],
        "lastonline": profile["lastonline"].isoformat() if profile["lastonline"] else None
        }
        
        messages_query = (
            db.query(Messages)
            .filter(
                or_(
                    and_(Messages.sender_id == user_id, Messages.recipient_id == recipient_id),
                    and_(Messages.sender_id == recipient_id, Messages.recipient_id == user_id)
                ),
                Messages.deleted_for_sender == False  
            )
            .order_by(Messages.timestamp.desc())
            .limit(50) 
        )
        try:
            for_decrypt = db.query(UserKeyAES).filter(UserKeyAES.id == recipient_id).first()
            key_recipient = bytes.fromhex(for_decrypt.key_aes)
            key_recipient = decrypt_AES_256_ECB(AES_KEY_1, key_recipient)
        except Exception as e:
            print(f"Ошибка при получении ключа пользователя {recipient_id} для пользователя {user_id}")
        
        messages = messages_query.all()

        response_data = []
        for msg in reversed(messages): 
            try:
                if msg.sender_id == recipient_id:
                    try:
                        message = AES_GCM.decrypt(msg.message, msg.iv, msg.tag, key_recipient)
                        message_encrypt, iv, tag = AES_GCM.encrypt(message, user_aes_key)
                    except Exception as e:
                        print(f"При попытке загрузить сообщение {msg.id} для пользователя {user_id} возникла ошибка при расшифровании")
                else:
                    message_encrypt = msg.message
                    iv = msg.iv
                    tag = msg.tag

                response_data.append({
                    "id": str(msg.id),
                    "sender_id": msg.sender_id,
                    "recipient_id": msg.recipient_id,
                    "text": message_encrypt,
                    "iv": iv,
                    "tag": tag,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "status": msg.status.value,
                    "is_edited": msg.is_edited,
                    "reaction": msg.reaction,
                    "message_type": msg.message_type,
                    "attachment_url": msg.attachment_url
                })
            except Exception as e:
                print(f"Ошибка с сообщением {msg.id}: {e}")
                continue

        await websocket.send_json({
            "action": "messages_list",
            "data": response_data,
            "profile": profile_user
        })

async def send_message(user_id, json_data, websocket, user_aes_key):
    recipient_id = json_data.get("recipient_id")
    message_text = json_data.get("message")
    tag_base64 = json_data.get("tag")
    iv_base64 = json_data.get("iv")
    
    if not recipient_id or not message_text:
        await websocket.send_json({"error": "Invalid message data"})
        return
    
    with SessionLocal() as db:
        new_message = Messages(
            sender_id=user_id,
            recipient_id=recipient_id,
            message=message_text,
            timestamp=datetime.now(),
            status=MessageStatus.DELIVERED,
            tag=tag_base64,
            iv=iv_base64
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        await websocket.send_json({
            "action": "message_sent",
            "data": {
                "id": str(new_message.id),
                "sender_id": new_message.sender_id,
                "recipient_id": new_message.recipient_id,
                "text": new_message.message,
                "timestamp": new_message.timestamp.isoformat(),
                "status": new_message.status.value,
                "is_edited": new_message.is_edited,
                "tag": new_message.tag,
                "iv": new_message.iv
            }
        })
        
        try:
            for_decrypt = db.query(UserKeyAES).filter(UserKeyAES.id == recipient_id).first()
            key_recipient = bytes.fromhex(for_decrypt.key_aes)
            key_recipient = decrypt_AES_256_ECB(AES_KEY_1, key_recipient)
        except Exception as e:
            print(f"Сообщение от пользователя {user_id} отправлено пользователю {new_message.recipient_id} но  возникла ошибка при получении ключа получателя")
        
        try:
            message_decrytp = AES_GCM.decrypt(new_message.message, new_message.iv, new_message.tag, user_aes_key)
            message_rec, iv_r, tag_r = AES_GCM.encrypt(message_decrytp, key_recipient)
            
        except Exception as e:
            print(f"Попытка зашифровать сообщение для получателя {recipient_id} не увенчалась успехом")
            
        for uid in [user_id, recipient_id]:
            if uid == user_id:
                chat_item = get_chat_item(db, user_id, recipient_id)
                message = chat_item["text"]
                try:
                    message_encrypt, iv, tag = AES_GCM.encrypt(message, user_aes_key)
                    chat_item["text"] = message_encrypt
                    chat_item["iv"] = iv
                    chat_item["tag"] = tag
                except Exception as e:
                    print(f"При попытке зашифровать сообщение для пользователя {uid} возникла ошибка")
            
            else:
                chat_item = get_chat_item(db, recipient_id, user_id)
                message = chat_item["text"]
                try:
                    message_encrypt, iv, tag = AES_GCM.encrypt(message, key_recipient)
                    chat_item["text"] = message_encrypt
                    chat_item["iv"] = iv
                    chat_item["tag"] = tag
                except Exception as e:
                    print(f"При попытке зашифровать сообщение для пользователя {uid} возникла ошибка")
                    
            user_sessions = active_connections.get(uid)
            if user_sessions:
                for session_id, user_ws in user_sessions.items():
                    try:
                        await user_ws.send_json({
                            "action": "updateChat",
                            "data": chat_item
                        })
                    except Exception as e:
                        print(f"Ошибка отправки updateChat пользователю {uid}: {e}")

        print(f"Пользователь {user_id} отправил сообщение пользователю {recipient_id}")

        recipient_sessions = active_connections.get(recipient_id)

        if recipient_sessions:
            for session_id, recipient_ws in recipient_sessions.items():
                try:
                    await recipient_ws.send_json({
                        "action": "new_message",
                        "data": {
                            "id": str(new_message.id),
                            "sender_id": new_message.sender_id,
                            "recipient_id": new_message.recipient_id,
                            "text": message_rec,
                            "iv": iv_r,
                            "tag": tag_r,
                            "timestamp": new_message.timestamp.isoformat(),
                            "status": new_message.status.value,
                            "is_edited": new_message.is_edited
                        }
                    })
                except Exception as e:
                    print(f"Ошибка отправки пользователю {recipient_id}: {e}")
                    
        
async def message_read(json_data, websocket, key_recipient):
    message_id = json_data.get("message_id")
    if not message_id:
        return
    with SessionLocal() as db:
        message = db.query(Messages).filter(Messages.id == message_id).first()
        if message:
            message.status = MessageStatus.READ
            db.commit()
            
            sender = message.sender_id
            recipient = message.recipient_id
            print(f'Пользователь {sender} прочитал сообщение {message_id} пользователя {recipient}')
            
            try:
                for_decrypt = db.query(UserKeyAES).filter(UserKeyAES.id == sender).first()
                key_sender = bytes.fromhex(for_decrypt.key_aes)
                key_sender = decrypt_AES_256_ECB(AES_KEY_1, key_sender)
            except Exception as e:
                print(f"Не удалось получить ключ пользователя {sender}")
                
            for uid in [recipient, sender]:
                if uid == recipient:
                    chat_item = get_chat_item(db, recipient, sender)
                    message_decrypt = chat_item["text"]
                    try:
                        message_encrypt, iv, tag = AES_GCM.encrypt(message_decrypt, key_recipient)
                        chat_item["text"] = message_encrypt
                        chat_item["iv"] = iv
                        chat_item["tag"] = tag
                        
                    except Exception as e:
                        print(f"При попытке зашифровать сообщение для пользователя {uid} возникла ошибка [флаг прочтения]")
                else:
                    chat_item = get_chat_item(db, sender, recipient)
                    message_decrypt = chat_item["text"]
                    try:
                        message_encrypt, iv, tag = AES_GCM.encrypt(message_decrypt, key_sender)
                        chat_item["text"] = message_encrypt
                        chat_item["iv"] = iv
                        chat_item["tag"] = tag
                    
                    except Exception as e:
                        print(f"При попытке зашифровать сообщение для пользователя {uid} возникла ошибка [флаг прочтения]")
                user_sessions = active_connections.get(uid)
                if user_sessions:
                    for session_id, user_ws in user_sessions.items():
                        try:
                            await user_ws.send_json({
                                "action": "message_read",
                                "data": {
                                    "id": str(message.id),
                                    "sender_id": message.sender_id,
                                    "recipient_id": message.recipient_id,
                                    "text": message_encrypt,
                                    "iv": iv,
                                    "tag": tag,
                                    "timestamp": message.timestamp.isoformat(),
                                    "status": message.status.value,
                                    "is_edited": message.is_edited
                                }
                            })
                            await user_ws.send_json({
                                "action": "updateChat",
                                "data": chat_item
                            })
                        except Exception as e:
                            print(f"Ошибка отправки updateChat пользователю {uid}: {e}")
        else:
            return
