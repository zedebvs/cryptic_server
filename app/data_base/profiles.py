from app.data_base.models import Public_profile, Private_profile

def Create_public_profile(new_rows):
    return Public_profile(
        id=new_rows.id,
        avatar="default_avatar_3.png",
        status=None,
        online=0
    )

def Create_private_profile(new_rows):
    return Private_profile(
        id=new_rows.id,
        avatar="default_avatar_3.png",
        status=None,
        online=0
    )