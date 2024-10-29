from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend import crud, schemas
from backend.api import deps
from backend.services.chat import get_chat_response
from backend.core.logger import logger
from backend.models.chat import Chat

router = APIRouter()

class MessageRequest(BaseModel):
    content: str

@router.post("/create", response_model=schemas.Chat)
async def create_chat(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> Any:
    """
    创建新对话
    """
    chat = crud.chat.create_with_owner(
        db=db, obj_in=schemas.ChatCreate(), user_id=current_user.id
    )
    return chat

@router.get("/history", response_model=List[schemas.Chat])
async def read_chats(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    获取对话历史
    """
    chats = crud.chat.get_user_chats(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return chats

@router.get("/{chat_id}/messages", response_model=List[schemas.Message])
async def read_messages(
    chat_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    获取对话消息
    """
    chat = crud.chat.get(db=db, id=chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对话不存在")
    messages = crud.chat.get_messages(db=db, chat_id=chat_id, skip=skip, limit=limit)
    return messages

@router.post("/{chat_id}/messages/stream")
async def create_message_stream(
    *,
    chat_id: int,
    message: MessageRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """发送消息并获取流式响应"""
    logger.info(f"收到消息请求 - chat_id: {chat_id}, user_id: {current_user.id}")
    
    # 获取对话及其标题
    chat = crud.chat.get(db=db, id=chat_id)
    if not chat or chat.user_id != current_user.id:
        logger.error(f"对话不存在或无权限 - chat_id: {chat_id}")
        raise HTTPException(status_code=404, detail="对话不存在")
    
    current_title = chat.title
    
    # 获取历史消息
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in crud.chat.get_messages(db=db, chat_id=chat_id)
    ]
    logger.info(f"获取到历史消息 - 数量: {len(history)}")
    
    # 保存用户消息
    user_message = crud.chat.add_message(
        db=db, 
        chat_id=chat_id, 
        message=schemas.MessageCreate(content=message.content, role="user")
    )
    logger.info("用户消息已保存")
    
    async def response_stream():
        logger.info("开始生成流式响应")
        response_text = ""
        try:
            async for token, new_title in get_chat_response(
                message=message.content,
                current_title=current_title,
                history=history
            ):
                response_text += token
                yield f"data: {token}\n\n"
                
                # 如果有新标题，更新对话标题并发送事件
                if new_title and new_title != current_title:  # 只在标题变化时更新
                    try:
                        # 重新获取chat对象并更新标题
                        chat_obj = db.query(Chat).filter(Chat.id == chat_id).first()
                        if chat_obj:
                            chat_obj.title = new_title
                            db.add(chat_obj)
                            db.commit()
                            logger.info(f"对话标题已更新: {new_title}")
                            yield f"event: title\ndata: {new_title}\n\n"
                    except Exception as e:
                        logger.error(f"更新标题失败: {str(e)}", exc_info=True)
            
            logger.info("AI响应生成完成")
            
            # 保存AI响应
            ai_message = crud.chat.add_message(
                db=db, 
                chat_id=chat_id, 
                message=schemas.MessageCreate(content=response_text, role="assistant")
            )
            logger.info("AI响应已保存")
                
        except Exception as e:
            logger.error(f"流式响应生成失败: {str(e)}", exc_info=True)
            yield f"data: 抱歉，处理消息时出现错误。\n\n"
    
    return StreamingResponse(
        response_stream(),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )

@router.delete("/{chat_id}", response_model=schemas.Chat)
async def delete_chat(
    chat_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    删除对话
    """
    chat = crud.chat.get(db=db, id=chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对话不存在")
    chat = crud.chat.remove(db=db, id=chat_id)
    return chat

@router.get("/{chat_id}", response_model=schemas.Chat)
async def read_chat(
    chat_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    获取单个对话
    """
    chat = crud.chat.get(db=db, id=chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对话不存在")
    return chat