#!/usr/bin/env python3
"""
Debug the request system to see why requests aren't showing up
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "jai_database")

async def debug_requests():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("🔍 DEBUGGING REQUEST SYSTEM")
    print("=" * 50)
    
    # Get test users
    client_user = await db.users.find_one({"email": "client@test.com"})
    lawyer_user = await db.users.find_one({"email": "lawyer@test.com"})
    
    print("👥 USER INFORMATION:")
    if client_user:
        print(f"   Client ID: {client_user['_id']}")
        print(f"   Client Name: {client_user['first_name']} {client_user['last_name']}")
    else:
        print("   ❌ Client not found!")
    
    if lawyer_user:
        print(f"   Lawyer ID: {lawyer_user['_id']}")
        print(f"   Lawyer Name: {lawyer_user['first_name']} {lawyer_user['last_name']}")
    else:
        print("   ❌ Lawyer not found!")
    
    print()
    print("📋 ALL REQUESTS IN DATABASE:")
    all_requests = await db.lawyer_requests.find({}).to_list(length=100)
    print(f"   Total requests: {len(all_requests)}")
    
    for i, req in enumerate(all_requests, 1):
        print(f"\n   {i}. {req.get('title', 'No title')}")
        print(f"      Status: {req.get('status', 'unknown')}")
        print(f"      Client ID: {req.get('client_id')}")
        print(f"      Lawyer ID: {req.get('lawyer_id')}")
        print(f"      Category: {req.get('category', 'unknown')}")
        print(f"      Created: {req.get('created_at', 'unknown')}")
    
    print()
    print("🎯 REQUESTS FOR TEST LAWYER:")
    if lawyer_user:
        lawyer_requests = await db.lawyer_requests.find({"lawyer_id": lawyer_user["_id"]}).to_list(length=100)
        print(f"   Found {len(lawyer_requests)} requests for test lawyer")
        
        if lawyer_requests:
            for req in lawyer_requests:
                print(f"   - {req.get('title', 'No title')} (status: {req.get('status', 'unknown')})")
        else:
            print("   ❌ No requests found for test lawyer!")
            print("   This means requests were sent to a different lawyer ID")
    
    print()
    print("🔍 CHECKING LAWYER PROFILES:")
    lawyers = await db.lawyers.find({}).to_list(length=100)
    print(f"   Found {len(lawyers)} lawyer profiles:")
    
    for lawyer in lawyers:
        user_id = lawyer.get("user_id")
        bar_number = lawyer.get("bar_number", "unknown")
        print(f"   - User ID: {user_id}, Bar: {bar_number}")
        
        # Find corresponding user
        user = await db.users.find_one({"_id": user_id})
        if user:
            print(f"     Name: {user.get('first_name', 'unknown')} {user.get('last_name', 'unknown')}")
            print(f"     Email: {user.get('email', 'unknown')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_requests())