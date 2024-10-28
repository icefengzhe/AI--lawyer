from fastapi import APIRouter, Depends, WebSocket, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_current_user_ws
from app.database import get_db
from app.models.database import User, Chat, Message
from app.services.chat.ai_chat import AIChatService
from app.core.exceptions import NotFoundError
from .schemas import ChatMessage, ChatResponse, ChatHistoryItem
import logging
from typing import List
from starlette.websockets import WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

# 移除路由前缀，让它在main.py中配置
router = APIRouter()
chat_service = AIChatService()

@router.get("/chats", response_model=List[ChatHistoryItem])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的聊天历史"""
    try:
        chats = db.query(Chat).filter(
            Chat.user_id == current_user.id
        ).order_by(Chat.created_at.desc()).all()
        
        return [{"id": chat.id, "title": chat.title} for chat in chats]
    except Exception as e:
        logger.error(f"获取聊天历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat history"
        )

@router.get("/chats/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个聊天的详细信息"""
    try:
        chat = db.query(Chat).filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        ).first()
        
        if not chat:
            raise NotFoundError(f"Chat {chat_id} not found")
            
        messages = db.query(Message).filter(
            Message.chat_id == chat_id
        ).order_by(Message.created_at.asc()).all()
        
        return {
            "id": chat.id,
            "title": chat.title,
            "messages": [
                {
                    "content": msg.content,
                    "role": msg.role,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"获取聊天详细信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat"
        )

@router.post("/chats", response_model=ChatResponse)
async def create_chat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新聊天"""
    try:
        chat = Chat(user_id=current_user.id, title="新对话")
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return {
            "id": chat.id,
            "title": chat.title,
            "messages": []
        }
    except Exception as e:
        logger.error(f"创建聊天失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat"
        )

@router.delete("/chats/{chat_id}")
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除聊天"""
    logger.info(f"User {current_user.id} attempting to delete chat {chat_id}")
    try:
        success = chat_service.delete_chat(db, chat_id, current_user.id)
        if not success:
            logger.warning(f"Chat {chat_id} not found or not owned by user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found or unauthorized"
            )

        logger.info(f"Successfully deleted chat {chat_id}")
        return {"message": "Chat deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat {chat_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat"
        )

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    await websocket.accept()
    try:
        user = await get_current_user_ws(token, db)
        if not user:
            await websocket.close(code=4001, reason="Invalid authentication token")
            return

        logger.info(f"User {user.username} connected to WebSocket")
        chat_service = AIChatService()

        while True:
            try:
                data = await websocket.receive_json()
                chat_id = data.get('chat_id')
                message = data.get('message')

                if not all([chat_id, message]):
                    await websocket.send_json({"error": "Missing required parameters"})
                    continue

                # 保存用户消息
                user_message = Message(content=message, role="user", chat_id=chat_id)
                db.add(user_message)
                db.commit()
                db.refresh(user_message)

                # 发送用户消息确认，确保时间格式正确
                await websocket.send_json({
                    "type": "message",
                    "content": message,
                    "role": "user",
                    "timestamp": user_message.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                })

                # 生成AI响应
                async for token in chat_service.stream_response(db, user.id, chat_id, message):
                    await websocket.send_json({
                        "type": "token",
                        "content": token
                    })

                # 保存AI响应
                ai_message = await chat_service.save_response(db, chat_id)

                # 发送完成标记，确保时间格式正确
                await websocket.send_json({
                    "type": "done",
                    "timestamp": ai_message.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                })

                # 生成并更新聊天标题
                title = await chat_service.generate_chat_title(db, chat_id)
                if title:
                    await websocket.send_json({
                        "type": "title_update",
                        "chat_id": chat_id,
                        "title": title
                    })

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({"error": str(e)})

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=4000, reason="Internal server error")

class ChatRouter:
    def __init__(self):
        self.router = router

chat_router = ChatRouter()
