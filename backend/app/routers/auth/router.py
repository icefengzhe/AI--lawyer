from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.services.auth.auth_service import AuthService
from app.core.exceptions import AuthenticationError
from app.models.database import User
from .schemas import TokenResponse, UserCreate
from fastapi.security import OAuth2PasswordRequestForm
import logging

logger = logging.getLogger(__name__)

# 创建路由器，不要在这里添加前缀
router = APIRouter()
auth_service = AuthService()

@router.post("/token", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        user = auth_service.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"Login failed: Invalid credentials for user {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        access_token = auth_service.create_access_token({"sub": user.username})
        logger.info(f"Login successful for user: {user.username}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/register")
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Registration attempt for username: {user.username}")
    try:
        existing_user = auth_service.get_user(db, user.username)
        if existing_user:
            logger.warning(f"Registration failed: Username {user.username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

        new_user = auth_service.register_user(db, user.username, user.password)
        if not new_user:
            logger.error(f"Registration failed: Could not create user {user.username}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="注册失败"
            )

        logger.info(f"Registration successful for user: {user.username}")
        return {"message": "注册成功", "user_id": new_user.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

class AuthRouter:
    def __init__(self):
        self.router = router

auth_router = AuthRouter()
