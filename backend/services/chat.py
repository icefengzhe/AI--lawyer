from typing import AsyncGenerator, Optional, Dict, List, Tuple
from langchain_community.chat_models import ChatTongyi
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from backend.core.config import settings
from backend.tools.file_tools import FileNeedAnalyzer
from backend.services.vector_store import vector_store
import logging
import dashscope

logger = logging.getLogger("ai_lawyer")


class ChatService:
    """聊天服务"""

    def __init__(self):
        logger.info("=== 初始化聊天服务 ===")
        self._init_models()
        self._init_memory()
        self._init_prompts()
        self.file_analyzer = FileNeedAnalyzer(self.chat_model)

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
        try:
            self.memory = ConversationBufferMemory(return_messages=True)
            logger.info("对话记忆初始化完成")
        except Exception as e:
            logger.error(f"对话记忆初始化失败: {str(e)}")
            raise

    def _init_prompts(self):
        """初始化提示词"""
        self.base_system_prompt = """你是一个专业的法律顾问。请根据用户的问题提供专业、准确的法律建议。

请先给出简短的开场语，表达理解和共情。

然后按以下方面展开说明：

1. 分析用户问题涉及的法律问题
2. 提供具体的建议和解决方案
3. 引用相关法律条文和法规
4. 说明需要注意的风险
5. 补充其他重要信息

要自然流畅表达，注意控制篇幅，最后给出简短的结束语，表达鼓励和支持。

请记住：你的建议可能影响用户的重要决策，务必谨慎和专业。"""
        self.system_prompt = SystemMessage(content=self.base_system_prompt)

    def _init_tools(self):
        """初始化工具"""
        try:
            self.file_processor = FileProcessor()
            self.tools = create_file_tools(self.file_processor)
            
            # 初始化agent
            self.agent = initialize_agent(
                tools=self.tools,
                llm=self.chat_model,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=True,
                memory=self.memory,
                handle_parsing_errors=True
            )
            
            logger.info("工具初始化完成")
        except Exception as e:
            logger.error(f"工具初始化失败: {str(e)}")
            raise

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

    async def get_chat_response(self, message: str, current_title: str, history: Optional[List[Dict]] = None, user_id: Optional[int] = None) -> AsyncGenerator[Tuple[str, Optional[str], bool], None]:
        """生成回复，同时返回更新的标题和是否需要上传文件"""
        logger.info("="*50)
        logger.info(f"收到用户消息: {message}")
        
        try:
            # 分析是否需要上传文件
            need_file = await self.file_analyzer.analyze_file_need(message)
            logger.info(f"是否需要上传文件: {need_file}")
            
            # 生成新标题
            new_title = await self.generate_title(current_title, message)
            
            # 如果提供了user_id，搜索相关文档作为上下文
            system_content = self.base_system_prompt
            if user_id is not None:
                context = await self.get_relevant_context(message, user_id)
                if context:
                    system_content = f"{self.base_system_prompt}\n\n请基于以下参考资料回答问题：\n{context}"
            
            # 生成回复
            messages = [SystemMessage(content=system_content)]
            if history:
                for msg in history:
                    msg_type = HumanMessage if msg["role"] == "user" else AIMessage
                    messages.append(msg_type(content=msg["content"]))
            
            messages.append(HumanMessage(content=message))
            
            # 流式返回响应
            first_token = True
            async for chunk in self.chat_model.astream(messages):
                if chunk.content:
                    if first_token:
                        yield chunk.content, new_title, need_file
                        first_token = False
                    else:
                        yield chunk.content, None, False
                        
        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}", exc_info=True)
            error_msg = "抱歉，我现在无法回答您的问题。请稍后再试。"
            yield error_msg, None, False

    async def get_relevant_context(self, query: str, user_id: int) -> str:
        """获取相关上下文"""
        results = await vector_store.search(query, user_id, top_k=3)
        logger.info(f"搜索结果: {results}")
        if not results:
            return ""
            
        # 将搜索结果组合成上下文
        context = "\n\n".join([
            f"相关文档内容：{result['content']}" 
            for result in results
        ])
        
        return context


# 创建全局实例
chat_service = ChatService()


# 导出函数
async def get_chat_response(
    message: str, 
    current_title: str, 
    history: Optional[List[Dict]] = None,
    user_id: Optional[int] = None
) -> AsyncGenerator[Tuple[str, Optional[str], bool], None]:
    """获取AI回复和更新的标题"""
    async for token, title, need_file in chat_service.get_chat_response(
        message, 
        current_title, 
        history,
        user_id
    ):
        yield token, title, need_file


__all__ = ["get_chat_response"]
