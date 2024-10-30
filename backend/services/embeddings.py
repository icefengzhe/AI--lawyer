from typing import List
import dashscope
from langchain.embeddings.base import Embeddings
from backend.core.config import settings

class QwenEmbeddings(Embeddings):
    """通义千问 Embedding 模型包装器"""
    
    def __init__(self, model: str = "text-embedding-v1"):
        self.model = model
        dashscope.api_key = settings.DASHSCOPE_API_KEY
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成文档的嵌入向量"""
        try:
            response = dashscope.TextEmbedding.call(
                model=self.model,
                input=texts
            )
            
            if response.status_code == 200:
                return [item['embedding'] for item in response.output['embeddings']]
            else:
                raise Exception(f"Embedding generation failed: {response.message}")
                
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    def embed_query(self, text: str) -> List[float]:
        """生成查询的嵌入向量"""
        try:
            response = dashscope.TextEmbedding.call(
                model=self.model,
                input=[text]
            )
            
            if response.status_code == 200:
                return response.output['embeddings'][0]['embedding']
            else:
                raise Exception(f"Embedding generation failed: {response.message}")
                
        except Exception as e:
            raise Exception(f"Error generating query embedding: {str(e)}")

qwen_embeddings = QwenEmbeddings() 