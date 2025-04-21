from app.data_base.db_setup import SessionLocal
from app.data_base.models import Private_profile, Public_profile, User
from fastapi import HTTPException


def update_status(status, id):
    with SessionLocal() as db:
        try:
            private_profile = db.query(Private_profile).filter(Private_profile.id).first()
            public_profile = db.query(Public_profile).filter(Public_profile.id).first()
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
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == id).first()
        if user:
            user.name = new_name
            db.commit()
    print(f"Пользователь {id} сменил имя на {new_name}")
    await websocket.send_text(f"Имя успешно изменено на {new_name}")

