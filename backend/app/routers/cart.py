# app/routers/cart.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from .. import crud, schemas, security

router = APIRouter(
    prefix="/cart",
    tags=["Shopping Cart"],
    responses={404: {"description": "Not found"}},
)

@router.post("/items", response_model=schemas.Order)
def add_item_to_cart(
    item: schemas.OrderItemCreate,
    db: Session = Depends(security.get_db), # Re-using get_db from security
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Add an item to the current user's shopping cart.
    If no cart exists, one will be created.
    """
    try:
        cart = crud.add_item_to_cart(db=db, customer_id=current_user.id, item=item)
        return cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/", response_model=schemas.Order)
def get_cart(
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Retrieve the current user's active shopping cart.
    """
    cart = crud.get_active_cart_by_customer(db=db, customer_id=current_user.id)
    if not cart:
        # Create an empty cart for the user
        from ..models import Order
        cart = Order(
            customer_id=current_user.id,
            status='cart',
            total_price=0
        )
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.put("/items/{order_item_id}", response_model=schemas.Order)
def update_cart_item(
    order_item_id: uuid.UUID,
    item_update: schemas.OrderItemUpdate,
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Update the quantity of an item in the current user's shopping cart.
    """
    try:
        cart = crud.update_cart_item_quantity(
            db=db,
            customer_id=current_user.id,
            order_item_id=order_item_id,
            quantity=item_update.quantity
        )
        return cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/items/{order_item_id}", response_model=schemas.Order)
def remove_cart_item(
    order_item_id: uuid.UUID,
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Remove an item from the current user's shopping cart.
    """
    try:
        cart = crud.remove_item_from_cart(
            db=db,
            customer_id=current_user.id,
            order_item_id=order_item_id
        )
        return cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

class CheckoutRequest(BaseModel):
    delivery_address: Optional[str] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    use_saved_address: bool = False

@router.post("/checkout", response_model=schemas.Order)
def checkout_cart(
    checkout_data: CheckoutRequest,
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Finalize the user's cart and move it to the 'pending_payment' status.
    This prepares the order for payment processing.
    Requires delivery address for order delivery.
    Can use saved address from profile or provide new address.
    """
    # Determine which address to use
    if checkout_data.use_saved_address or not checkout_data.delivery_address:
        # Use saved address from profile
        if not current_user.delivery_address:
            raise HTTPException(
                status_code=400, 
                detail="No saved address found. Please provide delivery address or update your profile."
            )
        delivery_address = current_user.delivery_address
        delivery_lat = float(current_user.delivery_lat) if current_user.delivery_lat else None
        delivery_lng = float(current_user.delivery_lng) if current_user.delivery_lng else None
    else:
        # Use provided address
        delivery_address = checkout_data.delivery_address
        delivery_lat = checkout_data.delivery_lat
        delivery_lng = checkout_data.delivery_lng
    
    try:
        order = crud.checkout_cart(
            db=db,
            customer_id=current_user.id,
            delivery_address=delivery_address,
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))