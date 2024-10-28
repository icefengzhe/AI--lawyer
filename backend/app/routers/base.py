from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.database import User
from app.core.exceptions import AppException, DatabaseError, NotFoundError
import logging
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar('T')

class BaseRouter(Generic[T]):
    def __init__(self, prefix: str, tags: list[str]):
        self.router = APIRouter()
        self.prefix = prefix
        self.tags = tags
        self.setup_routes()

    def setup_routes(self):
        """子类需要实现此方法来设置路由"""
        raise NotImplementedError

    async def handle_request(self, operation: str, callback: callable, *args, **kwargs) -> Any:
        """通用请求处理器"""
        try:
            return await callback(*args, **kwargs)
        except AppException as e:
            logger.warning(f"{operation} failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {operation}: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to {operation}")

    def get_router(self) -> APIRouter:
        """获取配置好的路由器"""
        router = APIRouter(prefix=self.prefix, tags=self.tags)
        for route in self.router.routes:
            router.routes.append(route)
        return router
