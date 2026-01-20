#!/usr/bin/env python3
"""
Simple FastAPI server for J.A.I Platform (No MongoDB required)
This allows immediate testing of login functionality
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="J.A.I Platform API (Simple Mode)",
    description="Legal consultation platform API - Simple mode without MongoDB",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    user_type: str
    is_active: bool = True

# In-memory user storage (for testing without MongoDB)
MOCK_USERS = {
    "client@test.com": {
        "id": "client_1",
        "email": "client@test.com",
        "password_hash": pwd_context.hash("password123"),
        "first_name": "John",
        "last_name": "Client",
        "phone": "+1234567890",
        "user_type": "client",
        "is_verified": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    "lawyer@test.com": {
        "id": "lawyer_1",
        "email": "lawyer@test.com",
        "password_hash": pwd_context.hash("password123"),
        "first_name": "Sarah",
        "last_name": "Attorney",
        "phone": "+1234567891",
        "user_type": "lawyer",
        "is_verified": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    "demo.client@jai.com": {
        "id": "demo_client_1",
        "email": "demo.client@jai.com",
        "password_hash": pwd_context.hash("demo123"),
        "first_name": "Demo",
        "last_name": "Client",
        "phone": "+1234567892",
        "user_type": "client",
        "is_verified": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    "demo.lawyer@jai.com": {
        "id": "demo_lawyer_1",
        "email": "demo.lawyer@jai.com",
        "password_hash": pwd_context.hash("demo123"),
        "first_name": "Demo",
        "last_name": "Lawyer",
        "phone": "+1234567893",
        "user_type": "lawyer",
        "is_verified": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "J.A.I Platform API - Simple Mode",
        "status": "running",
        "mode": "no-mongodb",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mode": "simple"}

@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    """Mock login endpoint that works without MongoDB"""
    email = login_data.email
    password = login_data.password
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Find user in mock data
    user = MOCK_USERS.get(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    # Return user data without password hash
    user_response = {k: v for k, v in user.items() if k != "password_hash"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@app.get("/api/users")
async def get_users():
    """Get all mock users (for testing)"""
    users = []
    for user in MOCK_USERS.values():
        user_data = {k: v for k, v in user.items() if k != "password_hash"}
        users.append(user_data)
    return {"users": users}

# Mock lawyer data for dashboard
@app.get("/api/lawyers")
async def get_lawyers():
    """Get mock lawyer data"""
    return {
        "lawyers": [
            {
                "id": "lawyer_1",
                "name": "Sarah Attorney",
                "specializations": ["Family Law", "Corporate Law"],
                "rating": 4.5,
                "experience": 5,
                "hourly_rate": 350
            },
            {
                "id": "demo_lawyer_1", 
                "name": "Demo Lawyer",
                "specializations": ["Real Estate", "Criminal Law"],
                "rating": 4.8,
                "experience": 8,
                "hourly_rate": 400
            }
        ]
    }

# Mock case data for dashboard
@app.get("/api/cases")
async def get_cases():
    """Get mock case data"""
    return {
        "cases": [
            {
                "id": "case_1",
                "title": "Family Law Consultation",
                "description": "Need help with divorce proceedings",
                "status": "open",
                "category": "Family Law"
            },
            {
                "id": "case_2",
                "title": "Contract Review",
                "description": "Business contract needs review",
                "status": "in-progress", 
                "category": "Corporate Law"
            }
        ]
    }

# Mock dashboard stats
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get mock dashboard statistics"""
    return {
        "total_cases": 15,
        "active_cases": 8,
        "completed_cases": 7,
        "total_lawyers": 25,
        "available_lawyers": 18
    }

if __name__ == "__main__":
    print("🚀 Starting J.A.I Platform - Simple Mode")
    print("=" * 50)
    print("✅ No MongoDB required!")
    print("✅ Mock authentication enabled")
    print("✅ CORS configured for frontend")
    print()
    
    print("🔑 TEST LOGIN CREDENTIALS")
    print("-" * 30)
    print("Client: client@test.com / password123")
    print("Lawyer: lawyer@test.com / password123")
    print("Demo Client: demo.client@jai.com / demo123")
    print("Demo Lawyer: demo.lawyer@jai.com / demo123")
    print()
    
    print("🌐 Server will start at:")
    print("   Backend:  http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print()
    print("📁 Frontend files are in the 'pages' directory")
    print("   Open pages/client-login.html or pages/lawyer-login.html")
    print()
    
    # Start the server
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )