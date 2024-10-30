from fastapi import APIRouter
from backend.api.v1 import chat, auth, file
from backend.api.file import file_router

api_router = APIRouter()

# 添加各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(file_router, prefix="/files", tags=["files"]) 