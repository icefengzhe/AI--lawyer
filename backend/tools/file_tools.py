from typing import Tuple, Optional, Any, List
from langchain_community.chat_models import ChatTongyi
from langchain.schema import HumanMessage
from langchain.tools import BaseTool
from langchain.agents import Tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredImageLoader
)
from langchain.embeddings import DashScopeEmbeddings
from langchain.vectorstores import FAISS
from backend.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

class FileNeedAnalyzer:
    """分析用户是否需要上传文件的工具"""
    
    def __init__(self, model: Optional[ChatTongyi] = None):
        self.model = model or ChatTongyi(
            model_name="qwen-max",
            dashscope_api_key=settings.DASHSCOPE_API_KEY,
            temperature=0.1
        )
        
        self.analyze_prompt = """请分析用户的问题是否需要上传文件来辅助回答。
只需返回"true"或"false"，不需要其他解释。

以下情况需要返回"true"：
1. 用户提到具体的文件、合同、协议等
2. 用户需要分析具体的文档内容
3. 用户需要查看图片或扫描件
4. 用户提到需要审查或审阅某些材料

以下情况返回"false"：
1. 用户询问一般性法律问题
2. 用户寻求法律建议但没有具体文件
3. 用户咨询法律概念或程序
4. 用户进行假设性讨论

用户问题：{question}

请直接返回："""

    async def analyze_file_need(self, question: str) -> bool:
        """分析用户问题是否需要上传文件"""
        try:
            messages = [
                HumanMessage(content=self.analyze_prompt.format(question=question))
            ]
            
            response = await self.model.agenerate([messages])
            result = response.generations[0][0].text.strip().lower()
            
            return result == "true"
                
        except Exception as e:
            logger.error(f"Error analyzing file need: {str(e)}")
            return False

class FileNeedAnalyzerTool(BaseTool):
    name: str = "file_need_analyzer"
    description: str = "Analyze if user needs to upload files based on their question"
    analyzer: FileNeedAnalyzer
    return_direct: bool = True

    def __init__(self, analyzer: Optional[FileNeedAnalyzer] = None):
        super().__init__()
        self.analyzer = analyzer or FileNeedAnalyzer()

    def _run(self, query: str) -> str:
        raise NotImplementedError("This tool only supports async execution")

    async def _arun(self, query: str) -> str:
        try:
            need_file = await self.analyzer.analyze_file_need(query)
            return str(need_file).lower()
        except Exception as e:
            logger.error(f"Error running file need analyzer tool: {str(e)}")
            return "false"

class FileProcessor:
    def __init__(self, embeddings_model=None):
        self.embeddings = embeddings_model or DashScopeEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = None
        self.loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
            '.jpg': UnstructuredImageLoader,
            '.png': UnstructuredImageLoader,
            '.jpeg': UnstructuredImageLoader,
        }

    def process_file(self, file_path: str) -> List[str]:
        """处理单个文件"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in self.loaders:
                raise ValueError(f"Unsupported file type: {ext}")

            loader = self.loaders[ext](file_path)
            documents = loader.load()
            texts = self.text_splitter.split_documents(documents)
            
            # 更新向量存储
            if not self.vector_store:
                self.vector_store = FAISS.from_documents(texts, self.embeddings)
            else:
                self.vector_store.add_documents(texts)
            
            return [doc.page_content for doc in texts]
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

    def search_similar(self, query: str, k: int = 3) -> List[str]:
        """搜索相似内容"""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"Error searching similar content: {str(e)}")
            return []