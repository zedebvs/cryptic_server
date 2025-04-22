from app.data_base.db_setup import SessionLocal
from app.data_base.models import Private_profile, Public_profile, User

async def online(user_id):
    with SessionLocal() as db:
        private_profile = db.query(Private_profile).filter(Private_profile.id == user_id).first()
        public_profile = db.query(Public_profile).filter(Public_profile.id == user_id).first()

        if private_profile and public_profile:
            private_profile.online += 1
            public_profile.online += 1
            db.commit()

async def offline(user_id):
    with SessionLocal() as db:
        private_profile = db.query(Private_profile).filter(Private_profile.id == user_id).first()
        public_profile = db.query(Public_profile).filter(Public_profile.id == user_id).first()

        if private_profile and public_profile:
            private_profile.online = max(private_profile.online - 1, 0)
            public_profile.online = max(public_profile.online - 1, 0)
            db.commit()