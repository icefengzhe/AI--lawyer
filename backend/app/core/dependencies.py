from fastapi import Depends, Request, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth.auth_service import AuthService
from app.models.database import User
from app.core.exceptions import AuthenticationError
from typing import Generator, Optional
from jose import JWTError, jwt
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def decode_token(token: str) -> dict:
    """统一的token解码函数"""
    try:
        # 移除Bearer前缀（如果存在）
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
            
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise AuthenticationError("Invalid token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_ws(token: str, db: Session) -> Optional[User]:
    """WebSocket专用的用户认证函数"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if not username:
            return None

        user = db.query(User).filter(User.username == username).first()
        return user
    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        return None

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user

def get_db_session(request: Request) -> Generator[Session, None, None]:
    db = request.state.db
    try:
        yield db
    finally:
        db.close()
