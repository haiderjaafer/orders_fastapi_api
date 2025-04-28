from fastapi import  HTTPException, status
from app.models.order import OrderDB
from app.models.order import OrderStatus,OrderType,CurrencyType,OrderOut
from app.models.order import OrderCreate

from datetime import  datetime
from sqlalchemy import text

from sqlalchemy.orm import Session  # Correct import
from sqlalchemy.exc import SQLAlchemyError



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
