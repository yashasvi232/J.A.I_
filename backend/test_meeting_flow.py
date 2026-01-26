#!/usr/bin/env python3
"""
Test script to verify meeting link generation flow
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import connect_to_mongo, get_database
from bson import ObjectId
from datetime import datetime
import json

async def test_meeting_flow():
    """Test the complete meeting link generation flow"""
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    if db is None:
        print("❌ Failed to connect to database")
        return
    
    print("✅ Connected to database")
    
    # Check existing users
    users = await db.users.find({"user_type": {"$in": ["client", "lawyer"]}}).to_list(length=10)
    print(f"📊 Found {len(users)} users")
    
    # Get specific test users
    client = await db.users.find_one({"email": "client@test.com"})
    lawyer = await db.users.find_one({"email": "lawyer@test.com"})
    
    if not client or not lawyer:
        print("❌ Need both client and lawyer users for testing")
        return
    
    print(f"👤 Client: {client['email']}")
    print(f"⚖️ Lawyer: {lawyer['email']}")
    
    # Check existing requests
    requests = await db.lawyer_requests.find({}).to_list(length=10)
    print(f"📋 Found {len(requests)} existing requests")
    
    # Show existing requests
    for i, req in enumerate(requests):
        print(f"  Request {i+1}: {req['title']} - Status: {req['status']}")
        if req.get('meeting_link'):
            print(f"    Meeting Link: {req['meeting_link']['join_url']}")
    
    # Create a test request if none exist
    if len(requests) == 0:
        print("📝 Creating test request...")
        
        test_request = {
            "client_id": client["_id"],
            "lawyer_id": lawyer["_id"],
            "title": "Test Legal Consultation",
            "description": "This is a test request to verify meeting link generation",
            "category": "General Practice",
            "urgency_level": "medium",
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.lawyer_requests.insert_one(test_request)
        print(f"✅ Created test request with ID: {result.inserted_id}")
        
        # Reload requests
        requests = await db.lawyer_requests.find({}).to_list(length=10)
    
    # Find a pending request to test with
    pending_request = None
    for req in requests:
        if req["status"] == "pending":
            pending_request = req
            break
    
    if pending_request:
        print(f"\n🎯 Test with request: {pending_request['title']}")
        print(f"   Request ID: {pending_request['_id']}")
        print(f"   Status: {pending_request['status']}")
        
        # Test the meeting link generation function
        from services.meeting_link_generator import generate_simple_meeting_link
        
        meeting_url = await generate_simple_meeting_link(
            title=pending_request['title'],
            description=pending_request['description'],
            host_email=lawyer['email'],
            attendee_email=client['email']
        )
        
        if meeting_url:
            print(f"✅ Generated meeting link: {meeting_url}")
        else:
            print("❌ Failed to generate meeting link")
    
    print("\n" + "="*50)
    print("🧪 TEST INSTRUCTIONS:")
    print("1. Open http://localhost:8001/test_meeting_links.html")
    print("2. Login as lawyer (lawyer@test.com / password123)")
    print("3. View pending requests to get a request ID")
    print("4. Accept a request with meeting details")
    print("5. Check if meeting link is generated")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(test_meeting_flow())