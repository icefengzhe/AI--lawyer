from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    # API配置
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "AI Lawyer"
    
    # 安全配置
    SECRET_KEY: str = os.getenv('SECRET_KEY', "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # 数据库配置
    DATABASE_URL: str = os.getenv('DATABASE_URL', "sqlite:///./ai_lawyer.db")
    
    # AI模型配置
    DASHSCOPE_API_KEY: str = os.getenv('DASHSCOPE_API_KEY', "your-api-key-here")
    VECTOR_DB_PATH: str = os.getenv('VECTOR_DB_PATH', "./vector_db")
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL: int = 30  # 30秒
    WS_TIMEOUT: int = 60  # 60秒
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        case_sensitive = True

settings = Settings()

if __name__ == '__main__':
    print(settings.DASHSCOPE_API_KEY)
