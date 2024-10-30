from typing import List
from pydantic_settings import BaseSettings
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # 基本设置
    PROJECT_NAME: str = "AI Lawyer"
    API_STR: str = "/api"
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
    
    # 文件存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "image/jpeg",
        "image/png",
        "image/gif"
    ]
    
    # 向量数据库存储路径
    VECTOR_STORE_PATH: Path = BASE_DIR / "data" / "vector_store"
    
    def __init__(self):
        super().__init__()
        # 确保向量存储目录存在
        self.VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    class Config:
        env_file = ".env"

    @property
    def UPLOAD_PATH(self) -> Path:
        return Path(self.UPLOAD_DIR).absolute()

settings = Settings() 