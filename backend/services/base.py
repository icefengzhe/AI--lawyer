from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

class AIService(ABC):
    """AI服务基类"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> AsyncGenerator[str, None]:
        """生成回复"""
        pass
    
    @abstractmethod
    async def generate_title(self, content: str) -> str:
        """生成标题"""
        pass

class AIServiceException(Exception):
    """AI服务异常"""
    pass 