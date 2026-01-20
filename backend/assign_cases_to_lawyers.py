#!/usr/bin/env python3
"""
Assign some test cases to lawyers so they appear in the lawyer dashboard
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

async def assign_cases_to_lawyers():
    """Assign existing cases to lawyers for testing"""
    
    print("🔗 Assigning test cases to lawyers...")
    
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "jai_database")
    
    client = AsyncIOMotorClient(mongodb_url)
    db = client[database_name]
    
    try:
        # Get all lawyers
        lawyers = await db.users.find({"user_type": "lawyer"}).to_list(length=100)
        print(f"📋 Found {len(lawyers)} lawyers")
        
        # Get all cases that don't have a lawyer assigned
        unassigned_cases = await db.cases.find({"lawyer_id": {"$exists": False}}).to_list(length=100)
        print(f"📋 Found {len(unassigned_cases)} unassigned cases")
        
        if not lawyers:
            print("❌ No lawyers found. Please create some lawyer accounts first.")
            return
            
        if not unassigned_cases:
            print("❌ No unassigned cases found. Creating some test cases...")
            
            # Create some test cases for lawyers
            test_cases = [
                {
                    "title": "Corporate Contract Review",
                    "description": "Review and negotiate terms for a major corporate partnership agreement.",
                    "category": "Corporate Law",
                    "status": "open",
                    "urgency_level": "medium",
                    "budget_min": 5000,
                    "budget_max": 10000,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "title": "Employment Dispute Resolution",
                    "description": "Handle wrongful termination case and negotiate settlement.",
                    "category": "Labour and Employment Law",
                    "status": "in-progress",
                    "urgency_level": "high",
                    "budget_min": 3000,
                    "budget_max": 8000,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "title": "Intellectual Property Protection",
                    "description": "File trademark application and protect brand assets.",
                    "category": "IPR Law",
                    "status": "open",
                    "urgency_level": "medium",
                    "budget_min": 2000,
                    "budget_max": 5000,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "title": "Real Estate Transaction",
                    "description": "Legal assistance for commercial property acquisition.",
                    "category": "Property Law",
                    "status": "closed",
                    "urgency_level": "low",
                    "budget_min": 4000,
                    "budget_max": 7000,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ]
            
            # Insert test cases
            for case in test_cases:
                await db.cases.insert_one(case)
            
            unassigned_cases = await db.cases.find({"lawyer_id": {"$exists": False}}).to_list(length=100)
            print(f"✅ Created {len(test_cases)} new test cases")
        
        # Assign cases to lawyers
        assigned_count = 0
        for i, case in enumerate(unassigned_cases):
            # Assign to lawyer in round-robin fashion
            lawyer = lawyers[i % len(lawyers)]
            
            # Update case with lawyer assignment
            await db.cases.update_one(
                {"_id": case["_id"]},
                {
                    "$set": {
                        "lawyer_id": ObjectId(lawyer["_id"]),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            assigned_count += 1
            print(f"✅ Assigned case '{case['title']}' to {lawyer['first_name']} {lawyer['last_name']}")
        
        print(f"\n🎉 Successfully assigned {assigned_count} cases to lawyers!")
        
        # Show summary
        print("\n📊 Assignment Summary:")
        for lawyer in lawyers:
            lawyer_cases = await db.cases.count_documents({"lawyer_id": ObjectId(lawyer["_id"])})
            print(f"   {lawyer['first_name']} {lawyer['last_name']}: {lawyer_cases} cases")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(assign_cases_to_lawyers())