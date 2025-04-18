from fastapi import FastAPI, APIRouter, Depends, HTTPException, status,Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from enum import Enum
from typing import Optional, Dict, Any
from datetime import date, datetime
import pyodbc
import logging
import time
import uvicorn

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

# ================= Models =================
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

STATUS_COLOR_MAP = {
    OrderStatus.APPROVED.value: "GREEN",  # green
    OrderStatus.REJECTED.value: "RED",  # red
    OrderStatus.PENDING.value: "YELLOW",   # yellow
}


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
    priceRequestedDestination: Optional[str] 
    finalPrice: Optional[str] 
    # = Field(None, pattern=r'^\d+(\.\d{1,2})?$')
    currencyType: CurrencyType = CurrencyType.LOCAL
    currentDate: Optional[date] = None
    color: Optional[str] = None
    checkOrderLink: bool = False
    userID: int = Field(..., gt=0)

    @field_validator('achievedOrderDate')
    @classmethod
    def validate_achieved_date(cls, v: Optional[date], values: Dict[str, Any]) -> Optional[date]:
        if v and 'orderDate' in values.data and v < values.data['orderDate']:
            raise ValueError("Achieved date cannot be before order date")
        return v

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    orderID: int  # This is the auto-generated ID
    
    class Config:
        from_attributes = True

# ================= Database =================
class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            connection_string = (
                f"DRIVER={{{settings.DATABASE_DRIVER}}};"
                f"SERVER={settings.DATABASE_SERVER};"
                f"DATABASE={settings.DATABASE_NAME};"
                f"UID={settings.DATABASE_USER};"
                f"PWD={settings.DATABASE_PASSWORD};"
            )
            cls._instance._connection = pyodbc.connect(connection_string)
            cls._instance._connection.autocommit = True
        return cls._instance

    def get_connection(self):
        return self._connection

def get_db():
    return DatabaseConnection().get_connection()

# ================= DAO =================

class OrderDAO:
    def __init__(self, db: pyodbc.Connection):
        self.db = db  # Consistent naming - use 'db' everywhere

    def check_order_exists(self, orderNo: str, orderYear: str) -> None:
        """
        Raise HTTPException(409) if order with the given orderNo and orderYear exists.
        """
        query = """
        SELECT COUNT(*) 
        FROM [dbo].[orderTable] 
        WHERE orderNo = ? AND orderYear = ?
        """
        params = (orderNo, orderYear)
        cursor = None
        try:
            cursor = self.db.cursor()  # Changed from self.connection to self.db
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result[0] > 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Order with number '{orderNo}' and year '{orderYear}' already exists."
                )
        except pyodbc.Error as e:
            print(f"Database error in check_order_exists: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def insert_order(self, order: OrderCreate) -> OrderOut:
        # This will raise an HTTPException(409) if the order exists
        self.check_order_exists(order.orderNo, order.orderYear)
        
        if order.color is None:
            order.color = STATUS_COLOR_MAP.get(order.orderStatus, "DEFAULT_COLOR")

        defaults = {
            'notes': order.notes or 'لا توجد ملاحظات',
            'checkOrderLink': order.checkOrderLink,
            'finalPrice': order.finalPrice or '0',
            'procedureID': order.procedureID or 1,
            'color': order.color,
            'currentDate': datetime.now().date()
        }

        insert_query = """
        INSERT INTO [dbo].[orderTable] (
            orderNo, orderYear, orderDate, orderType, coID, deID, materialName, 
            estimatorID, procedureID, orderStatus, notes, achievedOrderDate, 
            priceRequestedDestination, finalPrice, currencyType, currentDate, 
            color, checkOrderLink, userID
        ) 
        OUTPUT INSERTED.orderID, INSERTED.*
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        params = (
            order.orderNo, order.orderYear, order.orderDate, order.orderType, 
            order.coID, order.deID, order.materialName, order.estimatorID,
            defaults['procedureID'], order.orderStatus, defaults['notes'],
            order.achievedOrderDate, order.priceRequestedDestination, 
            defaults['finalPrice'], order.currencyType, defaults['currentDate'],
            defaults['color'], defaults['checkOrderLink'], order.userID
        )

        try:
            with self.db.cursor() as cursor:  # Changed from self.connection to self.db
                cursor.execute(insert_query, params)
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to retrieve inserted order details"
                    )
                
                columns = [column[0] for column in cursor.description]
                order_data = dict(zip(columns, result))

                
                
                self.db.commit()  # Changed from self.connection to self.db
                return OrderOut(**order_data)
                
        except pyodbc.Error as e:
            self.db.rollback()  # Changed from self.connection to self.db
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    def get_order_by_id(self, order_id: int) -> Optional[OrderOut]:
        cursor = self.db.cursor()
        query = "SELECT * FROM orderTable WHERE orderID = ?"
        cursor.execute(query, order_id)
        result = cursor.fetchone()
        
        if not result:
            return None
            
        # Map all fields explicitly, handling NULL values
        return OrderOut(
            orderID=result.orderID,
            orderNo=result.orderNo,
            orderYear=result.orderYear,
            orderDate=result.orderDate,
            orderType=OrderType(result.orderType) if result.orderType else OrderType.LOCAL,
            coID=result.coID if result.coID else None,
            deID=result.deID if result.deID else None,
            materialName=result.materialName,
            estimatorID=result.estimatorID if result.estimatorID else None,
            procedureID=result.procedureID if result.procedureID else None,
            orderStatus=OrderStatus(result.orderStatus) if result.orderStatus else OrderStatus.PENDING,
            notes=result.notes,
            achievedOrderDate=result.achievedOrderDate,
            priceRequestedDestination=result.priceRequestedDestination,
            finalPrice=str(result.finalPrice) if result.finalPrice else None,
            currencyType=CurrencyType(result.currencyType) if result.currencyType else CurrencyType.LOCAL,
            currentDate=result.currentDate,
            color=result.color if result.color else STATUS_COLOR_MAP.get(
                OrderStatus(result.orderStatus) if result.orderStatus else OrderStatus.PENDING, 
                "DEFAULT_COLOR"
            ),
            checkOrderLink=bool(result.checkOrderLink),
            userID=result.userID if result.userID else None
        )






# ================= API Routes =================
orders_router = APIRouter(prefix="/api/orders", tags=["orders"])
# orders_router = APIRouter(prefix="/api/orders", tags=["orders"])

@orders_router.post(
    "/add",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order"
)
async def create_order(
    request: Request,
    order_data: OrderCreate,
    db: pyodbc.Connection = Depends(get_db)
):
    try:
        raw_body = await request.body()
        print("Raw request:", raw_body.decode())
        print("we request:")

        dao = OrderDAO(db)
        return dao.insert_order(order_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@orders_router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: pyodbc.Connection = Depends(get_db)
):
    try:
        # Debug prints to verify connection
        print(f"DB connection type: {type(db)}")
        print(f"DB connection state: {'open' if db else 'closed'}")
        
        dao = OrderDAO(db)
        order = dao.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        return order
        
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
# ================= Application Setup =================
def create_app() -> FastAPI:
    app = FastAPI(
        title="Orders API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # List of allowed origins
        allow_credentials=True,  # This is the critical missing piece
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
        expose_headers=["*"]  # Exposes all headers to frontend
    )

    app.include_router(orders_router)

    @app.get("/api/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)