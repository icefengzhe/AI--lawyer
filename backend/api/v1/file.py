from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from backend.services.file import FileService, get_file_list
from backend.api import deps
from sqlalchemy.orm import Session
from backend.models import File as FileModel
from backend.services.vector_store import vector_store
from backend.core.logger import logger
router = APIRouter()
file_service = FileService()

@router.get("/list")
async def list_files(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """获取文件列表"""
    try:
        files = await get_file_list()
        return files
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """上传文件"""
    try:
        result = await file_service.save_file(file, current_user.id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    vector_store = Depends(lambda: vector_store)
):
    """删除文件"""
    try:
        # 查找文件记录
        file = db.query(FileModel).filter(
            FileModel.id == file_id,
            FileModel.user_id == current_user.id
        ).first()
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # 删除物理文件
        
        deleted =  await file_service.delete_file(file)
        if not deleted:
            logger.error(f"删除物理文件或向量数据库记录失败: {str(e)}", exc_info=True)
        
        # 删除数据库记录
        db.delete(file)
        db.commit()
        logger.info(f"数据库记录已删除: {file.id}")
        return {"status": "success", "message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除文件失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 