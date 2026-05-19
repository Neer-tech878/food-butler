# app/routers/delivery.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

from .. import crud, schemas, security
from ..database import get_db

router = APIRouter(
    prefix="/delivery",
    tags=["Delivery Tracking"],
    responses={404: {"description": "Not found"}},
)


@router.get("/track/{order_id}", response_model=schemas.OrderTrackingInfo)
def get_order_tracking(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Get real-time tracking information for an order.
    Includes delivery location, driver location, status, and ETA.
    """
    db_order = crud.get_order_tracking_info(db, order_id=order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify the order belongs to the current user (unless admin)
    if not current_user.is_admin and db_order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return schemas.OrderTrackingInfo(
        order_id=db_order.id,
        status=db_order.status,
        delivery_status=db_order.delivery_status or "pending",
        delivery_address=db_order.delivery_address,
        delivery_lat=db_order.delivery_lat,
        delivery_lng=db_order.delivery_lng,
        driver_lat=db_order.driver_lat,
        driver_lng=db_order.driver_lng,
        driver_name=db_order.driver_name,
        driver_phone=db_order.driver_phone,
        estimated_delivery_time=db_order.estimated_delivery_time,
        created_at=db_order.created_at
    )


@router.put("/{order_id}/driver-location")
def update_driver_location(
    order_id: uuid.UUID,
    location_update: schemas.DeliveryLocationUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Update the driver's current location for real-time tracking.
    This endpoint would typically be called by a driver app or admin.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can update driver location")
    
    updated_order = crud.update_driver_location(
        db,
        order_id=order_id,
        driver_lat=location_update.driver_lat,
        driver_lng=location_update.driver_lng
    )
    
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Driver location updated successfully"}


@router.put("/{order_id}/delivery-status")
def update_delivery_status(
    order_id: uuid.UUID,
    status_update: schemas.DeliveryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Update the delivery status of an order.
    Statuses: pending, assigned, picked_up, in_transit, nearby, delivered
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can update delivery status")
    
    valid_statuses = ["pending", "assigned", "picked_up", "in_transit", "nearby", "delivered", "cancelled"]
    if status_update.delivery_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid delivery status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    updated_order = crud.update_delivery_status(
        db,
        order_id=order_id,
        delivery_status=status_update.delivery_status,
        estimated_delivery_time=status_update.estimated_delivery_time
    )
    
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Delivery status updated successfully"}


@router.put("/{order_id}/assign-driver")
def assign_driver(
    order_id: uuid.UUID,
    driver_info: dict,
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Assign a driver to an order.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can assign drivers")
    
    driver_name = driver_info.get("driver_name")
    driver_phone = driver_info.get("driver_phone")
    
    if not driver_name or not driver_phone:
        raise HTTPException(status_code=400, detail="Driver name and phone are required")
    
    updated_order = crud.assign_driver_to_order(
        db,
        order_id=order_id,
        driver_name=driver_name,
        driver_phone=driver_phone
    )
    
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Set estimated delivery time (default 30 minutes from now)
    estimated_time = datetime.now() + timedelta(minutes=30)
    crud.update_delivery_status(
        db,
        order_id=order_id,
        delivery_status="assigned",
        estimated_delivery_time=estimated_time
    )
    
    return {"message": "Driver assigned successfully", "estimated_delivery_time": estimated_time}
