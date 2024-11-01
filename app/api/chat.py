from fastapi import APIRouter, Depends, HTTPException, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, get_async_session
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import select
from typing import List
from datetime import datetime
from app.models.message import Message
from app.models.user import User
from app.services.chat_service import ChatService
from app.utils.auth import get_current_user
from app.utils.database import get_db

router = APIRouter()

@router.post("/{chat_id}/messages/stream")
async def create_message_stream(
    chat_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. 创建用户消息记录
        user_message = Message(
            chat_id=chat_id,
            role="user",
            content=message.content,
            is_complete=True  # 用户消息总是完整的
        )
        db.add(user_message)
        await db.commit()

        # 2. 创建助手消息记录（初始为空）
        assistant_message = Message(
            chat_id=chat_id,
            role="assistant",
            content="",  # 初始内容为空
            is_complete=False  # 标记为未完成
        )
        db.add(assistant_message)
        await db.commit()

        # 3. 开始流式响应
        async def event_generator():
            try:
                current_content = ""
                async for chunk in chat_service.stream_chat(message.content, chat_id):
                    if chunk:
                        current_content += chunk
                        # 更新数据库中的消息内容
                        assistant_message.content = current_content
                        await db.commit()
                        # 返回块给前端（用于显示打字动画）
                        yield f"data: {chunk}\n\n"

                # 4. 标记消息完成
                assistant_message.is_complete = True
                await db.commit()

            except Exception as e:
                logger.error(f"Stream error: {str(e)}")
                # 确保在发生错误时也标记消息状态
                assistant_message.is_complete = True
                await db.commit()
                raise

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )

    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="创建消息失败"
        )

# 获取消息列表的接口
@router.get("/{chat_id}/messages")
async def get_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # 获取所有消息，包括 is_complete 状态
        query = select(Message).where(Message.chat_id == chat_id)
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "is_complete": msg.is_complete,  # 添加完成状态
                "created_at": msg.created_at
            }
            for msg in messages
        ]

    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="获取消息失败"
        ) 