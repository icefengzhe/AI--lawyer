from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, WebSocket, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import Annotated

from backend.core.config import settings
from backend.crud import crud_user
from backend.db.database import SessionLocal, get_db
from backend.schemas.token import TokenPayload
from backend.models import User
from backend.core.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_ws_token(websocket: WebSocket) -> str:
    """获取WebSocket连接中的token"""
    logger.debug(f"WebSocket query params: {websocket.query_params}")
    logger.debug(f"WebSocket headers: {websocket.headers}")
    
    # 首先尝试从URL参数获取token
    token = websocket.query_params.get("token")
    if token:
        logger.debug("从URL参数获取到token")
        # 如果token以Bearer开头，去掉Bearer前缀
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        return token
        
    # 如果URL参数中没有token，尝试从headers获取
    auth = websocket.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        logger.error("未找到有效的认证token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证token"
        )
    
    token = auth.split(" ")[1]
    logger.debug("从headers获取到token")
    return token

async def get_current_ws_user(
    websocket: WebSocket,
    db: Session = Depends(get_db),
) -> User:
    """WebSocket认证依赖"""
    try:
        token = await get_ws_token(websocket)
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证token"
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证token"
        )
    
    user = crud_user.get(db, id=int(token_data.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    return user

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """HTTP请求认证依赖"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except (jwt.JWTError, ValidationError):
        raise credentials_exception
    
    user = crud_user.get(db, id=int(token_data.sub))
    if not user:
        raise credentials_exception
    return user