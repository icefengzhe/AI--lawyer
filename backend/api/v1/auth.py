from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.api import deps
from backend.core.config import settings
from backend.core.security import create_access_token

router = APIRouter()

@router.post("/register", response_model=schemas.Token)
async def register(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在",
        )
    user = crud.user.create(db, obj_in=user_in)
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            str(user.id), expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    OAuth2 compatible token login
    """
    try:
        user = crud.user.authenticate(
            db, username=form_data.username, password=form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=400, detail="用户名或密码错误"
            )
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        return {
            "access_token": create_access_token(
                str(user.id), expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user = Depends(deps.get_current_user)
) -> Any:
    """
    Get current user.
    """
    return current_user