from enum import Enum
from sqlalchemy import Column, Integer, String, Unicode, Date, Boolean
from sqlalchemy.orm import validates
from app.database.database import Base
from datetime import date


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
            return OrderType(value).value
        except ValueError:
            raise ValueError(f"Invalid orderType. Valid values: {[e.value for e in OrderType]}")

    @validates('orderStatus')
    def validate_order_status(self, key, value):
        try:
            return OrderStatus(value).value
        except ValueError:
            raise ValueError(f"Invalid orderStatus. Valid values: {[e.value for e in OrderStatus]}")

    @validates('currencyType')
    def validate_currency_type(self, key, value):
        try:
            return CurrencyType(value).value
        except ValueError:
            raise ValueError(f"Invalid currencyType. Valid values: {[e.value for e in CurrencyType]}")






from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum


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
    checkOrderLink: Optional[bool] = False
    userID: int = Field(..., gt=0)

    @field_validator('achievedOrderDate')
    @classmethod
    def validate_achieved_date(cls, v: Optional[date], info) -> Optional[date]:
        order_date = info.data.get("orderDate")
        if v and order_date and v < order_date:
            raise ValueError("Achieved date cannot be before order date")
        return v

    @field_validator('orderType', 'orderStatus', 'currencyType')
    def validate_enums(cls, value, info):
        field_name = info.field_name
        enum_map = {
            'orderType': OrderType,
            'orderStatus': OrderStatus,
            'currencyType': CurrencyType
        }
        try:
            enum_map[field_name](value)
            return value
        except ValueError:
            valid_values = [e.value for e in enum_map[field_name]]
            raise ValueError(f"Invalid {field_name}. Valid options: {valid_values}")


class OrderCreate(OrderBase):
    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    orderID: int
    orderNo: str
    orderYear: Optional[str] = None
    orderDate: date
    orderType: Optional[str] = None
    coID: Optional[int] = None
    deID: Optional[int] = None
    materialName: Optional[str] = None
    estimatorID: Optional[int] = None
    procedureID: Optional[int] = None
    orderStatus: Optional[str] = None
    notes: Optional[str] = None
    achievedOrderDate: Optional[date] = None
    priceRequestedDestination: Optional[str] = None
    finalPrice: Optional[str] = None
    currencyType: Optional[str] = None
    cunnrentDate: Optional[date] = None
    color: Optional[str] = None
    checkOrderLink: Optional[bool] = None
    userID: Optional[int] = None


    model_config = {
        "from_attributes": True
    }


class PaginatedOrderOut(BaseModel):
    data: List[OrderOut]
    total: int
    page: int
    limit: int
    totalPages: int
