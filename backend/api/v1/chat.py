from typing import Any, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Body, WebSocket, WebSocketDisconnect, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend import crud, schemas
from backend.api import deps
from backend.services.chat import get_chat_response
from backend.core.logger import logger
from backend.models import Chat, Message, User

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
    logger.debug(f"Retrieved messages from DB: {messages}")
    return messages

@router.websocket("/{chat_id}/messages/stream")
async def create_message_stream(
    websocket: WebSocket,
    chat_id: int,
    db: Session = Depends(deps.get_db),
):
    """通过WebSocket发送消息并获取流式响应"""
    logger.info(f"开始建立WebSocket连接 - chat_id: {chat_id}")
    try:
        await websocket.accept()
        logger.info(f"WebSocket连接已接受 - chat_id: {chat_id}")
        
        # 先进行用户认证
        try:
            current_user = await deps.get_current_ws_user(websocket=websocket, db=db)
            logger.info(f"WebSocket用户认证成功 - chat_id: {chat_id}, user_id: {current_user.id}")
        except HTTPException as e:
            logger.error(f"WebSocket用户认证失败 - chat_id: {chat_id}, error: {e.detail}")
            await websocket.send_json({"error": e.detail})
            await websocket.close()
            return
            
        # 验证chat权限
        chat = crud.chat.get(db=db, id=chat_id)
        if not chat or chat.user_id != current_user.id:
            logger.error(f"WebSocket对话权限验证失败 - chat_id: {chat_id}, user_id: {current_user.id}")
            await websocket.send_json({"error": "对话不存在"})
            await websocket.close()
            return

        logger.info(f"WebSocket对话权限验证通过 - chat_id: {chat_id}, user_id: {current_user.id}")

        while True:
            # 接收用户消息
            message_data = await websocket.receive_json()
            message_content = message_data.get("content")
            
            if not message_content:
                logger.warning(f"收到空消息 - chat_id: {chat_id}")
                continue
                
            logger.info(f"收到WebSocket消息 - chat_id: {chat_id}, user_id: {current_user.id}")
            
            # 获取历史消息
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in crud.chat.get_messages(db=db, chat_id=chat_id)
            ]
            logger.info(f"获取到历史消息 - chat_id: {chat_id}, 数量: {len(history)}")
            
            # 保存用户消息
            user_message = crud.chat.add_message(
                db=db,
                chat_id=chat_id,
                message=schemas.MessageCreate(content=message_content, role="user")
            )
            logger.info(f"用户消息已保存 - chat_id: {chat_id}, message_id: {user_message.id}")
            
            # 生成响应
            response_text = ""
            try:
                logger.info(f"开始生成AI响应 - chat_id: {chat_id}")
                async for token, new_title, need_file in get_chat_response(
                    message=message_content,
                    current_title=chat.title, 
                    history=history,
                    user_id=current_user.id
                ):
                    response_text += token
                    # 发送token
                    await websocket.send_json({
                        "type": "token",
                        "content": token
                    })
                    
                    # 发送标题更新
                    if new_title:
                        crud.chat.update(db=db, id=chat_id, obj_in={"title": new_title})
                        logger.info(f"对话标题已更新 - chat_id: {chat_id}, new_title: {new_title}")
                        await websocket.send_json({
                            "type": "title",
                            "content": new_title
                        })
                    
                    # 发送文件上传事件
                    if need_file:
                        logger.info(f"需要文件上传 - chat_id: {chat_id}")
                        await websocket.send_json({
                            "type": "need_file",
                            "content": True
                        })
                
                logger.info(f"AI响应生成完成 - chat_id: {chat_id}")
                
                # 保存完整的AI响应
                ai_message = crud.chat.add_message(
                    db=db,
                    chat_id=chat_id,
                    message=schemas.MessageCreate(content=response_text, role="assistant")
                )

                logger.info(f"AI响应已保存 - chat_id: {chat_id}, message_id: {ai_message.id}")
                
            except Exception as e:
                logger.error(f"WebSocket响应生成失败 - chat_id: {chat_id}, error: {str(e)}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "content": "抱歉，处理消息时出现错误。"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开 - chat_id: {chat_id}")
    except Exception as e:
        logger.error(f"WebSocket处理异常 - chat_id: {chat_id}, error: {str(e)}", exc_info=True)
        try:
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close()
        except Exception:
            pass

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