from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# 添加消息请求模型
class MessageRequest(BaseModel):
    content: str

class MessageBase(BaseModel):
    content: str
    role: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    chat_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    title: str = "新对话"

class ChatCreate(ChatBase):
    pass

class ChatUpdate(ChatBase):
    pass

class Chat(ChatBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    
    class Config:
        from_attributes = True 