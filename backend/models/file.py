from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.base_class import Base
import datetime

class File(Base):
    __tablename__ = "file"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    filename = Column(String, index=True)
    file_path = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    user = relationship("User", back_populates="files") 