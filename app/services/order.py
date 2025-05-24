from fastapi import  HTTPException, status
from app.models.order import OrderDB
from app.models.order import OrderStatus,OrderType,CurrencyType,OrderOut
from app.models.order import OrderCreate

from datetime import  datetime
from sqlalchemy import text
from sqlalchemy import select,func
from typing import List, Optional



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
    def getAllOrderByOrderNo(db: Session, order_no: str) -> List[OrderOut]:
        stmt = (
            select(OrderDB)
            .where(OrderDB.orderNo == order_no)
            .order_by(OrderDB.orderYear.desc())  # Optional: sort by most recent year
        )

        results = db.scalars(stmt).all()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No orders found for order number {order_no}"
            )

        
        return [OrderOut.model_validate(order) for order in results] 



    # def getAllOrderByOrderNo(db: Session, order_no: str) -> List[OrderOut]:
    #     try:
    #         result = db.execute(
    #             text("SELECT * FROM orderTable WHERE orderNo = :order_no"),
    #             {"order_no": order_no}
    #         ).mappings().all()  # Use `.all()` instead of `.first()` to get multiple rows

    #         if not result:
    #             raise HTTPException(
    #                 status_code=status.HTTP_404_NOT_FOUND,
    #                 detail=f"No orders found for orderNo {order_no}"
    #             )

    #         orders = []
    #         for row in result:
    #             order_data = dict(row)
    #             order_data['orderType'] = OrderType(order_data['orderType'])
    #             order_data['orderStatus'] = OrderStatus(order_data['orderStatus'])
    #             order_data['currencyType'] = CurrencyType(order_data['currencyType'])

    #             orders.append(OrderOut(**order_data))

    #         return orders

    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=str(e)
    #         )

     
    @staticmethod
    def getAllorderNo(db: Session, page: int = 1, limit: int = 10, orderStatus: Optional[str] = None):
        # Step 1: Count total unique orderNo with optional status filter
        count_stmt = select(func.count(func.distinct(OrderDB.orderNo)))
        if orderStatus:
            count_stmt = count_stmt.filter(OrderDB.orderStatus == orderStatus)
        total = db.execute(count_stmt).scalar()

        # Step 2: Calculate offset
        offset = (page - 1) * limit

        # Step 3: Fetch paginated orderNo list with optional status filter
        stmt = (
            select(
                OrderDB.orderID,
                OrderDB.orderNo,
                OrderDB.orderDate,
                OrderDB.orderYear,
                OrderDB.orderType,
                OrderDB.coID,
                OrderDB.deID,
                OrderDB.materialName,
                OrderDB.estimatorID,
                OrderDB.procedureID,
                OrderDB.orderStatus,
                OrderDB.notes,
                OrderDB.achievedOrderDate,
                OrderDB.priceRequestedDestination,
                OrderDB.finalPrice,
                OrderDB.currencyType,
                OrderDB.cunnrentDate,
                OrderDB.color,
                OrderDB.checkOrderLink,
                OrderDB.userID,
            )
            .distinct(OrderDB.orderNo)
            .order_by(OrderDB.orderNo)
        )
        if orderStatus:
            stmt = stmt.filter(OrderDB.orderStatus == orderStatus)
        stmt = stmt.offset(offset).limit(limit)

        results = db.execute(stmt).all()

        # Format data
        data = [
            {
                "orderID": row.orderID,
                "orderNo": row.orderNo,
                "orderDate": row.orderDate,
                "orderYear": row.orderYear,
                "orderType": row.orderType,
                "coID": row.coID,
                "deID": row.deID,
                "materialName": row.materialName,
                "estimatorID": row.estimatorID,
                "procedureID": row.procedureID,
                "orderStatus": row.orderStatus,
                "notes": row.notes,
                "achievedOrderDate": row.achievedOrderDate,
                "priceRequestedDestination": row.priceRequestedDestination,
                "finalPrice": row.finalPrice,
                "currencyType": row.currencyType,
                "cunnrentDate": row.cunnrentDate,
                "color": row.color,
                "checkOrderLink": row.checkOrderLink,
                "userID": row.userID,
            }
            for row in results
        ]

        # Step 4: Return formatted pagination response
        return {
            "data": data,
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": (total + limit - 1) // limit  # ceil division
        }

    

    @staticmethod
    def getAll(db: Session):
        stmt = (
            select(OrderDB.orderNo)
            .group_by(OrderDB.orderNo)
            .order_by(OrderDB.orderNo)
           # .limit(100)
        )
        result = db.execute(stmt).scalars().all()
        return result
    

    # def getAllorderNo(db: Session):   // this also worked
    #     query = text("""
    #         SELECT DISTINCT TOP 100 orderNo
    #         FROM dbo.orderTable
    #         ORDER BY orderNo
    #     """)
    #     result = db.execute(query).scalars().all()
    #     return result