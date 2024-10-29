from typing import AsyncGenerator, Optional, Dict, List, Tuple
import logging
from langchain_community.chat_models import ChatTongyi
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from backend.core.config import settings

logger = logging.getLogger("ai_lawyer")

class ChatService:
    """聊天服务"""
    
    def __init__(self):
        logger.info("=== 初始化聊天服务 ===")
        self._init_models()
        self._init_memory()
        self._init_prompts()
    
    def _init_models(self):
        """初始化模型"""
        try:
            logger.info("初始化AI模型: qwen-max")
            logger.debug(f"使用API密钥: {settings.DASHSCOPE_API_KEY[:8]}...")
            
            # 对话模型
            self.chat_model = ChatTongyi(
                model_name="qwen-max",
                dashscope_api_key=settings.DASHSCOPE_API_KEY,
                temperature=0.7,
                streaming=True
            )
            
            # 标题生成模型
            self.title_model = ChatTongyi(
                model_name="qwen-max",
                dashscope_api_key=settings.DASHSCOPE_API_KEY,
                temperature=0.3,
                streaming=False
            )
            logger.info("AI模型初始化完成")
        except Exception as e:
            logger.error(f"AI模型初始化失败: {str(e)}", exc_info=True)
            raise
    
    def _init_memory(self):
        """初始化对话记忆"""
        self.memory = ConversationBufferMemory(return_messages=True)
    
    def _init_prompts(self):
        """初始化提示词"""
        self.system_prompt = SystemMessage(content="""你是一个专业的法律顾问。请根据用户的问题提供专业、准确的法律建议。

请先给出简短的开场语，表达理解和共情。

然后按以下方面展开说明：

1. 分析用户问题涉及的法律问题
2. 提供具体的建议和解决方案
3. 引用相关法律条文和法规
4. 说明需要注意的风险
5. 补充其他重要信息

最后给出简短的结束语，表达鼓励和支持。

请记住：你的建议可能影响用户的重要决策，务必谨慎和专业。""")

    async def generate_title(self, current_title: str, latest_message: str) -> str:
        """生成对话标题"""
        logger.info(f"开始生成标题，当前标题: {current_title}, 最新消息: {latest_message}")
        try:
            prompt = f"""请根据以下信息生成一个新的对话标题：

当前标题：{current_title}
最新问题：{latest_message}

要求：
1. 标题长度不超过15个字
2. 如果最新问题与当前标题主题相关，保持当前标题
3. 如果最新问题引入新的法律领域或主题，生成新标题反映主要内容
4. 使用简洁专业的语言
5. 优先保留法律领域相关的关键词

请直接返回新标题，不要包含其他内容。"""

            messages = [HumanMessage(content=prompt)]
            response = await self.title_model.agenerate([messages])
            title = response.generations[0][0].text.strip()
            logger.info(f"生成新标题: {title}")
            
            # 清理和截断标题
            title = title.replace('"', '').replace("'", '').split('\n')[0].strip()
            if len(title) > 15:
                for i in range(15, -1, -1):
                    if title[i] in '，。；！？,.;!?':
                        title = title[:i]
                        break
                else:
                    title = title[:15]
            
            return title
                
        except Exception as e:
            logger.error(f"生成标题失败: {str(e)}", exc_info=True)
            return latest_message[:15] + ("..." if len(latest_message) > 15 else "")

    async def get_chat_response(self, message: str, current_title: str, history: Optional[List[Dict]] = None) -> AsyncGenerator[Tuple[str, Optional[str]], None]:
        """生成回复，同时返回更新的标题"""
        logger.info("="*50)
        logger.info(f"收到用户消息: {message}")
        logger.info(f"当前标题: {current_title}")
        logger.info(f"历史消息数量: {len(history) if history else 0}")
        
        try:
            # 先生成新标题
            new_title = await self.generate_title(current_title, message)
            logger.info(f"生成新标题: {new_title}")
            
            messages = [self.system_prompt]
            
            if history:
                for msg in history:
                    msg_type = HumanMessage if msg["role"] == "user" else AIMessage
                    messages.append(msg_type(content=msg["content"]))
                    logger.debug(f"历史消息 - {msg['role']}: {msg['content'][:50]}...")
            
            messages.append(HumanMessage(content=message))
            logger.info(f"构建完整消息列表，总数: {len(messages)}")
            
            logger.info("开始调用AI模型...")
            try:
                # 第一个token返回时同时返回新标题
                first_token = True
                async for chunk in self.chat_model.astream(messages):
                    if chunk.content:
                        logger.debug(f"收到流式响应: {chunk.content}")
                        if first_token:
                            yield chunk.content, new_title
                            first_token = False
                        else:
                            yield chunk.content, None
                logger.info("AI响应生成完成")
                    
            except Exception as e:
                logger.error(f"AI模型调用失败: {str(e)}", exc_info=True)
                raise
                
        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}", exc_info=True)
            error_msg = "抱歉，我现在无法回答您的问题。请稍后再试。"
            logger.info(f"返回错误消息: {error_msg}")
            yield error_msg, None

# 创建全局实例
chat_service = ChatService()

# 导出函数
async def get_chat_response(message: str, current_title: str, history: Optional[List[Dict]] = None) -> AsyncGenerator[Tuple[str, Optional[str]], None]:
    """获取AI回复和更新的标题"""
    async for token, title in chat_service.get_chat_response(message, current_title, history):
        yield token, title

__all__ = ["get_chat_response"]