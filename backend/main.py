from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
try:
    from routers import auth, users, lawyers, cases, ai_matching, lawyer_requests, chat
    print("✅ All routers imported successfully")
except Exception as e:
    print(f"❌ Router import error: {e}")
    raise

from database import connect_to_mongo, close_mongo_connection, get_database

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    
    # Create test users if they don't exist
    await create_initial_users()
    
    yield
    # Shutdown
    await close_mongo_connection()

async def create_initial_users():
    """Create test users if database is empty"""
    try:
        db = get_database()
        if db is None:
            return
            
        # Check if users exist
        user_count = await db.users.count_documents({})
        if user_count > 0:
            print(f"✅ Database has {user_count} users")
            return
            
        print("📝 Creating initial test users...")
        
        from passlib.context import CryptContext
        from datetime import datetime
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Test users
        test_users = [
            {
                "email": "client@test.com",
                "password": "password123",
                "first_name": "Test",
                "last_name": "Client",
                "user_type": "client"
            },
            {
                "email": "lawyer@test.com", 
                "password": "password123",
                "first_name": "Test",
                "last_name": "Lawyer",
                "user_type": "lawyer",
                "bar_number": "BAR123456"
            }
        ]
        
        for user_data in test_users:
            password = user_data.pop("password")
            user_data["password_hash"] = pwd_context.hash(password)
            user_data["phone"] = ""
            user_data["is_verified"] = False
            user_data["is_active"] = True
            user_data["created_at"] = datetime.utcnow()
            user_data["updated_at"] = datetime.utcnow()
            
            result = await db.users.insert_one(user_data)
            
            # Create lawyer profile if needed
            if user_data["user_type"] == "lawyer":
                lawyer_profile = {
                    "user_id": result.inserted_id,
                    "bar_number": user_data.get("bar_number", ""),
                    "bar_state": "Test State",
                    "specializations": ["General Practice"],
                    "availability_status": "available",
                    "rating": 4.5,
                    "created_at": datetime.utcnow()
                }
                await db.lawyers.insert_one(lawyer_profile)
        
        print("✅ Test users created successfully")
        
    except Exception as e:
        print(f"⚠️ Error creating test users: {e}")

# Create FastAPI app
app = FastAPI(
    title="J.A.I API",
    description="Jurist Artificial Intelligence - AI-powered legal platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
print("📋 Including API routers...")
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
print("   ✅ Auth router included")
app.include_router(users.router, prefix="/api/users", tags=["Users"])
print("   ✅ Users router included")
app.include_router(lawyers.router, prefix="/api/lawyers", tags=["Lawyers"])
print("   ✅ Lawyers router included")
app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
print("   ✅ Cases router included")
app.include_router(lawyer_requests.router, prefix="/api/requests", tags=["Lawyer Requests"])
print("   ✅ Lawyer requests router included")
app.include_router(ai_matching.router, prefix="/api/ai", tags=["AI Services"])
print("   ✅ AI matching router included")
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
print("   ✅ Chat router included")
print("🎉 All routers included successfully!")

# Mount static files (HTML pages)
app.mount("/pages", StaticFiles(directory="pages"), name="pages")
print("✅ Static files mounted at /pages")

@app.get("/")
async def root():
    return {
        "message": "Welcome to J.A.I API",
        "description": "Jurist Artificial Intelligence - AI-powered legal platform",
        "version": "1.0.0",
        "docs": "/docs",
        "mongodb": "connected"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "J.A.I API", "mongodb": "connected"}

# Simple lawyers endpoint for quick testing
@app.get("/api/lawyers")
async def get_lawyers():
    """Get all lawyers from the database"""
    try:
        db = get_database()
        
        lawyers = []
        cursor = db.users.find({"user_type": "lawyer"})
        async for lawyer in cursor:
            lawyer["_id"] = str(lawyer["_id"])
            lawyer.pop("password_hash", None)  # Remove sensitive data
            lawyers.append(lawyer)
        
        return {"lawyers": lawyers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lawyers: {str(e)}")

# Add explicit OPTIONS handler for CORS
@app.options("/api/auth/signup")
async def signup_options():
    """Handle CORS preflight for signup"""
    return {"message": "OK"}

# Send request to lawyer endpoint
@app.post("/api/requests/send")
async def send_lawyer_request(request_data: dict):
    """Send request to lawyer"""
    try:
        from datetime import datetime
        from bson import ObjectId
        
        db = get_database()
        
        # Create request document
        request_doc = {
            "client_id": ObjectId(request_data["client_id"]),
            "lawyer_id": ObjectId(request_data["lawyer_id"]),
            "title": request_data["title"],
            "description": request_data["description"],
            "category": request_data["category"],
            "urgency_level": request_data.get("urgency_level", "medium"),
            "budget_min": request_data.get("budget_min"),
            "budget_max": request_data.get("budget_max"),
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        result = await db.lawyer_requests.insert_one(request_doc)
        
        return {
            "message": "Request sent successfully",
            "request_id": str(result.inserted_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending request: {str(e)}")

# Get lawyers with profiles - dedicated endpoint to avoid router conflicts
@app.get("/api/public/lawyers")
async def get_all_lawyers_public():
    """Get all lawyers with their profiles - public endpoint"""
    try:
        db = get_database()
        
        # Join users and lawyers collections
        pipeline = [
            {
                "$lookup": {
                    "from": "lawyers",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "profile"
                }
            },
            {
                "$match": {
                    "user_type": "lawyer",
                    "profile": {"$ne": []}
                }
            }
        ]
        
        lawyers = []
        async for lawyer in db.users.aggregate(pipeline):
            profile = lawyer["profile"][0] if lawyer["profile"] else {}
            
            lawyer_data = {
                "id": str(lawyer["_id"]),
                "first_name": lawyer["first_name"],
                "last_name": lawyer["last_name"],
                "email": lawyer["email"],
                "specializations": profile.get("specializations", []),
                "rating": profile.get("rating", 0.0),
                "years_experience": profile.get("years_experience", 0),
                "hourly_rate": profile.get("hourly_rate"),
                "law_firm": profile.get("law_firm", ""),
                "bio": profile.get("bio", ""),
                "availability_status": profile.get("availability_status", "available")
            }
            lawyers.append(lawyer_data)
        
        return {"lawyers": lawyers}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lawyers: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting J.A.I Platform with MongoDB")
    print("=" * 50)
    print("✅ MongoDB connection enabled")
    print("✅ Full API endpoints available")
    print("✅ CORS configured for frontend")
    print()
    
    # Get port from environment variable (for deployment) or use default
    port = int(os.getenv("PORT", 8001))
    
    # Check if running in production (Railway sets RAILWAY_ENVIRONMENT)
    is_production = os.getenv("RAILWAY_ENVIRONMENT") is not None
    
    print("🌐 Server will start at:")
    print(f"   Backend:  http://localhost:{port}")
    print(f"   API Docs: http://localhost:{port}/docs")
    print(f"   Environment: {'Production' if is_production else 'Development'}")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,  # Disable reload in production
        log_level="info"
    )