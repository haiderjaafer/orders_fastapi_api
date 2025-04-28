
from fastapi import  APIRouter, Depends, HTTPException, status, Request 
from sqlalchemy.orm import Session  
from app.services.committee import CommitteeService
from app.models.committee import CommitteeOut
from app.database.database import get_db
from typing import List



committee_router = APIRouter(prefix="/api/committees", tags=["committees"])


@committee_router.get("", response_model=List[CommitteeOut])
def list_committees(db: Session = Depends(get_db)):
    return CommitteeService.get_all_committees(db)
