from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.crud.base import CRUDBase
from backend.models.chat import Chat, Message
from backend.schemas.chat import ChatCreate, ChatUpdate, MessageCreate

class CRUDChat(CRUDBase[Chat, ChatCreate, ChatUpdate]):
    def get_user_chats(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chat]:
        return (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_owner(
        self, db: Session, *, obj_in: ChatCreate, user_id: int
    ) -> Chat:
        obj_in_data = obj_in.model_dump()
        db_obj = Chat(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def add_message(
        self, db: Session, *, chat_id: int, message: MessageCreate
    ) -> Message:
        db_obj = Message(**message.model_dump(), chat_id=chat_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_messages(
        self, db: Session, *, chat_id: int, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        return (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, db: Session, *, id: int, obj_in: Dict[str, Any]
    ) -> Chat:
        db_obj = db.query(Chat).filter(Chat.id == id).first()
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_chat = CRUDChat(Chat) 