from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # 仅用于SQLite
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """依赖注入函数，用于FastAPI路由"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def init_db(force: bool = False):
    """初始化数据库"""
    try:
        if force:
            # 删除数据库文件（如果存在）
            db_path = settings.DATABASE_URL.replace('sqlite:///', '')
            if os.path.exists(db_path):
                os.remove(db_path)
                logger.info(f"Removed existing database file: {db_path}")

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("Created all database tables")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

