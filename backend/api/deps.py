from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.crud import crud_user
from backend.db.database import SessionLocal, get_db
from backend.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
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