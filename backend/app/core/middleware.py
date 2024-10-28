from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import SessionLocal
import logging
import time
from typing import Callable
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request.state.db = SessionLocal()
        try:
            response = await call_next(request)
            return response
        finally:
            request.state.db.close()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # 记录响应时间和状态码
            process_time = time.time() - start_time
            logger.info(
                f"Response: status={response.status_code} "
                f"completed_in={process_time:.3f}s"
            )
            
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
