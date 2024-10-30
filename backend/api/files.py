from fastapi import APIRouter, UploadFile, Depends
from backend.services.vector_store import vector_store
from backend.core.auth import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile,
    current_user = Depends(get_current_user)
):
    try:
        # 保存文件
        file_path = await save_uploaded_file(file)
        
        # 添加到向量数据库
        success = await vector_store.add_file(
            file_path=file_path,
            user_id=current_user.id,  # 确保传入用户ID
            metadata={
                "filename": file.filename,
                "content_type": file.content_type
            }
        )
        
        if success:
            return {"message": "文件上传成功"}
        else:
            return {"error": "文件处理失败"}, 500
            
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return {"error": str(e)}, 500 