from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.auth import create_access_token, get_current_user
from backend.crud.user import crud_user
from backend.schemas.token import Token
from backend.schemas.user import UserCreate, User

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new user.
    """
    user = crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在",
        )
    user = crud_user.create(db, obj_in=user_in)
    return {
        "access_token": create_access_token(str(user.id)),
        "token_type": "bearer",
    }

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login
    """
    user = crud_user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="用户名或密码错误"
        )
    return {
        "access_token": create_access_token(str(user.id)),
        "token_type": "bearer",
    }

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user.
    """
    return current_user 