from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.api import deps
from backend.core.config import settings
from backend.services.file import FileService
from backend import crud
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
file_service = FileService()

@router.post("/upload", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """上传文件"""
    logger.info(f"收到文件上传请求: filename={file.filename}, type={file.content_type}, user_id={current_user.id}")
    
    # 验证文件类型
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        logger.warning(f"不支持的文件类型: {file.content_type}")
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    try:
        # 保存文件
        db_file = await file_service.save_file(file, current_user.id, db)
        logger.info(f"文件上传成功: id={db_file.id}, filename={db_file.filename}")
        
        return {
            "id": db_file.id,
            "filename": db_file.filename,
            "file_type": db_file.file_type,
            "file_size": db_file.file_size,
            "created_at": db_file.created_at
        }
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[dict])
def get_files(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """获取用户的文件列表"""
    logger.info(f"获取文件列表: user_id={current_user.id}")
    files = crud.file.get_multi_by_user(db, user_id=current_user.id)
    logger.info(f"文件列表获取成功: count={len(files)}")
    return [
        {
            "id": file.id,
            "filename": file.filename,
            "file_type": file.file_type,
            "file_size": file.file_size,
            "created_at": file.created_at
        }
        for file in files
    ]

@router.delete("/{file_id}", status_code=200)
def delete_file(
    file_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """删除文件"""
    logger.info(f"删除文件请求: file_id={file_id}, user_id={current_user.id}")
    
    file = crud.file.get(db, id=file_id)
    if not file or file.user_id != current_user.id:
        logger.warning(f"文件不存在或无权限: file_id={file_id}")
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        file_service.delete_file(file)
        crud.file.remove(db, id=file_id)
        logger.info(f"文件删除成功: file_id={file_id}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"文件删除失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 