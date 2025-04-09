from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from .utils import verify_password, get_password_hash
from .mongodb import get_user_by_email, create_user

# JWT settings
SECRET_KEY = "YOUR_SECRET_KEY"  # In production, use a secure random key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Router
auth_router = APIRouter()

# Helper functions
async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    print(f"Authenticating user: {email}")
    user = await get_user_by_email(email)
    print(f"User found: {user is not None}")
    if not user or not user.get("hashed_password"):
        print("User not found or no password")
        return None
    password_verified = verify_password(password, user.get("hashed_password"))
    print(f"Password verification result: {password_verified}")
    if not password_verified:
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Endpoints
@auth_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Login attempt with username: {form_data.username}")
    try:
        user = await authenticate_user(form_data.username, form_data.password)
        print(f"Authentication result: {user is not None}")
        if not user:
            print("Authentication failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.get("email"), "is_admin": user.get("is_admin", False)},
            expires_delta=access_token_expires
        )
        print(f"Generated token for user: {user.get('email')}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Error in login_for_access_token: {str(e)}")
        raise

@auth_router.post("/register")
async def register_user(email: str, password: str, full_name: str, is_admin: bool = False):
    user = await get_user_by_email(email=email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(password)
    
    user_data = {
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "is_admin": is_admin,
        "is_active": True,
        "assigned_channels": []
    }
    
    created_user = await create_user(user_data)
    return created_user

@auth_router.get("/me")
async def read_users_me(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    return current_user
