from app.security import login
from app.security.registration import registration
from fastapi import APIRouter, status
from app.models import model

router = APIRouter() 

@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(data: model.User):
    tokens = login.chek_login(data)
    return tokens

@router.post("/registration", status_code=status.HTTP_200_OK)
def registration_user(data: model.New_user):
    tokens = registration(data)
    return tokens