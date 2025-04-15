from sqlalchemy import Column, Integer, String
from app.data_base.db_setup import Base

class User(Base):
    __tablename__ = "users_"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)