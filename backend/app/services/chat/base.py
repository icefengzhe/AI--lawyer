from app.services.base_service import BaseService
from app.models.database import Chat, Message
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime
from app.core.exceptions import NotFoundError, DatabaseError
import logging

logger = logging.getLogger(__name__)

class BaseChatService(BaseService[Chat]):
    def __init__(self):
        super().__init__(Chat)

    def get_user_chats(self, db: Session, user_id: int) -> List[Dict]:
        """获取用户的所有聊天"""
        try:
            chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).all()
            return [{"id": chat.id, "title": chat.title} for chat in chats]
        except Exception as e:
            logger.error(f"Error getting user chats: {str(e)}")
            raise

    def get_chat_with_messages(self, db: Session, chat_id: int, user_id: int) -> Optional[Dict]:
        """获取聊天及其消息"""
        try:
            chat = db.query(Chat).filter(
                Chat.id == chat_id,
                Chat.user_id == user_id
            ).first()
            
            if not chat:
                logger.warning(f"Chat {chat_id} not found for user {user_id}")
                return None

            messages = db.query(Message).filter(Message.chat_id == chat_id)\
                .order_by(Message.created_at.asc()).all()

            # 确保每条消息都有时间戳
            message_list = []
            for msg in messages:
                message_dict = {
                    "content": msg.content,
                    "role": msg.role,
                    "timestamp": msg.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if msg.created_at else None
                }
                message_list.append(message_dict)

            return {
                "id": chat.id,
                "title": chat.title,
                "messages": message_list
            }
        except Exception as e:
            logger.error(f"Error getting chat with messages: {str(e)}")
            raise

    def create_message(self, db: Session, chat_id: int, content: str, role: str) -> Message:
        """创建新消息"""
        try:
            message = Message(
                content=content,
                role=role,
                timestamp=datetime.utcnow(),
                chat_id=chat_id
            )
            db.add(message)
            db.commit()
            return message
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating message: {str(e)}")
            raise DatabaseError("Failed to create message")

    def get_chat_messages(
        self, 
        db: Session,
        chat_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> List[Message]:
        """分页获取聊天消息"""
        try:
            messages = db.query(Message)\
                .filter(Message.chat_id == chat_id)\
                .order_by(Message.timestamp.desc())\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()
            return messages[::-1]  # 反转消息顺序，使最新消息在最后
        except Exception as e:
            logger.error(f"Error getting chat messages: {str(e)}")
            raise DatabaseError("Failed to get chat messages")

    def update_chat_title(self, db: Session, chat_id: int, title: str) -> bool:
        """更新聊天标题"""
        try:
            chat = db.query(Chat).filter(Chat.id == chat_id).first()
            if chat:
                chat.title = title
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating chat title: {str(e)}")
            db.rollback()
            return False

    def delete_chat(self, db: Session, chat_id: int, user_id: int) -> bool:
        """删除聊天及其所有消息"""
        try:
            chat = db.query(Chat).filter(
                Chat.id == chat_id,
                Chat.user_id == user_id
            ).first()
            
            if not chat:
                return False

            # 删除相关的消息
            db.query(Message).filter(Message.chat_id == chat_id).delete()
            
            # 删除聊天
            db.delete(chat)
            db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {str(e)}")
            db.rollback()
            return False

    def create_new_chat(self, db: Session, user_id: int, title: str = "新对话") -> Chat:
        """创建新的聊天"""
        try:
            chat = Chat(
                user_id=user_id,
                title=title
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)
            logger.info(f"Created new chat for user {user_id}: {chat.id}")
            return chat
        except Exception as e:
            logger.error(f"Error creating new chat: {str(e)}")
            db.rollback()
            raise
