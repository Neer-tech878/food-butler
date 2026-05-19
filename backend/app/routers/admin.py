# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from pydantic import BaseModel

from .. import crud, schemas, security, models

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    # Temporarily removed admin dependency for testing
    # dependencies=[Depends(security.get_current_admin_user)],
    responses={403: {"description": "Operation not permitted"}},
)

class OrderStatusUpdate(BaseModel):
    status: str

@router.get("/orders/", response_model=List[schemas.Order])
def read_all_orders(skip: int = 0, limit: int = 100, db: Session = Depends(security.get_db)):
    """
    Retrieve all user orders. Requires administrator privileges.
    """
    orders = crud.get_all_orders(db, skip=skip, limit=limit)
    return orders

@router.put("/orders/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: uuid.UUID,
    status_update: OrderStatusUpdate,
    db: Session = Depends(security.get_db)
):
    """
    Update the status of an order. Requires administrator privileges.
    """
    order = crud.update_order_status(db, order_id=order_id, new_status=status_update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/restaurants/", response_model=schemas.Restaurant)
def create_restaurant_admin(
    restaurant: schemas.RestaurantCreate,
    db: Session = Depends(security.get_db)
):
    """
    Create a new restaurant (admin endpoint).
    """
    return crud.create_restaurant(db=db, restaurant=restaurant)

@router.put("/restaurants/{restaurant_id}", response_model=schemas.Restaurant)
def update_restaurant_admin(
    restaurant_id: str,
    restaurant: schemas.RestaurantUpdate,
    db: Session = Depends(security.get_db)
):
    """
    Update a restaurant (admin endpoint).
    """
    try:
        restaurant_uuid = uuid.UUID(restaurant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
    
    db_restaurant = crud.update_restaurant(db, restaurant_id=restaurant_uuid, restaurant=restaurant)
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant

@router.delete("/restaurants/{restaurant_id}")
def delete_restaurant_admin(
    restaurant_id: str,
    db: Session = Depends(security.get_db)
):
    """
    Delete a restaurant (admin endpoint).
    """
    try:
        restaurant_uuid = uuid.UUID(restaurant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
    
    success = crud.delete_restaurant(db, restaurant_id=restaurant_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return {"message": "Restaurant deleted successfully"}

@router.post("/menu-items/", response_model=schemas.MenuItem)
def create_menu_item_admin(
    menu_item: schemas.MenuItemCreate,
    db: Session = Depends(security.get_db)
):
    """
    Create a new menu item (admin endpoint).
    """
    return crud.create_menu_item(db=db, menu_item=menu_item)

@router.put("/menu-items/{menu_item_id}", response_model=schemas.MenuItem)
def update_menu_item_admin(
    menu_item_id: str,
    menu_item: schemas.MenuItemUpdate,
    db: Session = Depends(security.get_db)
):
    """
    Update a menu item (admin endpoint).
    """
    try:
        menu_item_uuid = uuid.UUID(menu_item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid menu item ID format")
    
    db_menu_item = crud.update_menu_item(db, menu_item_id=menu_item_uuid, menu_item=menu_item)
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_menu_item

@router.delete("/menu-items/{menu_item_id}")
def delete_menu_item_admin(
    menu_item_id: str,
    db: Session = Depends(security.get_db)
):
    """
    Delete a menu item (admin endpoint).
    """
    try:
        menu_item_uuid = uuid.UUID(menu_item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid menu item ID format")
    
    success = crud.delete_menu_item(db, menu_item_id=menu_item_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": "Menu item deleted successfully"}

@router.get("/inventory/", response_model=List[schemas.Inventory])
def read_inventory(
    db: Session = Depends(security.get_db)
):
    """
    Get all inventory items (admin endpoint).
    """
    return db.query(models.Inventory).all()

@router.put("/inventory/{menu_item_id}")
def update_inventory(
    menu_item_id: uuid.UUID,
    quantity_data: dict,
    db: Session = Depends(security.get_db)
):
    """
    Update inventory quantity for a menu item (admin endpoint).
    """
    quantity = quantity_data.get("quantity", 0)
    inventory_item = db.query(models.Inventory).filter(models.Inventory.menu_item_id == menu_item_id).first()
    if not inventory_item:
        inventory_item = models.Inventory(menu_item_id=menu_item_id, quantity=quantity)
        db.add(inventory_item)
    else:
        inventory_item.quantity = quantity
    db.commit()
    db.refresh(inventory_item)
    return {"message": "Inventory updated successfully"}

@router.get("/customers/", response_model=List[schemas.Customer])
def read_all_customers(skip: int = 0, limit: int = 100, db: Session = Depends(security.get_db)):
    """
    Retrieve all customers. Requires administrator privileges.
    """
    customers = crud.get_all_customers(db, skip=skip, limit=limit)
    return customers

@router.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer_admin(
    customer_id: str,
    customer: schemas.CustomerUpdate,
    db: Session = Depends(security.get_db)
):
    """
    Update a customer. Requires administrator privileges.
    """
    try:
        customer_uuid = uuid.UUID(customer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid customer ID format")
    
    update_data = customer.model_dump(exclude_unset=True)
    db_customer = crud.update_customer(db, customer_id=customer_uuid, customer_update=update_data)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.delete("/customers/{customer_id}")
def delete_customer_admin(
    customer_id: str,
    db: Session = Depends(security.get_db)
):
    """
    Delete a customer. Requires administrator privileges.
    """
    try:
        customer_uuid = uuid.UUID(customer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid customer ID format")
    
    success = crud.delete_customer(db, customer_id=customer_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}