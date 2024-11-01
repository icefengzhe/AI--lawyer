from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.db.base_class import Base
import datetime

class Chat(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    title = Column(String, default="新对话")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # 关联关系
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chat.id'))
    role = Column(String)  # 'user' 或 'assistant'
    content = Column(Text) 
    created_at = Column(DateTime, default=datetime.datetime.now)
    chat = relationship("Chat", back_populates="messages")