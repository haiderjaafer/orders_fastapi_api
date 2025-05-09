# models.py
from sqlalchemy import Column, Integer, String
from app.database.database import Base  # Assuming you have Base = declarative_base()

class ProcedureDB(Base):
    __tablename__ = "proceduresTable"

    procedureID = Column(Integer, primary_key=True, index=True)
    procedureName = Column(String(255), nullable=False)




# schemas.py
#Pydantic Schema

from pydantic import BaseModel

class ProcedureOut(BaseModel):
    procedureID: int
    procedureName: str

    class Config:
        from_attributes = True  # or orm_mode = True for Pydantic v1
