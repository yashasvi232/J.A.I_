#!/usr/bin/env python3
"""
Create test lawyer requests for demonstration
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

async def create_test_requests():
    """Create some test lawyer requests"""
    
    print("🔗 Creating test lawyer requests...")
    
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "jai_database")
    
    client = AsyncIOMotorClient(mongodb_url)
    db = client[database_name]
    
    try:
        # Get a client and lawyer
        client_user = await db.users.find_one({"user_type": "client"})
        lawyer_user = await db.users.find_one({"user_type": "lawyer"})
        
        if not client_user or not lawyer_user:
            print("❌ Need at least one client and one lawyer to create test requests")
            return
        
        # Create test requests
        test_requests = [
            {
                "title": "Property Purchase Legal Review",
                "description": "I need legal assistance for reviewing a property purchase agreement. The property is worth ₹50 lakhs and I want to ensure all legal aspects are covered before signing.",
                "category": "Property Law",
                "urgency_level": "medium",
                "budget_min": 15000,
                "budget_max": 25000,
                "preferred_meeting_type": "in-person",
                "location": "Mumbai, Maharashtra",
                "additional_notes": "Property is in Bandra area. Need to complete within 2 weeks.",
                "client_id": ObjectId(client_user["_id"]),
                "lawyer_id": ObjectId(lawyer_user["_id"]),
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "title": "Employment Contract Dispute",
                "description": "My employer is not following the terms mentioned in my employment contract regarding overtime pay and leave policies. I need legal advice on how to proceed.",
                "category": "Labour and Employment Law",
                "urgency_level": "high",
                "budget_min": 10000,
                "budget_max": 20000,
                "preferred_meeting_type": "online",
                "additional_notes": "Have all employment documents ready. Prefer evening consultations.",
                "client_id": ObjectId(client_user["_id"]),
                "lawyer_id": ObjectId(lawyer_user["_id"]),
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Insert test requests
        for request in test_requests:
            await db.lawyer_requests.insert_one(request)
        
        print(f"✅ Created {len(test_requests)} test lawyer requests")
        
        # Show summary
        total_requests = await db.lawyer_requests.count_documents({})
        pending_requests = await db.lawyer_requests.count_documents({"status": "pending"})
        
        print(f"\n📊 Request Summary:")
        print(f"   Total requests: {total_requests}")
        print(f"   Pending requests: {pending_requests}")
        print(f"   Client: {client_user['first_name']} {client_user['last_name']}")
        print(f"   Lawyer: {lawyer_user['first_name']} {lawyer_user['last_name']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_test_requests())