from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.core.log_config import setup_logging
from app.routers.auth.router import auth_router
from app.routers.chat.router import chat_router
from app.database import init_db
import logging

# 设置日志
logger = setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AI法律助手API",
        version="1.0.0"
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    # 添加Gzip压缩，使用正确的参数
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000  # 只压缩大于1KB的响应
    )
    
    # 注册路由
    app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
    app.include_router(chat_router.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up application...")
        init_db()
        
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down application...")
        
    return app

app = create_app()

# 添加调试日志
logger.info(f"Available routes:")
for route in app.routes:
    if hasattr(route, 'methods'):
        logger.info(f"{route.methods} {route.path}")
    else:
        logger.info(f"WebSocket {route.path}")
