from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # JWT设置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # API设置
    DASHSCOPE_API_KEY: str
    
    # 数据库设置
    DATABASE_URL: Optional[str] = "sqlite:///./ai_lawyer.db"
    
    # 向量数据库设置
    VECTOR_DB_PATH: str = "./vector_store"
    
    # 日志设置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings() 