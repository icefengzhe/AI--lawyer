from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.db.base_class import Base
import datetime

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # 关联关系
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")