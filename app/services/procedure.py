

# services/procedure_service.py
from sqlalchemy.orm import Session
from app.models.procedure import ProcedureDB
from typing import List

class ProcedureService:
    @staticmethod
    def get_all_procedures(db: Session) -> List[ProcedureDB]:
        return db.query(ProcedureDB).all()
