from fastapi import  APIRouter, Depends, HTTPException, status, Request 
from sqlalchemy.orm import Session  
from app.models.order import OrderCreate,OrderOut
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
    

