#!/usr/bin/env python3
"""
Create test users for J.A.I platform
This script creates sample client and lawyer accounts for testing
"""

import asyncio
import sys
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "jai_database")

async def create_test_users():
    """Create test users in the database"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("🔗 Connected to MongoDB")
    
    # Test users data
    test_users = [
        {
            "email": "client@test.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Client",
            "phone": "+1234567890",
            "user_type": "client"
        },
        {
            "email": "lawyer@test.com", 
            "password": "password123",
            "first_name": "Sarah",
            "last_name": "Attorney",
            "phone": "+1234567891",
            "user_type": "lawyer"
        },
        {
            "email": "demo.client@jai.com",
            "password": "demo123",
            "first_name": "Demo",
            "last_name": "Client",
            "phone": "+1234567892",
            "user_type": "client"
        },
        {
            "email": "demo.lawyer@jai.com",
            "password": "demo123", 
            "first_name": "Demo",
            "last_name": "Lawyer",
            "phone": "+1234567893",
            "user_type": "lawyer"
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data["email"]})
        
        if existing_user:
            print(f"⚠️  User {user_data['email']} already exists, skipping...")
            created_users.append({
                "email": user_data["email"],
                "password": user_data["password"],
                "user_type": user_data["user_type"],
                "status": "exists"
            })
            continue
        
        # Hash password
        password_hash = pwd_context.hash(user_data["password"])
        
        # Create user document
        user_doc = {
            "email": user_data["email"],
            "password_hash": password_hash,
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "phone": user_data.get("phone"),
            "user_type": user_data["user_type"],
            "profile_image_url": None,
            "is_verified": True,  # Auto-verify test users
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        result = await db.users.insert_one(user_doc)
        
        print(f"✅ Created {user_data['user_type']}: {user_data['email']}")
        
        created_users.append({
            "email": user_data["email"],
            "password": user_data["password"],
            "user_type": user_data["user_type"],
            "user_id": str(result.inserted_id),
            "status": "created"
        })
        
        # Create lawyer profile if user is a lawyer
        if user_data["user_type"] == "lawyer":
            lawyer_profile = {
                "user_id": result.inserted_id,
                "bar_number": f"BAR{result.inserted_id}",
                "bar_state": "CA",
                "law_firm": f"{user_data['first_name']} {user_data['last_name']} Law Firm",
                "years_experience": 5,
                "hourly_rate": 350.0,
                "bio": f"Experienced lawyer specializing in various legal matters. {user_data['first_name']} has been practicing law for several years.",
                "specializations": ["Family Law", "Corporate Law", "Real Estate"],
                "education": [
                    {
                        "school": "Harvard Law School",
                        "degree": "J.D.",
                        "year": 2018,
                        "description": "Juris Doctor with honors"
                    }
                ],
                "certifications": [],
                "languages": ["English"],
                "availability_status": "available",
                "rating": 4.5,
                "total_reviews": 10,
                "total_cases": 25,
                "success_rate": 92.0,
                "ai_match_score": 85.0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db.lawyers.insert_one(lawyer_profile)
            print(f"✅ Created lawyer profile for {user_data['email']}")
    
    # Create some sample cases
    sample_cases = [
        {
            "title": "Family Law Consultation",
            "description": "Need help with divorce proceedings and child custody arrangements.",
            "category": "Family Law",
            "status": "open",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "title": "Contract Review",
            "description": "Business contract needs legal review before signing.",
            "category": "Corporate Law", 
            "status": "in-progress",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "title": "Real Estate Transaction",
            "description": "Legal assistance needed for property purchase.",
            "category": "Real Estate",
            "status": "closed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Find a client user to assign cases to
    client_user = next((u for u in created_users if u["user_type"] == "client"), None)
    if client_user and client_user.get("user_id"):
        from bson import ObjectId
        for case_data in sample_cases:
            case_data["client_id"] = ObjectId(client_user["user_id"])
            await db.cases.insert_one(case_data)
        print(f"✅ Created {len(sample_cases)} sample cases")
    
    # Close connection
    client.close()
    
    return created_users

def print_login_credentials(users):
    """Print login credentials for easy access"""
    print("\n" + "=" * 60)
    print("🔑 TEST LOGIN CREDENTIALS")
    print("=" * 60)
    
    clients = [u for u in users if u["user_type"] == "client"]
    lawyers = [u for u in users if u["user_type"] == "lawyer"]
    
    if clients:
        print("\n👤 CLIENT ACCOUNTS:")
        print("-" * 30)
        for client in clients:
            print(f"Email:    {client['email']}")
            print(f"Password: {client['password']}")
            print(f"Status:   {client['status']}")
            print()
    
    if lawyers:
        print("⚖️  LAWYER ACCOUNTS:")
        print("-" * 30)
        for lawyer in lawyers:
            print(f"Email:    {lawyer['email']}")
            print(f"Password: {lawyer['password']}")
            print(f"Status:   {lawyer['status']}")
            print()
    
    print("📋 USAGE INSTRUCTIONS:")
    print("-" * 30)
    print("1. Start the backend server:")
    print("   cd backend && python start_server.py")
    print()
    print("2. Open the frontend:")
    print("   - Client Login: pages/client-login.html")
    print("   - Lawyer Login: pages/lawyer-login.html")
    print()
    print("3. Use the credentials above to login")
    print("4. You'll be redirected to the appropriate dashboard")
    print()
    print("🌐 URLs:")
    print("   Frontend: http://localhost:5500 (if using live server)")
    print("   Backend:  http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")

async def main():
    """Main function"""
    print("🚀 Creating test users for J.A.I platform...")
    print()
    
    try:
        users = await create_test_users()
        print_login_credentials(users)
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        print("\nMake sure MongoDB is running and accessible.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())