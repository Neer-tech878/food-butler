import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Import modules from the current 'app' package
from . import crud, schemas
from .database import get_db

# --- Configuration ---
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("WARNING: Backend SECRET_KEY environment variable not set!")
    SECRET_KEY = "fallback-secret-key-change-in-production"  # Fallback for development
else:
    print(f"Backend SECRET_KEY loaded successfully (length: {len(SECRET_KEY)})")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT Creation ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set in the environment")
        
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Security Dependencies ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"--- BACKEND SECURITY: Validating token, SECRET_KEY available: {SECRET_KEY is not None} ---")
        if SECRET_KEY:
            print(f"--- BACKEND SECURITY: SECRET_KEY length: {len(SECRET_KEY)} ---")
        if not SECRET_KEY:
            raise credentials_exception
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        print(f"--- BACKEND SECURITY: Token decoded successfully for email: {email} ---")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError as e:
        print(f"--- BACKEND SECURITY: JWT decode failed: {e} ---")
        raise credentials_exception
    
    user = crud.get_customer_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_current_user_optional(token: str = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)):
    if not token:
        return None
    try:
        return get_current_user(token, db)
    except:
        return None

# THIS IS THE FUNCTION THAT WAS MISSING
def get_current_admin_user(current_user: schemas.Customer = Depends(get_current_user)):
    """
    A dependency that checks if the current user is an administrator.
    If not, it raises a 403 Forbidden error.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have administrative privileges"
        )
    return current_user

