from app.security.jwt_auth import create_access_token, create_refresh_token
from app.utils import hash
from app.data_base.models import User
from app.data_base.db_setup import SessionLocal


respons_login = {
    "name" : "zed",
    "password" : "test1234"
}


def chek_login(respons_login):
    with SessionLocal() as db:
        users = db.query(User).filter(User.name == respons_login["name"]).first()
        if users == None: return False
        valid_password = hash.hash_password(respons_login["password"], users.salt)
        
        if valid_password == users.password:
            TokenUser = {"id" : users.id, "name" : users.name, "email" : users.email}
            tokens = {"access_token":create_access_token(TokenUser), "refresh_token":create_refresh_token(TokenUser)}
            return tokens
        
        return False

print(chek_login(respons_login))
