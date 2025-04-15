import os
from app.utils import whitlists
from app.utils import hash
from app.data_base.models import User
from app.data_base.db_setup import SessionLocal
import time


test_new_user ={
    "name" : "zedebvs31afsfsa211",
    "email" : "zedebvs@g1ma312il.com123",
    "password" : "zed12ljko3"
}

new_user = User(
    name=test_new_user["name"],
    email=test_new_user["email"],
    password=test_new_user["password"],
)

def registration(new_user):
    with SessionLocal() as db:
        if not whitlists.valid_username(new_user.name):
            return "bad name"
        
        if not whitlists.valid_email(new_user.email):
            return "bad email"
        
        if len(new_user.password) < 8:
            return "bad password"
        
        if db.query(User).filter(User.name == new_user.name).first() != None:
            return "Name exists"
        
        if db.query(User).filter(User.email == new_user.email).first() != None:
            return "Email exists"
        
        salt = os.urandom(32).hex()
        password_hash = hash.hash_password(new_user.password, salt)
        welcome_to_Cryptic = User(name=new_user.name, email=new_user.email, password=password_hash, salt=salt)
        
        try:
            db.add(welcome_to_Cryptic)
            db.commit()
            db.refresh(welcome_to_Cryptic)
            return True
        except:
            return False

print(registration(new_user))


    