# app/routers/customers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from .. import crud, schemas, security
from ..database import get_db

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer. (Note: For production, use /register)
    """
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(customer.password)
    return crud.create_customer(db=db, customer=customer, hashed_password=hashed_password)


@router.get("/me", response_model=schemas.Customer)
def read_my_profile(current_user: schemas.Customer = Depends(security.get_current_user)):
    """
    Get the profile for the currently authenticated user.
    """
    return current_user

@router.get("/email/{email}", response_model=schemas.Customer)
def read_customer_by_email(email: str, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_email(db, email=email)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.get("/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single customer by their ID.
    """
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.put("/me/password", status_code=204) # 204 No Content is standard for successful updates with no body
def change_my_password(
    password_update: schemas.CustomerPasswordUpdate,
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Update the password for the currently authenticated user.
    """
    hashed_password = security.get_password_hash(password_update.new_password)
    crud.update_customer_password(db=db, customer=current_user, hashed_password=hashed_password)
    return

@router.put("/me/address", response_model=schemas.Customer)
def update_my_address(
    address_update: schemas.CustomerAddressUpdate,
    db: Session = Depends(security.get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Update the delivery address for the currently authenticated user.
    Requires address text and GPS coordinates.
    """
    updated_customer = crud.update_customer_address(
        db=db,
        customer=current_user,
        delivery_address=address_update.delivery_address,
        delivery_lat=address_update.delivery_lat,
        delivery_lng=address_update.delivery_lng
    )
    return updated_customer