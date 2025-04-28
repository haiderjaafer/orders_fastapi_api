from pydantic import BaseModel
from sqlalchemy import  Column,String,Integer
from app.database.database import Base



class CommitteeDB(Base):
    __tablename__ = "ComTB"

    coID = Column(Integer, primary_key=True, index=True)
    Com = Column(String(250), nullable=False)

class CommitteeOut(BaseModel):
    coID: str
    Com: str

    class Config:
        from_attributes = True  # so SQLAlchemy model can be directly returned
