import os
from app.utils import whitlists, hash
from app.data_base.models import User
from app.data_base.db_setup import SessionLocal
from app.data_base.profiles import Create_public_profile,Create_private_profile
from fastapi import HTTPException

new_user = User(
    name="admi1n11",
    email="admin@yandex.co1m11",
    password="admin1234"
)

def registration(new_user):
    with SessionLocal() as db:
        if not whitlists.valid_username(new_user.name):
            raise HTTPException(status_code=400, detail="bad name")
        
        if not whitlists.valid_email(new_user.email):
            raise HTTPException(status_code=400, detail="bad email")
        
        if len(new_user.password) < 8:
            raise HTTPException(status_code=400, detail="bad password")
        
        if db.query(User).filter(User.name == new_user.name).first() is not None:
            raise HTTPException(status_code=400, detail="Name exists")
        
        if db.query(User).filter(User.email == new_user.email).first() is not None:
            raise HTTPException(status_code=400, detail="Email exists")
        
        salt = os.urandom(32).hex()
        password_hash = hash.hash_password(new_user.password, salt)
        welcome_to_Cryptic = User(name=new_user.name, email=new_user.email, password=password_hash, salt=salt)
        
        try:
            db.add(welcome_to_Cryptic)
            db.commit()
            db.refresh(welcome_to_Cryptic)
            
            public_profile = Create_public_profile(welcome_to_Cryptic)
            private_profile = Create_private_profile(welcome_to_Cryptic)

            db.add(public_profile)
            db.add(private_profile)
            db.commit()
            
            return True
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"db_error: {str(e)}")

registration(new_user)

    