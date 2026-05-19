# ai_agent/security.py
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY")  # This should be the same secret key as your backend
if not SECRET_KEY:
    print("⚠️ WARNING: SECRET_KEY environment variable not set!")
    SECRET_KEY = "fallback-secret-key-change-in-production"  # Fallback for development
else:
    print(f"✅ SECRET_KEY loaded successfully (length: {len(SECRET_KEY)})")

ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # tokenUrl is just a placeholder here

class TokenData(BaseModel):
    email: str | None = None

def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"🔐 [get_current_user_email] Decoding token (length: {len(token) if token else 0})")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            print("❌ [get_current_user_email] Email (sub) not found in JWT payload!")
            raise credentials_exception
        print(f"✅ [get_current_user_email] JWT decoded successfully for user: {email}")
        # We are not returning a full user object, just the email from the trusted token.
        return email
    except JWTError as e:
        print(f"❌ [get_current_user_email] JWT decode error: {type(e).__name__}: {str(e)}")
        raise credentials_exception

def get_current_user_context(token: str = Depends(oauth2_scheme)) -> tuple[str, str]:
    """
    Returns both the user email and the JWT token for use in tool calls.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"🔐 Attempting to decode JWT token (length: {len(token) if token else 0})")
        print(f"🔑 Using SECRET_KEY (length: {len(SECRET_KEY)})")
        print(f"📝 Token preview: {token[:20]}..." if token and len(token) > 20 else "⚠️ Token too short or missing")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            print("❌ Email (sub) not found in JWT payload!")
            print(f"Payload keys: {list(payload.keys())}")
            raise credentials_exception
        
        print(f"✅ JWT decoded successfully for user: {email}")
        return email, token
    except JWTError as e:
        print(f"❌ JWT decode error: {type(e).__name__}: {str(e)}")
        print(f"Token that failed: {token[:50]}..." if token and len(token) > 50 else f"Token: {token}")
        raise credentials_exception