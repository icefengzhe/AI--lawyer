from typing import List, Optional
import numpy as np
from langchain_community.vectorstores.chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, Docx2txtLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
import os
from pathlib import Path
from backend.core.config import settings
from backend.core.logger import logger
from backend.services.embeddings import qwen_embeddings
from backend.models.file import File
import logging

class VectorStore:
    def __init__(self):
        self.embeddings = qwen_embeddings  # 使用通义千问 Embeddings
        # 将 Path 对象转换为字符串
        self.persist_directory = str(settings.VECTOR_STORE_PATH)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # 调整块大小以适应中文
            chunk_overlap=50,
            length_function=len,
        )
        self.logger = logging.getLogger(__name__)
        
        # 确保存储目录存在
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
        
    def get_user_collection(self, user_id: int) -> Chroma:
        """获取用户专属的向量集合"""
        collection_name = f"user_{user_id}_docs"
        persist_directory = os.path.join(self.persist_directory, collection_name)
        
        # 确保用户的向量存储目录存在
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
            
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
    
    async def add_file(self, file_path: str, user_id: int, metadata: dict) -> bool:
        """添加文件到向量数据库"""
        try:
            # 根据文件类型选择加载器
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith('.docx'):
                loader = Docx2txtLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding='utf-8')
            
            # 加载文档
            documents = loader.load()
            
            # 分割文本
            texts = self.text_splitter.split_documents(documents)
            
            # 添加用户ID到元数据
            for text in texts:
                text.metadata.update({
                    "user_id": user_id,
                    **metadata
                })
            
            # 获取用户的向量集合
            vectorstore = self.get_user_collection(user_id)
            
            # 添加文档
            vectorstore.add_documents(texts)
            vectorstore.persist() # 持久化存储
            
            logger.info(f"文件已添加到向量数据库: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"添加文件到向量数据库失败: {str(e)}", exc_info=True)
            return False
    
    async def search(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        metadata_filter: dict = None
    ) -> List[dict]:
        """搜索相关文档片段"""
        try:
            # 获取用户的向量集合
            vectorstore = self.get_user_collection(user_id)
            
            # 添加用户ID过滤
            filter_dict = {"user_id": user_id}
            if metadata_filter:
                filter_dict.update(metadata_filter)
            
            # 执行搜索
            results = vectorstore.similarity_search_with_score(
                query,
                k=top_k,
                filter=filter_dict
            )
            
            # 格式化结果
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"向量搜索失败: {str(e)}", exc_info=True)
            return []
    
    async def delete_file(self, file_id: int, user_id: int) -> bool:
        """删除文件相关的向量"""
        try:
            vectorstore = self.get_user_collection(user_id)
            
            # 先查询要删除的文档
            results = vectorstore._collection.get(
                where={"file_id": file_id}
            )
            
            if results and results['ids']:
                # 使用文档ID删除
                vectorstore._collection.delete(
                    ids=results['ids']
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"删除向量存储中的文件失败: {str(e)}")
            raise

vector_store = VectorStore()