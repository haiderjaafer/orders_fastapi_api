from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request ,UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from sqlalchemy import create_engine, Column, Integer, String,Unicode, Date, Boolean, Enum as SQLEnum,text

from sqlalchemy.orm import validates,Session  # Correct import
from contextlib import asynccontextmanager
import logging
import uvicorn
import pyodbc
import urllib.parse
import os
import sqlalchemy





from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator




# # ================= Configuration =================
# class Settings(BaseSettings):
#     DATABASE_SERVER: str
#     DATABASE_NAME: str
#     DATABASE_USER: str
#     DATABASE_PASSWORD: str
#     DATABASE_DRIVER: str = "ODBC Driver 17 for SQL Server"
#     PDF_BASE_PATH: str = 'D:/order_pdfs'

#     class Config:
#         env_file = ".env"

# settings = Settings()

# # ================= SQLAlchemy Setup =================
# params = urllib.parse.quote_plus(
#     f"DRIVER={settings.DATABASE_DRIVER};"
#     f"SERVER={settings.DATABASE_SERVER};"
#     f"DATABASE={settings.DATABASE_NAME};"
#     f"UID={settings.DATABASE_USER};"
#     f"PWD={settings.DATABASE_PASSWORD};"
#     f"TrustServerCertificate=yes;"
#     f"MARS_Connection=Yes;"
#     f"CHARSET=UTF8;"
# )

# SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"unicode_results": True},
#     fast_executemany=True,
#     echo=False , # optional for debugging

#     pool_size=5,
#     max_overflow=2,
#     pool_timeout=30
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# def get_db() -> Generator[Session, None, None]:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # ================= Database Models =================
# class OrderType(str, Enum):
#     LOCAL = "محلية"
#     DIRECT_LOCAL = "محلية-مباشرة"
#     STORAGE_LOCAL = "محلية-مخزنية"
#     EXTERNAL_GENERAL = "خارجية-عامة"
#     EXTERNAL_MONOPOLISTIC = "خارجية-احتكارية"

# class OrderStatus(str, Enum):
#     PENDING = "قيد الانجاز"
#     APPROVED = "منجز"
#     REJECTED = "الغيت"

# class CurrencyType(str, Enum):
#     USD = "دولار امريكي"
#     EUR = "اليورو"
#     LOCAL = "دينار عراقي"

# class CommitteeDB(Base):
#     __tablename__ = "ComTB"

#     coID = Column(Unicode(50), primary_key=True, index=True)
#     Com = Column(Unicode(255), nullable=False)

# class CommitteeOut(BaseModel):
#     coID: str
#     Com: str

#     class Config:
#         from_attributes = True  # so SQLAlchemy model can be directly returned

# #1. Department model
# class DepartmentDB(Base):
#     __tablename__ = "DepTB"

#     deID = Column(Integer, primary_key=True, index=True)
#     Dep = Column(String(250), nullable=True)
#     coID = Column(Integer, nullable=True)


# # 2. Pydantic Schema
# class DepartmentOut(BaseModel):
#     deID: int
#     Dep: str
#     coID: int

#     class Config:
#         from_attributes = True



# class EstimatorCreate(BaseModel):
#     estimatorName: str
#     startDate: Optional[date] = None
#     endDate: Optional[date] = None
#     estimatorStatus: bool
#     coID: int
#     deID: int

#     @field_validator('startDate', 'endDate', mode='before')
#     def validate_date_format(cls, value):
#         if value is None or isinstance(value, date):
#             return value
#         try:
#             return date.fromisoformat(value)
#         except ValueError:
#             raise ValueError("Date must be in YYYY-MM-DD format")


# class EstimatorDB(Base):
#     __tablename__ = "estimatorsTable"

#     estimatorID = Column(Integer, primary_key=True, index=True)
#     estimatorName = Column(String(100))
#     startDate = Column(Date)
#     endDate = Column(Date)
#     estimatorStatus = Column(Boolean)
#     coID = Column(Integer)
#     deID = Column(Integer)


# class EstimatorOut(BaseModel):
#     # estimatorID: int
#     estimatorName: str                # will return only estimatorName as response or if want to getback all properties 
#     # startDate: date | None = None
#     # endDate: date | None = None
#     # estimatorStatus: bool | None = None
#     # coID: int | None = None
#     # deID: int | None = None

#     class Config:
#         from_attributes = True



# class OrderDB(Base):
#     __tablename__ = "orderTable"

#     orderID = Column(Integer, primary_key=True, index=True)
#     orderNo = Column(String(50), nullable=False)
#     orderYear = Column(String(4), nullable=False)
#     orderDate = Column(Date, nullable=False)
#     orderType = Column(Unicode(50), nullable=False)
#     coID = Column(Integer)
#     deID = Column(Integer)
#     materialName = Column(String(5000))
#     estimatorID = Column(Integer)
#     procedureID = Column(Integer)
#     orderStatus = Column(Unicode(50), nullable=False)
#     notes = Column(String(5000))
#     achievedOrderDate = Column(Date)
#     priceRequestedDestination = Column(String(100))
#     finalPrice = Column(String(50))
#     currencyType = Column(Unicode(50), nullable=False)
#     cunnrentDate = Column(Date)
#     color = Column(String(50))
#     checkOrderLink = Column(Boolean, default=False)
#     userID = Column(Integer, nullable=False)

#     @validates('orderType')
#     def validate_order_type(self, key, value):
#         try:
#             return OrderType(value).value  # Convert to enum then get Arabic value
#         except ValueError:
#             valid_values = [e.value for e in OrderType]
#             raise ValueError(f"Invalid orderType. Valid values: {valid_values}")
    
#     @validates('orderStatus')
#     def validate_order_status(self, key, value):
#         try:
#             return OrderStatus(value).value
#         except ValueError:
#             valid_values = [e.value for e in OrderStatus]
#             raise ValueError(f"Invalid orderStatus. Valid values: {valid_values}")
    
#     @validates('currencyType')
#     def validate_currency_type(self, key, value):
#         try:
#             return CurrencyType(value).value
#         except ValueError:
#             valid_values = [e.value for e in CurrencyType]
#             raise ValueError(f"Invalid currencyType. Valid values: {valid_values}")

# # ================= Pydantic Schemas =================
# class OrderBase(BaseModel):
#     orderNo: str = Field(..., min_length=1)
#     orderYear: str = Field(..., pattern=r'^\d{4}$')
#     orderDate: date
#     orderType: OrderType = OrderType.LOCAL
#     coID: Optional[int] = Field(None, gt=0)
#     deID: Optional[int] = Field(None, gt=0)
#     materialName: Optional[str] = Field(None, max_length=5000)
#     estimatorID: Optional[int] = Field(None, gt=0)
#     procedureID: Optional[int] = Field(None, gt=0)
#     orderStatus: OrderStatus = OrderStatus.PENDING
#     notes: Optional[str] = Field(None, max_length=5000)
#     achievedOrderDate: Optional[date] = None
#     priceRequestedDestination: Optional[str] = None
#     finalPrice: Optional[str] = None
#     currencyType: CurrencyType = CurrencyType.LOCAL
#     cunnrentDate: Optional[date] = None
#     color: Optional[str] = None
#     checkOrderLink: bool = False
#     userID: int = Field(..., gt=0)

#     # @field_validator('achievedOrderDate')
#     # @classmethod
#     # def validate_achieved_date(cls, v: Optional[date], values: Dict[str, Any]) -> Optional[date]:
#     #     if v and 'orderDate' in values.data and v < values.data['orderDate']:
#     #         raise ValueError("Achieved date cannot be before order date")
#     #     return v
    
#     @field_validator('orderType', 'orderStatus', 'currencyType')
#     def validate_enums(cls, value, info):
#         field_name = info.field_name  # Get the field being validated
        
#         try:
#             if field_name == 'orderType':
#                 OrderType(value)
#             elif field_name == 'orderStatus':
#                 OrderStatus(value)
#             elif field_name == 'currencyType':
#                 CurrencyType(value)
#             return value
#         except ValueError:
#             valid_values = {
#                 'orderType': [e.value for e in OrderType],
#                 'orderStatus': [e.value for e in OrderStatus],
#                 'currencyType': [e.value for e in CurrencyType]
#             }
#             raise ValueError(f"Invalid {field_name}. Valid options: {valid_values[field_name]}")
   
# class OrderCreate(OrderBase):
#     class Config:
#         from_attributes = True

# class OrderOut(OrderBase):
#     orderID: int
    
#     # Add these configs
#     class Config:
#         from_attributes = True
#         json_encoders = {
#             OrderType: lambda v: v.value,  # Return Arabic value
#             OrderStatus: lambda v: v.value,
#             CurrencyType: lambda v: v.value
#         }


# class PdfTableCreate(BaseModel):
#     orderID: int
#     orderNo: str
#     orderYear: str

# class PdfTableOut(BaseModel):
#     message: str
#     pdfID: int
#     filePath: str    

# # ================= Dependency Setup =================


# # ================= Service Layer =================
# class OrderService:
#     STATUS_COLOR_MAP = {
#         OrderStatus.APPROVED: "GREEN",
#         OrderStatus.REJECTED: "RED",
#         OrderStatus.PENDING: "YELLOW"
#     }

    
    
#     @staticmethod
#     def create_order(db: Session, order: OrderCreate):
#         # Check for existing order
#         existing = db.query(OrderDB).filter(
#             OrderDB.orderNo == order.orderNo,
#             OrderDB.orderYear == order.orderYear
#         ).first()

#         if existing:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail=f"Order {order.orderNo}/{order.orderYear} already exists"
#             )

#         # Set default values
#         db_order = OrderDB(
#             **order.model_dump(exclude_unset=True),
#             color=order.color or OrderService.STATUS_COLOR_MAP.get(order.orderStatus),
#             cunnrentDate=datetime.now().date()
#         )

#         try:
#             db.add(db_order)
#             db.commit()
#             db.refresh(db_order)

#             # 🟡 Convert problematic Enum fields from string to Enum (for response validation)
#             response_data = db_order.__dict__.copy()

#             response_data["orderType"] = OrderType(response_data["orderType"])
#             response_data["orderStatus"] = OrderStatus(response_data["orderStatus"])
#             response_data["currencyType"] = CurrencyType(response_data["currencyType"])

#             # Return correct response schema
#             return OrderOut(**response_data)

#         except Exception as e:
#             db.rollback()
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Database error: {str(e)}"
#             )

    
#     @staticmethod
#     def get_order(db: Session, order_id: int) -> OrderOut:
#         try:
#             # Get the raw database row
#             result = db.execute(
#                 text("SELECT * FROM orderTable WHERE orderID = :id"),
#                 {"id": order_id}
#             ).mappings().first()
            
#             if not result:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail=f"Order {order_id} not found"
#                 )
                
            
#             order_data = dict(result)

# # Fixing corrupted enum fields manually
#             order_data['orderType'] = OrderType(order_data['orderType'])
#             order_data['orderStatus'] = OrderStatus(order_data['orderStatus'])
#             order_data['currencyType'] = CurrencyType(order_data['currencyType'])

#             return OrderOut(**order_data)


            
#         except SQLAlchemyError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Database error: {str(e)}"
#             )
        


# class CommitteeService:
#     @staticmethod
#     def get_all_committees(db: Session) -> List[CommitteeOut]:
#         try:
#             print("committees")
#             committees = db.query(CommitteeDB).all()
#            # return [CommitteeOut.from_orm(c) for c in committees]
#             return [CommitteeOut.model_validate(com) for com in committees]

#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Error fetching committees: {str(e)}")


# class DepartmentService:
#     @staticmethod
#     def get_departments_by_committee(db: Session, co_id: int):
#         return db.query(DepartmentDB).filter(DepartmentDB.coID == co_id).all()
    


# class EstimatorService:
#     @staticmethod
#     def get_all_estimators(db: Session):
#         return db.query(EstimatorDB).all()



#     @staticmethod
#     def insert_estimator(db: Session, estimator: EstimatorCreate) -> int:
#         try:
#             query = text("""
#                 INSERT INTO estimatorsTable (
#                     estimatorName, 
#                     startDate, 
#                     endDate, 
#                     estimatorStatus, 
#                     coID, 
#                     deID
#                 ) 
#                 OUTPUT INSERTED.estimatorID
#                 VALUES (:estimatorName, :startDate, :endDate, :estimatorStatus, :coID, :deID)
#             """)
#             params = {
#                 "estimatorName": estimator.estimatorName,
#                 "startDate": estimator.startDate,
#                 "endDate": estimator.endDate,
#                 "estimatorStatus": estimator.estimatorStatus,
#                 "coID": estimator.coID,
#                 "deID": estimator.deID
#             }

#             result = db.execute(query, params)
#             estimator_id = result.scalar()  # ✅ .scalar() to get single value correctly
#             db.commit()

#             if estimator_id is None:
#                 raise ValueError("Failed to retrieve estimatorID after insert")

#             return estimator_id
        
#         except Exception as e:
#             db.rollback()
#             raise e



# class PdfService:
#     @staticmethod
#     def get_next_count(db: Session, order_id: int) -> int:
#         query = text("SELECT MAX(countPdf) FROM dbo.pdfTable WHERE orderID = :order_id")
#         result = db.execute(query, {"order_id": order_id}).scalar()
#         return (result or 0) + 1

#     @staticmethod
#     def insert_pdf(db: Session, pdf_data: PdfTableCreate, file_content: bytes, base_path: str) -> dict:
#         # Get next count
#         count = PdfService.get_next_count(db, pdf_data.orderID)

#         # Construct filename and path
#         filename = f"{pdf_data.orderNo}.{pdf_data.orderYear}.{count}.pdf"
#         full_path = os.path.join(base_path, filename)

#         # Make sure base folder exists
#         os.makedirs(base_path, exist_ok=True)

#         # Save the file
#         with open(full_path, 'wb') as f:
#             f.write(file_content)

#         # Insert into DB
#         insert_query = text("""
#             INSERT INTO dbo.pdfTable (orderID, orderNo, orderYear, countPdf, pdf)
#             VALUES (:orderID, :orderNo, :orderYear, :countPdf, :pdf)
#         """)

#         db.execute(insert_query, {
#             "orderID": pdf_data.orderID,
#             "orderNo": pdf_data.orderNo,
#             "orderYear": pdf_data.orderYear,
#             "countPdf": count,
#             "pdf": full_path
#         })
#         db.commit()

#         # Get the last inserted pdfID
#         get_id_query = text("SELECT IDENT_CURRENT('dbo.pdfTable')")
#         pdf_id = db.execute(get_id_query).scalar()

#         return {
#             "pdfID": int(pdf_id),
#             "filePath": full_path
#         }





# # ================= API Routes =================
# orders_router = APIRouter(prefix="/api/orders", tags=["orders"])

# @orders_router.post(
#     "",
#     response_model=OrderOut,
#     status_code=status.HTTP_201_CREATED,
#     summary="Create a new order"
# )
# async def create_order(
#     request: Request,
#     order_data: OrderCreate,
#     db: Session = Depends(get_db)
# ):
#     try:
#         created_order = OrderService.create_order(db, order_data)
#         return created_order
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )

# @orders_router.get("/{order_id}", response_model=OrderOut)
# def get_order(
#     order_id: int,
#     db: Session = Depends(get_db)  # Correct dependency injection
# ):
#     try:
#         print("get order")
#         return OrderService.get_order(db, order_id)
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
    




# committee_router = APIRouter(prefix="/api/committees", tags=["committees"])


# @committee_router.get("", response_model=List[CommitteeOut])
# def list_committees(db: Session = Depends(get_db)):
#     return CommitteeService.get_all_committees(db)


# department_router = APIRouter(prefix="/api/departments", tags=["departments"])

# @department_router.get("/by-committee/{co_id}", response_model=List[DepartmentOut])
# def get_departments_by_committee(co_id: int, db: Session = Depends(get_db)):
#     return DepartmentService.get_departments_by_committee(db, co_id)


# estimator_router = APIRouter(prefix="/api/estimators", tags=["estimators"])

# @estimator_router.get("/", response_model=List[EstimatorOut])
# def get_all_estimators(db: Session = Depends(get_db)):
#     return EstimatorService.get_all_estimators(db)

# routerAddEstimators = APIRouter(
#     prefix="/api/estimators",
#     tags=["Estimators"]
# )

# @routerAddEstimators.post("/", status_code=201)
# async def create_estimator(estimator: EstimatorCreate, db: Session = Depends(get_db)):
#     try:
#         estimator_id = EstimatorService.insert_estimator(db, estimator)
#         return {
#             "message": "Estimator created successfully",
#             "estimatorID": estimator_id
#         }
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except sqlalchemy.exc.SQLAlchemyError as e:
#         print(f"Database error: {str(e)}")  # Print the real DB error
#         raise HTTPException(status_code=500, detail="Database operation failed")
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")  # Also print general unexpected errors
#         raise HTTPException(status_code=500, detail="An unexpected error occurred")



# router = APIRouter(prefix="/api/pdfs", tags=["pdfs"])


# base_path = settings.PDF_BASE_PATH

# # You should define your base PDF folder
# PDF_BASE_PATH = base_path

# @router.post("/upload")
# async def upload_pdf(
#     orderID: int = Form(...),
#     orderNo: str = Form(...),
#     orderYear: str = Form(...),
#     pdf: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     # Validate PDF extension
#     if not pdf.filename.lower().endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

#     # Read file content
#     file_content = await pdf.read()

#     # Create PdfTableCreate model
#     pdf_data = PdfTableCreate(
#         orderID=orderID,
#         orderNo=orderNo,
#         orderYear=orderYear
#     )

#     try:
#         result = PdfService.insert_pdf(db, pdf_data, file_content, PDF_BASE_PATH)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {str(e)}")

#     return {
#         "message": "PDF uploaded successfully",
#         "pdfID": result["pdfID"],
#         "filePath": result["filePath"]
#     }


# ================= Application Setup =================

from app.database.database import engine,Base
from app.database.config import settings


# all routes imports
from app.routes.order import orders_router
from app.routes.committee import committee_router
from app.routes.department import department_router
from app.routes.estimator import estimatorRouter
from app.routes.pdf import routerPdf

from app.routes.procedure import procedureRouter




@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.MODE.upper() == "DEVELOPMENT":   # always safe
        print("🌱 DEVELOPMENT mode: creating database tables...")
        Base.metadata.create_all(bind=engine)
    else:
        print("🚀 PRODUCTION mode: skipping table creation.")

    yield  # always yield after preparing



def create_app() -> FastAPI:
    app = FastAPI(
        title="Orders API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    app.include_router(orders_router)
    app.include_router(committee_router)
    app.include_router(department_router)
    app.include_router( estimatorRouter )
    app.include_router(routerPdf)  
    app.include_router(procedureRouter)   
      

 
    return app

app = create_app()

