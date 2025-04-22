from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.data_base.db_setup import Base

class User(Base):
    __tablename__ = "users_"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    
    public_profile = relationship("Public_profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    private_profile = relationship("Private_profile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Public_profile(Base):
    __tablename__ = "public_profile"
    id = Column(Integer, ForeignKey("users_.id", ondelete="CASCADE"), primary_key=True, index=True)
    avatar = Column(String, default="default_avatar_3.png")
    status = Column(String, nullable=True)
    online = Column(Integer, default=0)

    user = relationship("User", back_populates="public_profile")
    

class Private_profile(Base):
    __tablename__ = "private_profile"
    id = Column(Integer, ForeignKey("users_.id", ondelete="CASCADE"), primary_key=True, index=True)
    avatar = Column(String, default="default_avatar_3.png")
    status = Column(String, nullable=True)
    online = Column(Integer, default=0)
    
    user = relationship("User", back_populates="private_profile")

#Base.metadata.create_all(engine)
