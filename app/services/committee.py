from app.models.committee import CommitteeOut,CommitteeDB
from fastapi import  HTTPException
from sqlalchemy.orm import Session  
from typing import  List


class CommitteeService:
    @staticmethod
    def get_all_committees(db: Session) -> List[CommitteeOut]:
        try:
            print("committees")
            committees = db.query(CommitteeDB).all()
           # return [CommitteeOut.from_orm(c) for c in committees]
            return [CommitteeOut.model_validate(com) for com in committees]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching committees: {str(e)}")

