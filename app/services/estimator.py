from sqlalchemy.orm import Session  
from app.models.estimator import EstimatorCreate,EstimatorDB,EstimatorOut
from sqlalchemy import text
from fastapi import HTTPException





class EstimatorService:
    @staticmethod
    def get_all_estimators(db: Session):
        return db.query(EstimatorDB).all()



    @staticmethod
    def insert_estimator(db: Session, estimator: EstimatorCreate) -> int:
        try:
            query = text("""
                INSERT INTO estimatorsTable (
                    estimatorName, 
                    startDate, 
                    endDate, 
                    estimatorStatus, 
                    coID, 
                    deID
                ) 
                OUTPUT INSERTED.estimatorID
                VALUES (:estimatorName, :startDate, :endDate, :estimatorStatus, :coID, :deID)
            """)
            params = {
                "estimatorName": estimator.estimatorName,
                "startDate": estimator.startDate,
                "endDate": estimator.endDate,
                "estimatorStatus": estimator.estimatorStatus,
                "coID": estimator.coID,
                "deID": estimator.deID
            }

            result = db.execute(query, params)
            estimator_id = result.scalar()  # ✅ .scalar() to get single value correctly
            db.commit()

            if estimator_id is None:
                raise ValueError("Failed to retrieve estimatorID after insert")

            return estimator_id
        
        except Exception as e:
            db.rollback()
            raise e
    @staticmethod
    def update_estimator(db: Session, estimator_id: int, estimator_data: EstimatorCreate):
        estimator = db.query(EstimatorDB).filter(EstimatorDB.estimatorID == estimator_id).first()
        if not estimator:
            raise HTTPException(status_code=404, detail="Estimator not found")

        estimator.estimatorName = estimator_data.estimatorName
        estimator.startDate = estimator_data.startDate
        estimator.endDate = estimator_data.endDate
        estimator.estimatorStatus = estimator_data.estimatorStatus
        estimator.coID = estimator_data.coID
        estimator.deID = estimator_data.deID

        db.commit()
        db.refresh(estimator)

        return estimator