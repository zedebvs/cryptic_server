from app.data_base.models import Public_profile, Private_profile
from datetime import datetime

def Create_public_profile(new_rows):
    return Public_profile(
        id=new_rows.id,
        avatar="default_avatar_3.png",
        status=None,
        online=0,
        lastonline=datetime.now()
    )

def Create_private_profile(new_rows):
    return Private_profile(
        id=new_rows.id,
        avatar="default_avatar_3.png",
        status=None,
	online=0
    )
