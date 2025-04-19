from app.data_base.models import Public_profile, Private_profile

def getPublic_profile(db, user_id):
    public_profile = db.query(Public_profile).filter(Public_profile.id == user_id).first()
    if not public_profile:
        return None  
    return {
        "id": user_id,
        "name": public_profile.user.name,
        "avatar": f"/static/{public_profile.avatar}",
        "status": public_profile.status
    }

def getPrivate_profile(db, user_id):
    private_profile = db.query(Private_profile).filter(Private_profile.id == user_id).first()
    if not private_profile:
        return None  
    return {
        "id": user_id,
        "name": private_profile.user.name,
        "email": private_profile.user.email,
        "avatar": private_profile.avatar,
        "status": private_profile.status
    }