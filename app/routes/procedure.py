

# routes/procedures.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.procedure import ProcedureOut
from app.services.procedure import ProcedureService
from typing import List



procedureRouter = APIRouter(prefix="/api/procedures", tags=["procedure"])


@procedureRouter.get("", response_model=List[ProcedureOut])
def get_procedures(db: Session = Depends(get_db)):
    return ProcedureService.get_all_procedures(db)
