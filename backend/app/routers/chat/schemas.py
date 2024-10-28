from pydantic import BaseModel, Field
from typing import List, Optional

class WebSocketMessage(BaseModel):
    chat_id: int
    message: str

class ChatMessage(BaseModel):
    content: str
    role: str
    timestamp: str

class ChatResponse(BaseModel):
    id: int
    title: str
    messages: List[ChatMessage]

class ChatHistoryItem(BaseModel):
    id: int
    title: str

class ChatCreate(BaseModel):
    title: str = "New Chat"
