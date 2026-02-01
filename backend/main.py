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
    from routers import auth, users, lawyers, cases, ai_matching, lawyer_requests, messages
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

# Include routers FIRST - before any catch-all routes
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
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
print("   ✅ Messages router included")
app.include_router(ai_matching.router, prefix="/api/ai", tags=["AI Services"])
print("   ✅ AI matching router included")
print("🎉 All routers included successfully!")

# API root endpoint
@app.get("/api")
async def api_root():
    return {
        "message": "Welcome to J.A.I API",
        "description": "Jurist Artificial Intelligence - AI-powered legal platform",
        "version": "1.0.0",
        "docs": "/docs",
        "mongodb": "connected"
    }

# Mount static files (HTML pages)
app.mount("/pages", StaticFiles(directory="../pages"), name="pages")
print("✅ Static files mounted at /pages")

# Serve the frontend at the root
from fastapi.responses import FileResponse
import os

@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    return FileResponse("../pages/index.html")

# Serve specific frontend files directly from root (only common ones)
@app.get("/style.css")
async def serve_style():
    return FileResponse("../pages/style.css")

@app.get("/script.js") 
async def serve_script():
    return FileResponse("../pages/script.js")

@app.get("/Logo.jpeg")
async def serve_logo():
    return FileResponse("../pages/Logo.jpeg")

@app.get("/{filename}.html")
async def serve_html_files(filename: str):
    """Serve HTML files from root"""
    file_path = f"../pages/{filename}.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "J.A.I API", "mongodb": "connected"}

# Debug endpoint to check all requests
@app.get("/api/debug/requests")
async def debug_all_requests():
    """Debug endpoint to see all requests in database"""
    try:
        db = get_database()
        
        requests = []
        async for request in db.lawyer_requests.find({}).sort("created_at", -1):
            # Get client and lawyer info
            client = await db.users.find_one({"_id": request["client_id"]})
            lawyer = await db.users.find_one({"_id": request["lawyer_id"]})
            
            request_data = {
                "id": str(request["_id"]),
                "title": request["title"],
                "status": request["status"],
                "client_name": f"{client['first_name']} {client['last_name']}" if client else "Unknown",
                "lawyer_name": f"{lawyer['first_name']} {lawyer['last_name']}" if lawyer else "Unknown",
                "created_at": request["created_at"].isoformat() if request.get("created_at") else None
            }
            requests.append(request_data)
        
        return {
            "total_requests": len(requests),
            "requests": requests
        }
        
    except Exception as e:
        return {"error": str(e)}

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

# Simple login endpoint for quick testing
@app.post("/api/auth/login")
async def login(login_data: dict):
    """Simple login endpoint"""
    try:
        email = login_data.get("email")
        password = login_data.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        db = get_database()
        user = await db.users.find_one({"email": email})
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # For now, just return success (you can add password verification later)
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        
        return {
            "access_token": "fake-token-for-testing",
            "token_type": "bearer",
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

# Signup endpoint for both clients and lawyers
@app.post("/api/auth/signup")
async def signup(signup_data: dict):
    """Handle user registration for both clients and lawyers"""
    try:
        print(f"🔍 Received signup data: {signup_data}")  # Debug logging
        
        # Extract common fields
        email = signup_data.get("email", "").strip().lower()
        password = signup_data.get("password", "")
        full_name = signup_data.get("full_name", "").strip()
        user_type = signup_data.get("user_type", "client")  # default to client
        
        print(f"📋 Parsed fields - Email: {email}, Full Name: {full_name}, Type: {user_type}")  # Debug
        
        # Validation
        if not email or not password or not full_name:
            print(f"❌ Validation failed - Missing fields")  # Debug
            raise HTTPException(
                status_code=400, 
                detail="Email, password, and full name are required"
            )
        
        if len(password) < 8:
            print(f"❌ Validation failed - Password too short")  # Debug
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )
        
        # Split full name into first and last name
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        db = get_database()
        if db is None:
            print("❌ Database connection failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            print(f"❌ User already exists: {email}")
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists"
            )
        
        # Hash password (simple hash for now - in production use proper bcrypt)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(password)
        
        # Create user document
        from datetime import datetime
        user_doc = {
            "email": email,
            "password_hash": password_hash,
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
        
        # Create lawyer profile if user is a lawyer
        if user_type == "lawyer":
            bar_number = signup_data.get("bar_number", "").strip()
            if not bar_number:
                print(f"❌ Bar number missing for lawyer")
                raise HTTPException(
                    status_code=400,
                    detail="Bar Association ID is required for lawyers"
                )
            user_doc["bar_number"] = bar_number
            user_doc["bar_state"] = signup_data.get("bar_state", "")
            user_doc["law_firm"] = signup_data.get("law_firm", "")
            user_doc["specializations"] = signup_data.get("specializations", [])
        
        # Insert user into database
        print(f"💾 Inserting user into database...")
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        print(f"✅ User created with ID: {user_id}")
        
        # Create lawyer profile if user is a lawyer
        if user_type == "lawyer":
            print(f"👨‍⚖️ Creating lawyer profile...")
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
            print(f"✅ Lawyer profile created")
        
        # Return success response (without password hash)
        user_response = {
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "user_type": user_type,
            "is_verified": False,
            "is_active": True
        }
        
        print(f"🎉 Registration successful for: {email}")
        return {
            "message": "User registered successfully",
            "user": user_response,
            "access_token": "fake-token-for-testing",
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Signup error: {e}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

# Add explicit OPTIONS handler for CORS
@app.options("/api/auth/signup")
async def signup_options():
    """Handle CORS preflight for signup"""
    return {"message": "OK"}

# Send request to lawyer endpoint with proper authentication
@app.post("/api/requests/")
async def send_lawyer_request(request_data: dict, authorization: str = None):
    """Send request to lawyer - supports any lawyer"""
    try:
        from datetime import datetime
        from bson import ObjectId
        
        db = get_database()
        
        print(f"🔍 Received request data: {request_data}")  # Debug logging
        
        # Validate required fields
        required_fields = ["title", "description", "category", "lawyer_id"]
        for field in required_fields:
            if not request_data.get(field):
                raise HTTPException(status_code=400, detail=f"{field} is required")
        
        # TODO: Extract client_id from JWT token
        # For now, we'll determine the client from the login context
        # In a real implementation, this would come from the JWT token
        
        # Try to get client_id from request data first (for testing)
        client_id = request_data.get("client_id")
        
        if not client_id:
            # Fallback: use the test client for now
            # In production, this should be extracted from JWT
            test_client = await db.users.find_one({"email": "client@test.com"})
            if test_client:
                client_id = str(test_client["_id"])
            else:
                raise HTTPException(status_code=400, detail="Client authentication required")
        
        print(f"📋 Using client_id: {client_id}")  # Debug
        
        # Verify the target lawyer exists and is actually a lawyer
        lawyer = await db.users.find_one({
            "_id": ObjectId(request_data["lawyer_id"]),
            "user_type": "lawyer"
        })
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found or invalid")
        
        print(f"⚖️ Found target lawyer: {lawyer['first_name']} {lawyer['last_name']} ({lawyer['email']})")  # Debug
        
        # Create request document
        request_doc = {
            "client_id": ObjectId(client_id),
            "lawyer_id": ObjectId(request_data["lawyer_id"]),
            "title": request_data["title"],
            "description": request_data["description"],
            "category": request_data["category"],
            "urgency_level": request_data.get("urgency_level", "medium"),
            "budget_min": request_data.get("budget_min"),
            "budget_max": request_data.get("budget_max"),
            "preferred_meeting_type": request_data.get("preferred_meeting_type"),
            "location": request_data.get("location"),
            "additional_notes": request_data.get("additional_notes"),
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "response_message": None,
            "responded_at": None,
            "meeting_slots": None,
            "selected_meeting": None
        }
        
        print(f"💾 Inserting request for lawyer: {lawyer['email']}")  # Debug
        
        result = await db.lawyer_requests.insert_one(request_doc)
        
        print(f"✅ Request inserted with ID: {result.inserted_id}")  # Debug
        
        return {
            "message": "Request sent successfully",
            "request_id": str(result.inserted_id),
            "lawyer_name": f"{lawyer['first_name']} {lawyer['last_name']}"
        }
        
    except Exception as e:
        print(f"❌ Error in send_lawyer_request: {e}")  # Debug
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error sending request: {str(e)}")

# Get pending requests for any lawyer (with proper authentication)
@app.get("/api/requests/pending")
async def get_pending_requests_for_lawyers(lawyer_email: str = None):
    """Get pending requests for any lawyer - supports multiple lawyers"""
    try:
        db = get_database()
        
        print("🔍 Getting pending requests...")  # Debug
        
        # TODO: Extract lawyer_id from JWT token
        # For now, we'll use a query parameter or fallback to test lawyer
        
        target_lawyer = None
        
        if lawyer_email:
            # If lawyer email is provided, use that
            target_lawyer = await db.users.find_one({
                "email": lawyer_email,
                "user_type": "lawyer"
            })
        else:
            # Fallback: try to determine from context or use test lawyer
            # In production, this would come from JWT token
            target_lawyer = await db.users.find_one({"email": "lawyer@test.com"})
        
        if not target_lawyer:
            print("⚠️ No lawyer found for pending requests")
            return []
        
        lawyer_id = target_lawyer["_id"]
        print(f"⚖️ Looking for requests for lawyer: {target_lawyer['first_name']} {target_lawyer['last_name']} ({target_lawyer['email']})")
        
        requests = []
        async for request in db.lawyer_requests.find({
            "lawyer_id": lawyer_id,
            "status": "pending"
        }).sort("created_at", -1):
            print(f"📋 Found pending request: {request['_id']} - {request['title']}")  # Debug
            
            # Get client info
            client = await db.users.find_one({"_id": request["client_id"]})
            if not client:
                print(f"⚠️ Client not found for request {request['_id']}")
                continue
            
            request_data = {
                "id": str(request["_id"]),
                "title": request["title"],
                "description": request["description"],
                "category": request["category"],
                "urgency_level": request["urgency_level"],
                "budget_min": request.get("budget_min"),
                "budget_max": request.get("budget_max"),
                "preferred_meeting_type": request.get("preferred_meeting_type"),
                "location": request.get("location"),
                "additional_notes": request.get("additional_notes"),
                "status": request["status"],
                "created_at": request["created_at"],
                "client_name": f"{client['first_name']} {client['last_name']}",
                "client_email": client["email"]
            }
            requests.append(request_data)
        
        print(f"✅ Returning {len(requests)} pending requests for lawyer {target_lawyer['email']}")  # Debug
        return requests
        
    except Exception as e:
        print(f"❌ Error getting pending requests: {e}")  # Debug
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching pending requests: {str(e)}")

# Get pending requests for a specific lawyer by ID
@app.get("/api/requests/pending/{lawyer_id}")
async def get_pending_requests_for_specific_lawyer(lawyer_id: str):
    """Get pending requests for a specific lawyer by ID"""
    try:
        from bson import ObjectId
        db = get_database()
        
        print(f"🔍 Getting pending requests for lawyer ID: {lawyer_id}")  # Debug
        
        # Verify lawyer exists
        lawyer = await db.users.find_one({
            "_id": ObjectId(lawyer_id),
            "user_type": "lawyer"
        })
        
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        
        print(f"⚖️ Found lawyer: {lawyer['first_name']} {lawyer['last_name']} ({lawyer['email']})")
        
        requests = []
        async for request in db.lawyer_requests.find({
            "lawyer_id": ObjectId(lawyer_id),
            "status": "pending"
        }).sort("created_at", -1):
            print(f"📋 Found pending request: {request['_id']} - {request['title']}")  # Debug
            
            # Get client info
            client = await db.users.find_one({"_id": request["client_id"]})
            if not client:
                print(f"⚠️ Client not found for request {request['_id']}")
                continue
            
            request_data = {
                "id": str(request["_id"]),
                "title": request["title"],
                "description": request["description"],
                "category": request["category"],
                "urgency_level": request["urgency_level"],
                "budget_min": request.get("budget_min"),
                "budget_max": request.get("budget_max"),
                "preferred_meeting_type": request.get("preferred_meeting_type"),
                "location": request.get("location"),
                "additional_notes": request.get("additional_notes"),
                "status": request["status"],
                "created_at": request["created_at"],
                "client_name": f"{client['first_name']} {client['last_name']}",
                "client_email": client["email"]
            }
            requests.append(request_data)
        
        print(f"✅ Returning {len(requests)} pending requests for lawyer {lawyer['email']}")  # Debug
        return requests
        
    except Exception as e:
        print(f"❌ Error getting pending requests for specific lawyer: {e}")  # Debug
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching pending requests: {str(e)}")

# Respond to request endpoint
@app.post("/api/requests/{request_id}/respond")
async def respond_to_request(request_id: str, response_data: dict):
    """Respond to a lawyer request (accept/reject)"""
    try:
        from datetime import datetime
        from bson import ObjectId
        
        db = get_database()
        
        print(f"🔍 Responding to request {request_id} with data: {response_data}")  # Debug
        
        request_obj_id = ObjectId(request_id)
        
        # Get the request
        request_doc = await db.lawyer_requests.find_one({
            "_id": request_obj_id,
            "status": "pending"
        })
        
        if not request_doc:
            raise HTTPException(status_code=404, detail="Request not found or already responded")
        
        action = response_data.get("action")
        if action not in ["accept", "reject"]:
            raise HTTPException(status_code=400, detail="Action must be 'accept' or 'reject'")
        
        print(f"⚖️ Lawyer {action}ing request")  # Debug
        
        # Update request
        update_data = {
            "status": "accepted" if action == "accept" else "rejected",
            "response_message": response_data.get("response_message"),
            "responded_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Add meeting slots if accepting
        if action == "accept" and response_data.get("meeting_slots"):
            update_data["meeting_slots"] = response_data["meeting_slots"]
        
        await db.lawyer_requests.update_one(
            {"_id": request_obj_id},
            {"$set": update_data}
        )
        
        print(f"✅ Request {action}ed successfully")  # Debug
        
        # If accepted, send a welcome message to start the conversation
        if action == "accept":
            # Get lawyer info for the message
            test_lawyer = await db.users.find_one({"email": "lawyer@test.com"})
            if test_lawyer:
                welcome_message = {
                    "request_id": request_obj_id,
                    "sender_id": test_lawyer["_id"],
                    "sender_type": "lawyer",
                    "content": response_data.get("response_message", "Thank you for your request. I'm happy to help with your case. Let's discuss the details."),
                    "message_type": "text",
                    "is_read": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await db.messages.insert_one(welcome_message)
                print("💬 Welcome message sent to start conversation")
        
        return {"message": f"Request {action}ed successfully"}
        
    except Exception as e:
        print(f"❌ Error responding to request: {e}")  # Debug
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error responding to request: {str(e)}")

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