

from fastapi import  APIRouter, Depends, HTTPException, status, Request ,Path,Body
from sqlalchemy.orm import Session  
from app.services.estimator import EstimatorService
from app.models.estimator import EstimatorOut,EstimatorCreate
from app.database.database import get_db
from typing import List
import sqlalchemy  # this for sqlalchemy.exc.SQLAlchemyError


estimatorRouter = APIRouter(prefix="/api/estimators", tags=["estimators"])

@estimatorRouter.get("/", response_model=List[EstimatorOut])
def get_all_estimators(db: Session = Depends(get_db)):
    return EstimatorService.get_all_estimators(db)





@estimatorRouter.post("/add", status_code=201)
async def create_estimator(estimator: EstimatorCreate, db: Session = Depends(get_db)):
    try:
        estimator_id = EstimatorService.insert_estimator(db, estimator)
        return {
            "message": "Estimator created successfully",
            "estimatorID": estimator_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"Database error: {str(e)}")  # Print the real DB error
        raise HTTPException(status_code=500, detail="Database operation failed")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Also print general unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred")





@estimatorRouter.put("/{estimator_id}", status_code=200)
async def update_estimator(
    estimator_id: int = Path(..., description="ID of the estimator to update"),
    estimator: EstimatorCreate = Body(...),  # <- THIS!
    db: Session = Depends(get_db)
):
    updated_estimator = EstimatorService.update_estimator(db, estimator_id, estimator)
    return {
        "message": "Estimator updated successfully",
        "data": {
            "estimatorID": updated_estimator.estimatorID,
            "estimatorName": updated_estimator.estimatorName
        }
    }

