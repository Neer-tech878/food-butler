from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas, security

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)

@router.post("/", status_code=201)
def add_inventory(
    inventory: schemas.InventoryCreate,
    db: Session = Depends(security.get_db),
    # This should be protected by an admin user in the future
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Create or update the stock level for a menu item.
    """
    return crud.create_or_update_inventory(db=db, inventory=inventory)