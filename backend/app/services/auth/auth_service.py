from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.database import User
from app.core.config import settings
from app.core.exceptions import DatabaseError
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def get_user(self, db: Session, username: str) -> Optional[User]:
        try:
            return db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"获取用户时出错: {str(e)}")
            raise DatabaseError("获取用户信息失败")

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        try:
            user = self.get_user(db, username)
            if not user:
                return None
            if not self.verify_password(password, user.hashed_password):
                return None
            return user
        except Exception as e:
            logger.error(f"认证用户时出错: {str(e)}")
            raise DatabaseError("认证失败")

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created access token for user: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"创建访问令牌时出错: {str(e)}")
            raise DatabaseError("创建访问令牌失败")

    def register_user(self, db: Session, username: str, password: str) -> Optional[User]:
        try:
            hashed_password = self.get_password_hash(password)
            user = User(username=username, hashed_password=hashed_password)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"注册用户时出错: {str(e)}")
            raise DatabaseError("注册用户失败")
