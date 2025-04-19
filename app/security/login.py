from app.security.jwt_auth import create_access_token, create_refresh_token
from app.utils import hash
from app.data_base.models import User
from app.data_base.profiles import Create_public_profile, Create_private_profile
from app.data_base.db_setup import SessionLocal
from fastapi import HTTPException
from app.getElemets import profile


respons_login = User(
    name="admin1",
    password="admin1234"
)


def chek_login(respons_login):
    if respons_login.name is None or respons_login.password is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    with SessionLocal() as db:
        user = db.query(User).filter(User.name == respons_login.name).first()
        if user is None: raise HTTPException(status_code=401, detail="Invalid credentials")
        
        valid_password = hash.hash_password(respons_login.password, user.salt)
        
        if valid_password == user.password:
            public_profile = profile.getPublic_profile(db, user.id)

            if not public_profile:
                db.add(Create_public_profile(user))
                db.add(Create_private_profile(user))
                db.commit()
                public_profile = profile.getPublic_profile(db, user.id)
                
            TokenUser = {"id" : user.id, "name" : user.name, "email" : user.email}
            tokens = {"access_token":create_access_token(TokenUser), "refresh_token":create_refresh_token(TokenUser)}
            
            return {"tokens" : tokens, "public_profile" : public_profile}
        
        raise HTTPException(status_code=401, detail="Invalid credentials")

print(chek_login(respons_login))


'''if respons_login.name is None or respons_login.password is None:
    raise HTTPException(status_code=401, detail="Invalid credentials")
'''