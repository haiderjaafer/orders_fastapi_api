from pydantic import BaseModel, field_validator
from sqlalchemy import  Column, Integer, String, Date, Boolean,Unicode
from typing import Optional
from datetime import date
from app.database.database import Base


class EstimatorDB(Base):
    __tablename__ = "estimatorsTable"

    estimatorID = Column(Integer, primary_key=True, index=True)
    estimatorName = Column(Unicode(100))
    startDate = Column(Date)
    endDate = Column(Date)
    estimatorStatus = Column(Boolean)
    coID = Column(Integer)
    deID = Column(Integer)


class EstimatorCreate(BaseModel):
    estimatorName: str
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    estimatorStatus: bool
    coID: int
    deID: int

    @field_validator('startDate', 'endDate', mode='before')
    def validate_date_format(cls, value):
        if value is None or isinstance(value, date):
            return value
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")




class EstimatorOut(BaseModel):
    estimatorID: int
    estimatorName: str                # will return only estimatorName as response or if want to getback all properties 
    startDate: date | None = None
    endDate: date | None = None
    estimatorStatus: bool | None = None
    coID: int | None = None
    deID: int | None = None

    class Config:
        from_attributes = True



    # from sqlalchemy import UnicodeText

    # description = Column(UnicodeText) this for huge text like notes that take let say 1000
    

