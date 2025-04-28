
from fastapi import  APIRouter, Depends, HTTPException, status, Request 
from sqlalchemy.orm import Session  
from app.services.department import DepartmentService
from app.models.department import DepartmentOut
from app.database.database import get_db
from typing import List






department_router = APIRouter(prefix="/api/departments", tags=["departments"])

@department_router.get("/by-committee/{co_id}", response_model=List[DepartmentOut])
def get_departments_by_committee(co_id: int, db: Session = Depends(get_db)):
    return DepartmentService.get_departments_by_committee(db, co_id)
