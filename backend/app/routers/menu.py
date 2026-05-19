from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

# Use correct relative imports for a package structure
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter(
    prefix="/menu",
    tags=["Menu"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.MenuItem, status_code=201)
def create_menu_item(
    menu_item: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    # Temporarily use regular auth instead of admin
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Create a new menu item. Temporarily allowing any authenticated user.
    """
    # This assumes create_menu_item in crud.py is updated to handle restaurant_id
    return crud.create_menu_item(db=db, menu_item=menu_item)


@router.get("/", response_model=List[schemas.MenuItem])
def read_menu_items(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
    # Removed authentication requirement for menu browsing
    # current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Retrieve all available menu items with pagination.
    Public endpoint - no authentication required for browsing menu.
    """
    try:
        items = crud.get_menu_items(db, skip=skip, limit=limit)
        return items
    except Exception as e:
        print(f"Error in get_menu_items: {e}")
        return []  # Return empty list for now
@router.get("/{menu_item_id}", response_model=schemas.MenuItem)
def read_menu_item(
    menu_item_id: uuid.UUID,
    db: Session = Depends(get_db),
    # Any logged-in user can view a single item
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Retrieve a single menu item by its ID. Requires a logged-in user.
    """
    db_menu_item = crud.get_menu_item(db, menu_item_id=menu_item_id)
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_menu_item


@router.put("/{menu_item_id}", response_model=schemas.MenuItem)
def update_menu_item(
    menu_item_id: uuid.UUID,
    item_update: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    # Temporarily use regular auth instead of admin
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Update a menu item. Temporarily allowing any authenticated user.
    """
    db_item = crud.update_menu_item(db=db, menu_item_id=menu_item_id, item_update=item_update)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_item


@router.delete("/{menu_item_id}", response_model=schemas.MenuItem)
def delete_menu_item(
    menu_item_id: uuid.UUID,
    db: Session = Depends(get_db),
    # Temporarily use regular auth instead of admin
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Soft delete a menu item (marks as unavailable). Temporarily allowing any authenticated user.
    """
    db_item = crud.delete_menu_item(db=db, menu_item_id=menu_item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_item

