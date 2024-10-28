from sqlalchemy.orm import Session
import logging
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.models.database import Base

T = TypeVar('T', bound=Base)

class BaseService(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting {self.model.__name__} by id: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred while fetching {self.model.__name__}"
            )

    def get_all(self, db: Session) -> List[T]:
        try:
            return db.query(self.model).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting all {self.model.__name__}s: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred while fetching {self.model.__name__}s"
            )

    def create(self, db: Session, obj_in: dict) -> T:
        try:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred while creating {self.model.__name__}"
            )

    def update(self, db: Session, id: int, obj_in: dict) -> Optional[T]:
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return None
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred while updating {self.model.__name__}"
            )

    def delete(self, db: Session, id: int) -> bool:
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return False
            db.delete(db_obj)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error deleting {self.model.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred while deleting {self.model.__name__}"
            )
