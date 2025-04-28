
from sqlalchemy.orm import Session  
from app.models.department import DepartmentDB,DepartmentOut



class DepartmentService:
    @staticmethod
    def get_departments_by_committee(db: Session, co_id: int):
        return db.query(DepartmentDB).filter(DepartmentDB.coID == co_id).all()
