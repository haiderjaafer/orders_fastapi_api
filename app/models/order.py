from pydantic import BaseModel, Field, field_validator
from enum import Enum
from sqlalchemy import  Column, Integer, String,Unicode, Date, Boolean
from sqlalchemy.orm import validates  # Correct import
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from app.database.database import Base






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

