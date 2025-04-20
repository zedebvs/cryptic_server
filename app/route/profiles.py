from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.data_base.db_setup import SessionLocal
from app.security.jwt_auth import valid_token
from app.data_base.models import User
from app.getElemets.profile import getPublic_profile, getPrivate_profile
from app.getElemets.updateElements import update_status, update_avatar
from app.models.model import NewStatus
import shutil



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

@profile_router.get("/Status")
def update_Status(request: NewStatus, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  
    payload = valid_token(token)
    
    new_status = update_status(request.status, payload["id"])
    
    return {"NewStatus" : new_status}

@profile_router.post("/uploadAvatar")
def upload_avatar(file: UploadFile = File(...), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  
    payload = valid_token(token)
    
    filename = file.filename
    allowed_extensions = {"png", "jpg", "jpeg", "gif"}
    extension = filename.split(".")[-1].lower()
    if extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла")
    
    new_filename = f"user_{payload['id']}_avatar.{extension}"
    file_location = f"app/static/avatars/{new_filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    update_avatar(new_filename, payload['id'])

    return {"filename": new_filename}
