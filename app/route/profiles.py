from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.data_base.db_setup import SessionLocal
from app.security.jwt_auth import valid_token
from data_base.models import User
from getElemets.profile import getPublic_profile, getPrivate_profile




profile_router = APIRouter() 
security = HTTPBearer()

@profile_router.get("/publicProfile")
def post_PublicProfile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  
    payload = valid_token(token)
    with SessionLocal() as db:
        try:
            user = db.query(User).filter(User.id == payload["id"]).first()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid user")
            user_id = user.id
        except Exception as e:
            raise HTTPException(status_code=401, detail="invalid user")
        return getPublic_profile(db, user_id)

@profile_router.get("/privateProfile")
def post_PrivateProfile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  
    payload = valid_token(token)
    with SessionLocal() as db:
        try:
            user = db.query(User).filter(User.id == payload["id"]).first()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid user")
            user_id = user.id
        except Exception as e:
            raise HTTPException(status_code=401, detail="invalid user")
        return getPrivate_profile(db, user_id)