import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from backend.core.config import settings
from backend.models import File
from backend import crud
from backend.db.session import SessionLocal
from backend.services.vector_store import vector_store
from backend.core.logger import logger


class FileService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_PATH
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"初始化文件服务，上传目录: {self.upload_dir}")
    
    async def save_file(self, file: UploadFile, user_id: int, db) -> Optional[File]:
        """保存上传的文件"""
        file_path = None
        try:
            # 创建用户专属目录
            user_dir = self.upload_dir / str(user_id)
            user_dir.mkdir(exist_ok=True)
            logger.info(f"用户目录创建成功: {user_dir}")
            
            # 生成文件路径
            file_path = user_dir / file.filename
            logger.info(f"准备保存文件: {file_path}")
            
            # 保存文件
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"文件保存成功: {file_path}")
            
            # 创建文件记录
            file_size = os.path.getsize(file_path)
            file_data = {
                "user_id": user_id,
                "filename": file.filename,
                "file_path": str(file_path),
                "file_type": file.content_type,
                "file_size": file_size
            }
            db_file = crud.file.create(db, obj_in=file_data)
            logger.info(f"文件记录创建成功: id={db_file.id}, size={file_size}bytes")
            
            # 添加到向量数据库
            metadata = {
                "file_id": db_file.id,
                "filename": file.filename,
                "file_type": file.content_type,
                "source": str(file_path)
            }
            
            await vector_store.add_file(
                file_path=str(file_path),
                user_id=user_id,
                metadata=metadata
            )
            
            return db_file
            
        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}", exc_info=True)
            # 如果保存失败，清理已上传的文件
            if file_path and file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"清理失败文件: {file_path}")
                except Exception as cleanup_error:
                    logger.error(f"清理失败文件出错: {str(cleanup_error)}")
            raise e
    
    async def delete_file(self, file: File) -> bool:
        """删除文件"""
        try:
            # 删除物理文件
            file_path = Path(file.file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"文件删除成功: {file_path}")
            
            # 删除向量数据
            await vector_store.delete_file(
                file_id=file.id,
                user_id=file.user_id
            )
            logger.info(f"向量数据库记录已删除: {file.id}")
            # 如果用户目录为空，也删除目录
            user_dir = file_path.parent
            if user_dir.exists() and not any(user_dir.iterdir()):
                user_dir.rmdir()
                logger.info(f"空目录删除成功: {user_dir}")
            
            return True
                
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}", exc_info=True)
            raise e

async def get_file_list():
    db = SessionLocal()
    try:
        files = db.query(File).all()
        return files
    finally:
        db.close()