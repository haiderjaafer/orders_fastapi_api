from fastapi import  APIRouter, Depends, HTTPException, status, Request ,Query
from sqlalchemy.orm import Session  
from app.models.order import OrderCreate,OrderOut,OrderDB
from app.database.database import get_db
from app.services.order import OrderService





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



@orders_router.get("/check-order-exists")
def check_order_exists(
    orderNo: str = Query(..., alias="orderNo"),
    orderYear: str = Query(..., alias="orderYear"),
    db: Session = Depends(get_db)
):
    order = db.query(OrderDB).filter(
        OrderDB.orderNo == orderNo,
        OrderDB.orderYear == orderYear
    ).first()

    return {"exists": bool(order)}



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


# Add this to your FastAPI router
# @orders_router.get("/check-order-exists")
# async def check_order_exists(
#     orderNo: str = Query(..., regex="^\d+$"),  # Only numbers allowed
#     orderYear: str = Query(...),
#     db: Session = Depends(get_db)
# ):
#     try:
#         existing = db.query(OrderDB).filter(
#             OrderDB.orderNo == orderNo,
#             OrderDB.orderYear == orderYear
#         ).first()
#         return {"exists": existing is not None}
#     except Exception as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Validation error: {str(e)}"
#         )


