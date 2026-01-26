#!/usr/bin/env python3
"""
Check users in database
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import connect_to_mongo, get_database

async def check_users():
    """Check users in database"""
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    print("✅ Connected to database")
    
    # Check all users
    users = await db.users.find({}).to_list(length=20)
    print(f"📊 Found {len(users)} total users")
    
    for i, user in enumerate(users):
        print(f"  User {i+1}: {user['email']} - Type: {user.get('user_type', 'MISSING')}")
    
    # Check specifically for test users
    client = await db.users.find_one({"email": "client@test.com"})
    lawyer = await db.users.find_one({"email": "lawyer@test.com"})
    
    print(f"\n🔍 Test users:")
    print(f"  client@test.com: {'✅ Found' if client else '❌ Not found'}")
    if client:
        print(f"    Type: {client.get('user_type', 'MISSING')}")
    
    print(f"  lawyer@test.com: {'✅ Found' if lawyer else '❌ Not found'}")
    if lawyer:
        print(f"    Type: {lawyer.get('user_type', 'MISSING')}")

if __name__ == "__main__":
    asyncio.run(check_users())