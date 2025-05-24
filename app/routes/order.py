from typing import List, Optional
from fastapi import  APIRouter, Depends, HTTPException, status, Request ,Query
from sqlalchemy.orm import Session  
from app.models.order import OrderCreate,OrderOut,OrderDB, PaginatedOrderOut
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



@orders_router.get("/getAll", response_model=PaginatedOrderOut)
def get_orders(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    orderStatus: Optional[str] = Query(None, enum=["منجز", "قيد الانجاز", "الغيت"])  # Add orderStatus
):
    return OrderService.getAllorderNo(db, page, limit, orderStatus)  # Pass orderStatus





@orders_router.get("/getAllForComobox", response_model=list[str])
def getAllForComobox(db: Session = Depends(get_db)):
    return OrderService.getAll(db)



@orders_router.get("/{order_id}", response_model=List[OrderOut])
def get_order(
    order_id: str,
    db: Session = Depends(get_db)  # Correct dependency injection
):
    try:
        print(f"get order{order_id}")
        return OrderService.getAllOrderByOrderNo(db, order_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )





# git push --force origin main   will force push if remote repository has changes that not pulled or existed in locally


