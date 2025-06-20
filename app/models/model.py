from pydantic import BaseModel

class User(BaseModel):
    name: str
    password: str

class New_user(BaseModel):
    name: str
    email: str
    password: str

class Public_profile(BaseModel):
    id: int
    name: str
    avatar: str 
    status: str | None = None
    online: int 
    lastonline: str

class Private_profile(BaseModel):
    id: int
    name: str
    email: str
    avatar: str 
    status: str | None = None
    online: int

class RefreshRequest(BaseModel):
    refreshToken: str

class NewStatus(BaseModel):
    status: str


class PublicRSA(BaseModel):
    key: str

class AesChipherKey(BaseModel):
    key: str
