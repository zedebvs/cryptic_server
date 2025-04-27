from app.data_base.db_setup import SessionLocal
from app.data_base.models import Private_profile, Public_profile
from datetime import datetime
from app.utils.send_online import send_chat_item_to_related_users



async def online(user_id):
    with SessionLocal() as db:
        private_profile = db.query(Private_profile).filter(Private_profile.id == user_id).first()
        public_profile = db.query(Public_profile).filter(Public_profile.id == user_id).first()

        if private_profile and public_profile:
            private_profile.online += 1
            public_profile.online += 1
            db.commit()
    await send_chat_item_to_related_users(user_id)

async def offline(user_id):    
    with SessionLocal() as db:
        private_profile = db.query(Private_profile).filter(Private_profile.id == user_id).first()
        public_profile = db.query(Public_profile).filter(Public_profile.id == user_id).first()

        if private_profile and public_profile:
            private_profile.online = max(private_profile.online - 1, 0)
            public_profile.online = max(public_profile.online - 1, 0)
            db.commit()
    await send_chat_item_to_related_users(user_id)

def last_online(user_id):
    with SessionLocal() as db:
        profile = db.query(Public_profile).filter(Public_profile.id == user_id).first()
        if profile:
            if profile.online == 0:
                profile.lastonline = datetime.now()
                db.commit()

