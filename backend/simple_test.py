#!/usr/bin/env python3
"""
Simple test to verify meeting link generation in the database
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import connect_to_mongo, get_database
from bson import ObjectId
from datetime import datetime
from services.meeting_link_generator import generate_simple_meeting_link

async def test_direct_meeting_generation():
    """Test meeting link generation directly"""
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    print("✅ Connected to database")
    
    # Find a pending request
    pending_request = await db.lawyer_requests.find_one({"status": "pending"})
    
    if not pending_request:
        print("❌ No pending requests found")
        return
    
    print(f"🎯 Found pending request: {pending_request['title']}")
    print(f"   Request ID: {pending_request['_id']}")
    
    # Get client and lawyer info
    client = await db.users.find_one({"_id": pending_request["client_id"]})
    lawyer = await db.users.find_one({"_id": pending_request["lawyer_id"]})
    
    print(f"👤 Client: {client['email']}")
    print(f"⚖️ Lawyer: {lawyer['email']}")
    
    # Test meeting link generation
    print("\n🔗 Generating meeting link...")
    
    meeting_url = await generate_simple_meeting_link(
        title=pending_request['title'],
        description=pending_request['description'],
        host_email=lawyer['email'],
        attendee_email=client['email']
    )
    
    if meeting_url:
        print(f"✅ Generated meeting link: {meeting_url}")
        
        # Now simulate accepting the request with meeting link
        print("\n📝 Simulating request acceptance...")
        
        # Create meeting link data
        meeting_link_data = {
            "meeting_id": f"meeting_{pending_request['_id']}_{int(datetime.utcnow().timestamp())}",
            "join_url": meeting_url,
            "host_url": meeting_url,
            "provider": "placeholder",
            "created_at": datetime.utcnow(),
            "expires_at": None,
            "meeting_password": None
        }
        
        # Update the request with meeting link
        update_data = {
            "status": "accepted",
            "response_message": "I would be happy to help with your case.",
            "responded_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "meeting_slots": [{
                "date": "2025-01-28",
                "time": "10:00 AM",
                "duration": 60,
                "meeting_type": "online",
                "available": True
            }],
            "meeting_link": meeting_link_data,
            "meeting_created_at": datetime.utcnow()
        }
        
        result = await db.lawyer_requests.update_one(
            {"_id": pending_request["_id"]},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            print("✅ Request updated with meeting link!")
            
            # Verify the update
            updated_request = await db.lawyer_requests.find_one({"_id": pending_request["_id"]})
            
            if updated_request and updated_request.get("meeting_link"):
                print(f"🎉 SUCCESS! Meeting link stored in database:")
                print(f"   Join URL: {updated_request['meeting_link']['join_url']}")
                print(f"   Provider: {updated_request['meeting_link']['provider']}")
                print(f"   Meeting ID: {updated_request['meeting_link']['meeting_id']}")
                
                print(f"\n📊 Request Status:")
                print(f"   Status: {updated_request['status']}")
                print(f"   Response: {updated_request['response_message']}")
                print(f"   Meeting Slots: {len(updated_request.get('meeting_slots', []))}")
                
                print(f"\n🌐 Test URLs:")
                print(f"   Client Dashboard: http://localhost:8001/pages/client-dashboard.html")
                print(f"   Lawyer Dashboard: http://localhost:8001/pages/lawyer-dashboard.html")
                print(f"   Test Page: http://localhost:8001/test_meeting_links.html")
                
            else:
                print("❌ Meeting link not found in updated request")
        else:
            print("❌ Failed to update request")
    else:
        print("❌ Failed to generate meeting link")

if __name__ == "__main__":
    asyncio.run(test_direct_meeting_generation())