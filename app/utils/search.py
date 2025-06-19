from app.data_base.db_setup import SessionLocal
from app.data_base.models import Public_profile, User
from app.models import model

def search_users(query):
    with SessionLocal() as db:
        results = db.query(Public_profile).join(User, User.id == Public_profile.id).filter(User.name.ilike(f"{query}%")).all()
        return [
        model.Public_profile(
            id=p.id,
            avatar=f"https://192.168.0.222/static/avatars/{p.avatar}" if p.avatar else None,
            status=p.status,
            online=p.online,
            name=p.user.name,  
            lastonline=p.lastonline.isoformat() if p.lastonline else None   
        )
        for p in results
    ]
