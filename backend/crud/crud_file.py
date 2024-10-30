from typing import List
from backend.crud.base import CRUDBase
from backend.models.file import File
from sqlalchemy.orm import Session

class CRUDFile(CRUDBase[File, dict, dict]):
    def get_multi_by_user(self, db: Session, *, user_id: int) -> List[File]:
        return db.query(File).filter(File.user_id == user_id).all()

crud_file = CRUDFile(File) 