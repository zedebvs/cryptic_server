from app.security import login, jwt_auth
from app.security.registration import registration
from fastapi import APIRouter, status
from app.models import model
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.model import RefreshRequest

router = APIRouter() 
security = HTTPBearer()

@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(data: model.User):
    tokens = login.chek_login(data)
    return tokens

@router.post("/registration", status_code=status.HTTP_200_OK)
def registration_user(data: model.New_user):
    tokens = registration(data)
    return tokens

@router.post("/refresh")
def refresh_token(request: RefreshRequest):
    token = request.refreshToken 
    token_new = jwt_auth.new_token(token)
    return {"accessToken": token_new}
