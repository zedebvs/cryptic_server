from app.data_base.models import Public_profile, Private_profile

def getPublic_profile(db, user_id):
    public_profile = db.query(Public_profile).filter(Public_profile.id == user_id).first()
    if not public_profile:
        return None  
    
    avatar_url = f"https://192.168.0.222/static/avatars/{public_profile.avatar}" if public_profile.avatar else None

    
    return {
        "id": user_id,
        "name": public_profile.user.name,
        "avatar": avatar_url,
        "status": public_profile.status,
	"online": public_profile.online,
        "lastonline": public_profile.lastonline
    }

def getPrivate_profile(db, user_id):
    private_profile = db.query(Private_profile).filter(Private_profile.id == user_id).first()
    if not private_profile:
        return None  
    
    avatar_url = f"https://192.168.0.222/static/avatars/{private_profile.avatar}" if private_profile.avatar else None

    
    return {
        "id": user_id,
        "name": private_profile.user.name,
        "email": private_profile.user.email,
        "avatar": avatar_url,
        "status": private_profile.status,
	"online": private_profile.online
    }
