from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from backend.api.v1 import api_router
from backend.core.config import settings
from backend.db.base import Base  # 这会导入所有模型
from backend.db.database import engine
from backend.core.logger import logger

# 初始化日志
logger.info("=== 启动AI Lawyer服务 ===")

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 挂载静态文件
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

logger.info("服务初始化完成")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)