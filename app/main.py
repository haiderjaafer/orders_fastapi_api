from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request
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



from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator




# ================= Configuration =================
class Settings(BaseSettings):
    DATABASE_SERVER: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_DRIVER: str = "ODBC Driver 17 for SQL Server"
    PDF_BASE_PATH: str = 'D:/order_pdfs'

    class Config:
        env_file = ".env"

settings = Settings()

# ================= SQLAlchemy Setup =================
params = urllib.parse.quote_plus(
    f"DRIVER={settings.DATABASE_DRIVER};"
    f"SERVER={settings.DATABASE_SERVER};"
    f"DATABASE={settings.DATABASE_NAME};"
    f"UID={settings.DATABASE_USER};"
    f"PWD={settings.DATABASE_PASSWORD};"
    f"TrustServerCertificate=yes;"
    f"MARS_Connection=Yes;"
    f"CHARSET=UTF8;"
)

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"unicode_results": True},
    fast_executemany=True,
    echo=True , # optional for debugging

    pool_size=5,
    max_overflow=2,
    pool_timeout=30
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= Database Models =================
class OrderType(str, Enum):
    LOCAL = "محلية"
    DIRECT_LOCAL = "محلية-مباشرة"
    STORAGE_LOCAL = "محلية-مخزنية"
    EXTERNAL_GENERAL = "خارجية-عامة"
    EXTERNAL_MONOPOLISTIC = "خارجية-احتكارية"

class OrderStatus(str, Enum):
    PENDING = "قيد الانجاز"
    APPROVED = "منجز"
    REJECTED = "الغيت"

class CurrencyType(str, Enum):
    USD = "دولار امريكي"
    EUR = "اليورو"
    LOCAL = "دينار عراقي"

class OrderDB(Base):
    __tablename__ = "orderTable"

    orderID = Column(Integer, primary_key=True, index=True)
    orderNo = Column(String(50), nullable=False)
    orderYear = Column(String(4), nullable=False)
    orderDate = Column(Date, nullable=False)
    orderType = Column(Unicode(50), nullable=False)
    coID = Column(Integer)
    deID = Column(Integer)
    materialName = Column(String(5000))
    estimatorID = Column(Integer)
    procedureID = Column(Integer)
    orderStatus = Column(Unicode(50), nullable=False)
    notes = Column(String(5000))
    achievedOrderDate = Column(Date)
    priceRequestedDestination = Column(String(100))
    finalPrice = Column(String(50))
    currencyType = Column(Unicode(50), nullable=False)
    cunnrentDate = Column(Date)
    color = Column(String(50))
    checkOrderLink = Column(Boolean, default=False)
    userID = Column(Integer, nullable=False)

    @validates('orderType')
    def validate_order_type(self, key, value):
        try:
            return OrderType(value).value  # Convert to enum then get Arabic value
        except ValueError:
            valid_values = [e.value for e in OrderType]
            raise ValueError(f"Invalid orderType. Valid values: {valid_values}")
    
    @validates('orderStatus')
    def validate_order_status(self, key, value):
        try:
            return OrderStatus(value).value
        except ValueError:
            valid_values = [e.value for e in OrderStatus]
            raise ValueError(f"Invalid orderStatus. Valid values: {valid_values}")
    
    @validates('currencyType')
    def validate_currency_type(self, key, value):
        try:
            return CurrencyType(value).value
        except ValueError:
            valid_values = [e.value for e in CurrencyType]
            raise ValueError(f"Invalid currencyType. Valid values: {valid_values}")

# ================= Pydantic Schemas =================
class OrderBase(BaseModel):
    orderNo: str = Field(..., min_length=1)
    orderYear: str = Field(..., pattern=r'^\d{4}$')
    orderDate: date
    orderType: OrderType = OrderType.LOCAL
    coID: Optional[int] = Field(None, gt=0)
    deID: Optional[int] = Field(None, gt=0)
    materialName: Optional[str] = Field(None, max_length=5000)
    estimatorID: Optional[int] = Field(None, gt=0)
    procedureID: Optional[int] = Field(None, gt=0)
    orderStatus: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = Field(None, max_length=5000)
    achievedOrderDate: Optional[date] = None
    priceRequestedDestination: Optional[str] = None
    finalPrice: Optional[str] = None
    currencyType: CurrencyType = CurrencyType.LOCAL
    cunnrentDate: Optional[date] = None
    color: Optional[str] = None
    checkOrderLink: bool = False
    userID: int = Field(..., gt=0)

    # @field_validator('achievedOrderDate')
    # @classmethod
    # def validate_achieved_date(cls, v: Optional[date], values: Dict[str, Any]) -> Optional[date]:
    #     if v and 'orderDate' in values.data and v < values.data['orderDate']:
    #         raise ValueError("Achieved date cannot be before order date")
    #     return v
    
    @field_validator('orderType', 'orderStatus', 'currencyType')
    def validate_enums(cls, value, info):
        field_name = info.field_name  # Get the field being validated
        
        try:
            if field_name == 'orderType':
                OrderType(value)
            elif field_name == 'orderStatus':
                OrderStatus(value)
            elif field_name == 'currencyType':
                CurrencyType(value)
            return value
        except ValueError:
            valid_values = {
                'orderType': [e.value for e in OrderType],
                'orderStatus': [e.value for e in OrderStatus],
                'currencyType': [e.value for e in CurrencyType]
            }
            raise ValueError(f"Invalid {field_name}. Valid options: {valid_values[field_name]}")
   
class OrderCreate(OrderBase):
    class Config:
        from_attributes = True

class OrderOut(OrderBase):
    orderID: int
    
    # Add these configs
    class Config:
        from_attributes = True
        json_encoders = {
            OrderType: lambda v: v.value,  # Return Arabic value
            OrderStatus: lambda v: v.value,
            CurrencyType: lambda v: v.value
        }

# ================= Dependency Setup =================


# ================= Service Layer =================
class OrderService:
    STATUS_COLOR_MAP = {
        OrderStatus.APPROVED: "GREEN",
        OrderStatus.REJECTED: "RED",
        OrderStatus.PENDING: "YELLOW"
    }

    
    
    @staticmethod
    def create_order(db: Session, order: OrderCreate):
        # Check for existing order
        existing = db.query(OrderDB).filter(
            OrderDB.orderNo == order.orderNo,
            OrderDB.orderYear == order.orderYear
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Order {order.orderNo}/{order.orderYear} already exists"
            )

        # Set default values
        db_order = OrderDB(
            **order.model_dump(exclude_unset=True),
            color=order.color or OrderService.STATUS_COLOR_MAP.get(order.orderStatus),
            cunnrentDate=datetime.now().date()
        )

        try:
            db.add(db_order)
            db.commit()
            db.refresh(db_order)

            # 🟡 Convert problematic Enum fields from string to Enum (for response validation)
            response_data = db_order.__dict__.copy()

            response_data["orderType"] = OrderType(response_data["orderType"])
            response_data["orderStatus"] = OrderStatus(response_data["orderStatus"])
            response_data["currencyType"] = CurrencyType(response_data["currencyType"])

            # Return correct response schema
            return OrderOut(**response_data)

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    
    @staticmethod
    def get_order(db: Session, order_id: int) -> OrderOut:
        try:
            # Get the raw database row
            result = db.execute(
                text("SELECT * FROM orderTable WHERE orderID = :id"),
                {"id": order_id}
            ).mappings().first()
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order {order_id} not found"
                )
                
            
            order_data = dict(result)

# Fixing corrupted enum fields manually
            order_data['orderType'] = OrderType(order_data['orderType'])
            order_data['orderStatus'] = OrderStatus(order_data['orderStatus'])
            order_data['currencyType'] = CurrencyType(order_data['currencyType'])

            return OrderOut(**order_data)


            
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

# ================= API Routes =================
orders_router = APIRouter(prefix="/api/orders", tags=["orders"])

@orders_router.post(
    "",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order"
)
async def create_order(
    request: Request,
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    try:
        created_order = OrderService.create_order(db, order_data)
        return created_order
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@orders_router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)  # Correct dependency injection
):
    try:
        print("get order")
        return OrderService.get_order(db, order_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ================= Application Setup =================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables (only for development)
    Base.metadata.create_all(bind=engine)
    yield

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

    @app.get("/api/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)