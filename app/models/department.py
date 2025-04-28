from pydantic import BaseModel
from sqlalchemy import  Column, Integer, String
from app.database.database import Base


#1. Department model
class DepartmentDB(Base):
    __tablename__ = "DepTB"

    deID = Column(Integer, primary_key=True, index=True)
    Dep = Column(String(250), nullable=True)
    coID = Column(Integer, nullable=True)


# 2. Pydantic Schema
class DepartmentOut(BaseModel):
    deID: int
    Dep: str
    coID: int

    class Config:
        from_attributes = True

