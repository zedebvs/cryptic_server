from app import config 
from app import data
from datetime import datetime, timedelta
from jose import jwt 

User_data = data.User

def create_access_token(User_data):
    to_encode = User_data.copy()
    iat = datetime.utcnow()
    exp = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"iat": iat, "exp": exp})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def create_refresh_token(User_data):
    to_encode = User_data.copy()
    iat = datetime.utcnow()
    exp = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"iat": iat, "exp": exp})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def check_token (token, User_data):
    try:
        payload = jwt.decode(token, config.SECRET_KEY)
        if payload["id"] != User_data["id"] or payload["name"] != User_data["name"] or payload["email"] != User_data["email"]:
            return False
        if payload["exp"] < datetime.utcnow():
            return f"{User_data['id']}: need new token"
        return True  
    except jwt.JWTError:
        return "wrong token"


