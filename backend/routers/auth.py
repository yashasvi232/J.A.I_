from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from bson import ObjectId

from database import get_database

router = APIRouter()
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Convert ObjectId to string for JSON serialization
    user["id"] = str(user["_id"])
    user.pop("_id")
    user.pop("password_hash", None)  # Remove sensitive data
    
    return user

@router.post("/login")
async def login(login_data: dict):
    """Authenticate user and return JWT token"""
    try:
        email = login_data.get("email", "").strip().lower()
        password = login_data.get("password", "")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        db = get_database()
        user = await db.users.find_one({"email": email})
        
        if not user or not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user["_id"])}, expires_delta=access_token_expires
        )
        
        # Prepare user response
        user_response = {
            "id": str(user["_id"]),
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "user_type": user["user_type"],
            "is_verified": user.get("is_verified", False),
            "is_active": user.get("is_active", True)
        }
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@router.post("/signup")
async def signup(signup_data: dict):
    """Register a new user"""
    try:
        # Extract and validate data
        email = signup_data.get("email", "").strip().lower()
        password = signup_data.get("password", "")
        full_name = signup_data.get("full_name", "").strip()
        user_type = signup_data.get("user_type", "client")
        
        if not email or not password or not full_name:
            raise HTTPException(status_code=400, detail="Email, password, and full name are required")
        
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Split full name
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        db = get_database()
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=409, detail="User with this email already exists")
        
        # Create user document
        user_doc = {
            "email": email,
            "password_hash": get_password_hash(password),
            "first_name": first_name,
            "last_name": last_name,
            "user_type": user_type,
            "phone": signup_data.get("phone", ""),
            "profile_image_url": None,
            "is_verified": False,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Add lawyer-specific fields
        if user_type == "lawyer":
            bar_number = signup_data.get("bar_number", "").strip()
            if not bar_number:
                raise HTTPException(status_code=400, detail="Bar Association ID is required for lawyers")
            user_doc["bar_number"] = bar_number
            user_doc["bar_state"] = signup_data.get("bar_state", "")
        
        # Insert user
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Create lawyer profile if needed
        if user_type == "lawyer":
            lawyer_profile = {
                "user_id": result.inserted_id,
                "bar_number": bar_number,
                "bar_state": signup_data.get("bar_state", ""),
                "law_firm": signup_data.get("law_firm", ""),
                "years_experience": int(signup_data.get("years_experience", 0)),
                "hourly_rate": float(signup_data.get("hourly_rate", 0)) if signup_data.get("hourly_rate") else None,
                "bio": signup_data.get("bio", ""),
                "specializations": signup_data.get("specializations", []),
                "education": [],
                "certifications": [],
                "languages": ["English"],
                "availability_status": "available",
                "rating": 0.0,
                "total_reviews": 0,
                "total_cases": 0,
                "success_rate": 0.0,
                "ai_match_score": 0.0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.lawyers.insert_one(lawyer_profile)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id}, expires_delta=access_token_expires
        )
        
        # Prepare response
        user_response = {
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "user_type": user_type,
            "is_verified": False,
            "is_active": True
        }
        
        return {
            "message": "User registered successfully",
            "user": user_response,
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Logged out successfully"}