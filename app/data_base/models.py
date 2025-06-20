from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UUID, Boolean
from sqlalchemy.orm import relationship
from app.data_base.db_setup import Base, engine
import uuid
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum

class User(Base):
    __tablename__ = "users_"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    
    public_profile = relationship("Public_profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    private_profile = relationship("Private_profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sent_messages = relationship("Messages", back_populates="sender", foreign_keys="Messages.sender_id")
    received_messages = relationship("Messages", back_populates="recipient", foreign_keys="Messages.recipient_id")
    user_key_aes = relationship("UserKeyAES", back_populates="user", uselist=False, cascade="all, delete-orphan")##

class Public_profile(Base):
    __tablename__ = "public_profile"
    id = Column(Integer, ForeignKey("users_.id", ondelete="CASCADE"), primary_key=True, index=True)
    avatar = Column(String, default="default_avatar_3.png")
    status = Column(String, nullable=True)
    online = Column(Integer, default=0)
    lastonline = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="public_profile")
    

class Private_profile(Base):
    __tablename__ = "private_profile"
    id = Column(Integer, ForeignKey("users_.id", ondelete="CASCADE"), primary_key=True, index=True)
    avatar = Column(String, default="default_avatar_3.png")
    status = Column(String, nullable=True)
    online = Column(Integer, default=0)
    
    user = relationship("User", back_populates="private_profile")
    
class MessageStatus(str, PyEnum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read" 
    
class Messages(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4) #юид чата
    sender_id = Column(Integer, ForeignKey("users_.id", ondelete="CASCADE"), nullable=False, index=True) #отправитель
    recipient_id = Column(Integer, ForeignKey("users_.id", ondelete="CASCADE"), nullable=False, index=True) #получатель
    message = Column(String, nullable=False) #текст сообщения
    timestamp = Column(DateTime, nullable=False, index=True) #дата отправки
    status = Column(SQLEnum(MessageStatus), default=MessageStatus.SENT) #статус сообщения типа отправлено, доставлено, получено
    reply_to = Column(UUID, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True) #ответ на сообщение
    is_edited = Column(Boolean, default=False) #флаг на редактор сообщения
    deleted_for_sender = Column(Boolean, default=False) #удаление для отправителя
    deleted_for_recipient = Column(Boolean, default=False) #удаление для получателя
    reaction = Column(String, nullable=True) #реакция на сообщение(мб дойдут руки;~)
    message_type = Column(String, default="text") #тип сообщения - на будущее 
    read_at = Column(DateTime, nullable=True) #дата прочтения тож на будущее
    attachment_url = Column(String, nullable=True) #вот тут спорная тема, буду я это делать так, но пусть будет пока тут 
    iv = Column(String, nullable=True)  # IV для шифрования
    tag = Column(String, nullable=True)  #tag для шифрования GCM но мб другой режим будет 
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")

class UserKeyAES(Base):
    __tablename__ = "user_key_aes"
    id = Column(Integer, ForeignKey("users_.id", ondelete="CASCADE"), primary_key=True, index=True) #id пользователя
    key_aes = Column(String, nullable=False)
    
    user = relationship("User", back_populates="user_key_aes")
#Base.metadata.create_all(engine)


