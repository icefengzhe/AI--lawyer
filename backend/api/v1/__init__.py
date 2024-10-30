from fastapi import APIRouter
from backend.api.v1 import chat, auth, file

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(file.router, prefix="/files", tags=["files"])