from app.services.chat.base import BaseChatService
from sqlalchemy.orm import Session
from app.core.exceptions import DatabaseError
from app.models.database import Message, Chat
from langchain.chat_models import ChatTongyi
from langchain.schema import HumanMessage, AIMessage
from app.core.config import settings
import logging
import asyncio
from typing import AsyncGenerator, List

logger = logging.getLogger(__name__)

class AIChatService(BaseChatService):
    def __init__(self):
        super().__init__()
        self._current_response = []
        self.setup_ai_components()

    def setup_ai_components(self):
        """初始化AI组件"""
        try:
            self.llm = ChatTongyi(
                api_key=settings.DASHSCOPE_API_KEY,
                model="qwen-turbo",
                temperature=0.7
            )
            logger.info("AI components initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up AI components: {str(e)}")
            raise RuntimeError("Failed to initialize AI components")

    async def process_message(self, db: Session, user_id: int, chat_id: int, message: str) -> str:
        """处理用户消息并生成AI响应"""
        try:
            # 保存用户消息
            user_message = Message(
                content=message,
                role="user",
                chat_id=chat_id
            )
            db.add(user_message)
            db.commit()
            db.refresh(user_message)

            # 获取聊天历史
            chat_history = self.get_chat_history(db, chat_id)
            
            # 使用AI生成响应
            result = await self.llm.apredict(message)
            
            # 保存AI响应
            ai_message = Message(
                content=result,
                role="ai",
                chat_id=chat_id
            )
            db.add(ai_message)
            db.commit()
            db.refresh(ai_message)
            
            return result
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            db.rollback()
            raise DatabaseError("Failed to process message")

    def get_chat_history(self, db: Session, chat_id: int) -> List[tuple]:
        """获取用于AI的聊天历史格式"""
        messages = db.query(Message)\
            .filter(Message.chat_id == chat_id)\
            .order_by(Message.created_at.asc()).all()
        return [(msg.content, msg.role) for msg in messages]

    async def generate_chat_title(self, db: Session, chat_id: int) -> str:
        """使用AI生成聊天标题"""
        try:
            messages = db.query(Message)\
                .filter(Message.chat_id == chat_id)\
                .order_by(Message.created_at.asc()).limit(3).all()
            
            if not messages:
                return "新对话"

            # 构建标题生成提示
            chat_content = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
            prompt = f"请为以下对话生成一个简短的标题（不超过10个字）:\n\n{chat_content}"
            
            # 使用AI生成标题
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            title = str(response.content).strip()
            
            # 更新聊天标题
            chat = db.query(Chat).filter(Chat.id == chat_id).first()
            if chat:
                chat.title = title
                db.commit()
            
            return title
        except Exception as e:
            logger.error(f"Error generating chat title: {str(e)}")
            return "新对话"

    async def stream_response(self, db: Session, user_id: int, chat_id: int, message: str) -> AsyncGenerator[str, None]:
        """流式生成AI响应"""
        try:
            self._current_response = []
            
            # 获取聊天历史
            history = self.get_chat_history(db, chat_id)
            messages = []
            for content, role in history[-5:]:  # 只使用最近5条消息作为上下文
                if role == "user":
                    messages.append(HumanMessage(content=content))
                else:
                    messages.append(AIMessage(content=content))
            
            # 添加当前消息
            messages.append(HumanMessage(content=message))
            
            # 使用AI生成响应
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, 'content'):
                    token = str(chunk.content)
                    self._current_response.append(token)
                    yield token
                await asyncio.sleep(0.05)  # 添加小延迟使流式效果更自然
                
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            raise DatabaseError(f"Failed to stream response: {str(e)}")

    async def save_response(self, db: Session, chat_id: int) -> Message:
        """保存完整的AI响应"""
        try:
            complete_response = ''.join(self._current_response).strip()
            
            ai_message = Message(
                content=complete_response,
                role="ai",
                chat_id=chat_id
            )
            db.add(ai_message)
            db.commit()
            db.refresh(ai_message)
            
            # 清空当前响应
            self._current_response = []
            
            return ai_message
        except Exception as e:
            logger.error(f"Error saving response: {str(e)}")
            db.rollback()
            raise DatabaseError("Failed to save response")
