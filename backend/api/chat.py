from fastapi import APIRouter
from backend.api.v1 import chat

# 创建新的路由器
router = APIRouter()

# 复用 v1 版本的所有路由
router.include_router(chat.router, prefix="")