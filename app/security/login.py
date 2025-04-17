from app.security.jwt_auth import create_access_token, create_refresh_token
from app.utils import hash
from app.data_base.models import User
from app.data_base.db_setup import SessionLocal
from fastapi import HTTPException

def chek_login(respons_login):
    with SessionLocal() as db:
        users = db.query(User).filter(User.name == respons_login.name).first()
        if users is None: raise HTTPException(status_code=401, detail="Invalid credentials")
        
        valid_password = hash.hash_password(respons_login.password, users.salt)
        
        if valid_password == users.password:
            TokenUser = {"id" : users.id, "name" : users.name, "email" : users.email}
            tokens = {"access_token":create_access_token(TokenUser), "refresh_token":create_refresh_token(TokenUser)}
            return tokens
        
        raise HTTPException(status_code=401, detail="Invalid credentials")

