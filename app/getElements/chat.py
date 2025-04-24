from sqlalchemy import or_, func
from app.getElements.profile import getPublic_profile
from data_base.db_setup import SessionLocal
from data_base.models import Messages

async def give_chats(user_id: int, websocket):
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
        print(f"обьекты из бд: {last_messages}\n")
        response_data = []
        
        for msg in last_messages:
            peer_id = msg.recipient_id if msg.sender_id == user_id else msg.sender_id
            profile = getPublic_profile(db, peer_id)
            print(f'профиль: {profile}')
            if profile:
                combined_data = {
                    "id": str(msg.id),
                    "text": msg.message,
                    "timestamp": msg.timestamp.isoformat(),
                    "status": msg.status.value,
                    "sender_id": msg.sender_id,
                    "recipient_id": msg.recipient_id,
                    "profile_id": profile["id"],
                    "name": profile["name"],
                    "avatar": profile["avatar"],
                    "profile_status": profile["status"],
                    "online": profile["online"],
                    "lastonline": profile["lastonline"]
                }
                response_data.append(combined_data)

        await websocket.send_json({
            "action": "chats",
            "data": response_data
        })
        