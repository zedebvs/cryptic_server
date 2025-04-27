from app.data_base.db_setup import SessionLocal
from app.data_base.models import Private_profile, Public_profile, User
from fastapi import HTTPException
from app.utils import whitlists
import logging
from app.utils.send_online import send_chat_item_to_related_users

logger = logging.getLogger("uvicorn.error")


def update_status(status, id):
    with SessionLocal() as db:
        try:
            private_profile = db.query(Private_profile).filter(Private_profile.id == id).first()
            public_profile = db.query(Public_profile).filter(Public_profile.id == id).first()
            if private_profile.name != public_profile.name:
                raise HTTPException(status_code=404, detail="invalid user")
            private_profile.status = status
            public_profile.status = status
            db.commit()
            return public_profile.status
        except Exception as e:
            raise HTTPException(status_code=404, detail="invalid user")

def update_avatar(avatar, id):
    with SessionLocal() as db:
        profile = db.query(Public_profile).filter(Public_profile.id == id).first()
        if profile:
            profile.avatar = avatar
            db.commit()
    with SessionLocal() as db:
        profile = db.query(Public_profile).filter(Public_profile.id == id).first()
        if profile:
            profile.avatar = avatar
            db.commit()


async def change_name(id, json_data, websocket):
    new_name = json_data.get("name")
    
    if not whitlists.valid_username(new_name):
        logger.info(f"[WebSocket] Пользователь {id} пытался сменить имя на недопустимое")
        await websocket.send_text(f"Ошибка: Недопустимое имя: {new_name}")
        return
    with SessionLocal() as db:
        if db.query(User).filter(User.name == new_name).first() is not None:
            logger.info(f"[WebSocket] Пользователь {id} пытался сменить имя на используемое")
            await websocket.send_text(f"Ошибка: Имя {new_name} занято")
            return
        
        user = db.query(User).filter(User.id == id).first()
        if user:
            user.name = new_name
            db.commit()
    print(f"[WebSocket] Пользователь {id} сменил имя на {new_name}")
    await send_chat_item_to_related_users(id)
    await websocket.send_text(f"Имя успешно изменено на {new_name}")

