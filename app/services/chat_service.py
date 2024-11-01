from typing import AsyncGenerator
from app.models.message import Message
from app.core.config import settings
import openai
import asyncio

class ChatService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        
    async def stream_chat(self, message: str, chat_id: int) -> AsyncGenerator[str, None]:
        try:
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": message}],
                stream=True,
                temperature=0.7,
            )
            
            async for chunk in response:
                if chunk and chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            raise 