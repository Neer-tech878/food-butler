# app/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from .. import security

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Order)
def create_order(
    order: schemas.OrderCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Create a new order for the currently authenticated user.
    """
    try:
        return crud.create_order(db=db, order=order, customer_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.Order])
def read_all_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Retrieve all orders (admin functionality).
    """
    return crud.get_orders(db=db, skip=skip, limit=limit)

@router.get("/me/", response_model=List[schemas.Order])
def read_my_orders(
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Retrieve order history for the currently authenticated user.
    """
    return crud.get_orders_by_customer(db=db, customer_id=current_user.id)


@router.get("/history", response_model=List[schemas.Order])
def get_order_history(
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Retrieve order history for the currently authenticated user (alias endpoint).
    """
    return crud.get_orders_by_customer(db=db, customer_id=current_user.id)


@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single order by its ID.
    """
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.put("/{order_id}/status")
def update_order_status(
    order_id: uuid.UUID,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Update the status of an order.
    """
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    db_order.status = new_status
    db.commit()
    db.refresh(db_order)
    return {"message": "Order status updated successfully"}