from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 基本设置
    PROJECT_NAME: str = "AI Lawyer"
    API_V1_STR: str = "/api/v1"
    
    # 安全设置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # API设置
    DASHSCOPE_API_KEY: str
    
    # 数据库设置
    DATABASE_URL: str = "sqlite:///./ai_lawyer.db"
    SQL_ECHO: bool = False
    
    # 向量数据库设置
    VECTOR_DB_PATH: str = "./vector_store"
    
    # 日志设置
    LOG_LEVEL: str = "INFO"
    
    # CORS设置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings() 