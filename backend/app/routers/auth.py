# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid
from pydantic import BaseModel

from .. import crud, schemas, security
from ..database import get_db

class LoginCredentials(BaseModel):
    username: str
    password: str

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/register", response_model=schemas.Customer)
async def register(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """Register a new customer"""
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(customer.password)
    return crud.create_customer(db=db, customer=customer, hashed_password=hashed_password)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(credentials: LoginCredentials, db: Session = Depends(get_db)):
    try:
        customer = crud.get_customer_by_email(db, email=credentials.username)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not security.verify_password(credentials.password, customer.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": customer.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/restaurant-admin/token", response_model=schemas.Token)
async def restaurant_admin_login(credentials: LoginCredentials, db: Session = Depends(get_db)):
    """Login endpoint specifically for restaurant admins"""
    restaurant = crud.authenticate_restaurant_admin(db, email=credentials.username, password=credentials.password)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": restaurant.restaurant_admin_email, "restaurant_id": str(restaurant.id), "user_type": "restaurant_admin"}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Temporary endpoint to promote user to admin - REMOVE IN PRODUCTION
@router.post("/promote-admin")
def promote_to_admin(email: str, db: Session = Depends(get_db)):
    """Temporary endpoint to make a user admin. Remove in production!"""
    customer = crud.get_customer_by_email(db, email=email)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer.is_admin = True
    db.commit()
    db.refresh(customer)

# ===============================================
# Restaurant Admin Authentication Dependencies
# ===============================================

async def get_current_restaurant_admin(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_access_token(token)
        email: str = payload.get("sub")
        restaurant_id: str = payload.get("restaurant_id")
        if email is None or restaurant_id is None:
            raise credentials_exception
    except:
        raise credentials_exception
    
    restaurant = crud.get_restaurant_by_admin_email(db, email=email)
    if restaurant is None or restaurant.id != uuid.UUID(restaurant_id):
        raise credentials_exception
    return restaurant

async def get_current_restaurant_admin_optional(
    token: str = Depends(security.oauth2_scheme_optional),
    db: Session = Depends(get_db)
):
    if not token:
        return None
    try:
        return await get_current_restaurant_admin(token, db)
    except:
        return None
    return {"message": f"User {email} is now an admin"}