from pydantic import BaseModel

class User(BaseModel):
    name: str
    password: str

class New_user(BaseModel):
    name: str
    email: str
    password: str

