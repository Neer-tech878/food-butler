from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
import uuid

from .. import crud, schemas, security
from ..routers.auth import get_current_restaurant_admin, get_current_restaurant_admin_optional

# Dependency to allow access for admin users or restaurant admins
async def get_current_admin_or_restaurant_admin(
    db: Session = Depends(security.get_db),
    current_user: Union[schemas.Customer, None] = Depends(security.get_current_user_optional),
    current_restaurant_admin: Union[schemas.Restaurant, None] = Depends(get_current_restaurant_admin_optional)
):
    if current_user and current_user.is_admin:
        return {"type": "admin", "user": current_user}
    elif current_restaurant_admin:
        return {"type": "restaurant_admin", "restaurant": current_restaurant_admin}
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Restaurant, status_code=201)
def create_restaurant(
    restaurant: schemas.RestaurantCreate,
    db: Session = Depends(security.get_db),
    # Temporarily use regular auth instead of admin
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Create a new restaurant. Temporarily allowing any authenticated user.
    """
    return crud.create_restaurant(db=db, restaurant=restaurant)


@router.get("/", response_model=List[schemas.Restaurant])
def read_restaurants(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(security.get_db)
    # Removed authentication requirement for restaurant browsing
    # current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Retrieve all restaurants. Public endpoint for browsing.
    """
    restaurants = crud.get_restaurants(db, skip=skip, limit=limit)
    return restaurants


@router.get("/{restaurant_id}", response_model=schemas.Restaurant)
def read_restaurant(
    restaurant_id: uuid.UUID, 
    db: Session = Depends(security.get_db)
):
    """
    Retrieve a specific restaurant by ID. Public endpoint.
    """
    restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.get("/{restaurant_id}/menu", response_model=List[schemas.MenuItem])
def read_restaurant_menu(
    restaurant_id: uuid.UUID, 
    db: Session = Depends(security.get_db)
    # Removed authentication requirement for menu browsing - customers should be able to see menus
    # current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Retrieve the menu for a specific restaurant. Public endpoint for browsing menus.
    """
    menu_items = crud.get_menu_items_by_restaurant(db, restaurant_id=restaurant_id)
    return menu_items

@router.put("/{restaurant_id}", response_model=schemas.Restaurant)
def update_restaurant(
    restaurant_id: uuid.UUID,
    restaurant_update: schemas.RestaurantCreate,
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    db_restaurant = crud.update_restaurant(db=db, restaurant_id=restaurant_id, restaurant_update=restaurant_update)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant

@router.delete("/{restaurant_id}", response_model=schemas.Restaurant)
def delete_restaurant(
    restaurant_id: uuid.UUID,
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    db_restaurant = crud.delete_restaurant(db=db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant