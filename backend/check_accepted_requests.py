#!/usr/bin/env python3
"""
Check accepted requests with meeting links
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import connect_to_mongo, get_database

async def check_accepted_requests():
    """Check accepted requests with meeting links"""
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    print("✅ Connected to database")
    
    # Find accepted requests
    accepted_requests = await db.lawyer_requests.find({"status": "accepted"}).to_list(length=10)
    
    print(f"📊 Found {len(accepted_requests)} accepted requests")
    
    for i, req in enumerate(accepted_requests):
        print(f"\n📋 Request {i+1}: {req['title']}")
        print(f"   ID: {req['_id']}")
        print(f"   Status: {req['status']}")
        print(f"   Client ID: {req['client_id']}")
        print(f"   Lawyer ID: {req['lawyer_id']}")
        
        if req.get('meeting_link'):
            meeting_link = req['meeting_link']
            print(f"   🔗 Meeting Link: {meeting_link['join_url']}")
            print(f"   📅 Provider: {meeting_link['provider']}")
            print(f"   🆔 Meeting ID: {meeting_link['meeting_id']}")
        else:
            print(f"   ❌ No meeting link")
        
        if req.get('meeting_slots'):
            print(f"   📅 Meeting Slots: {len(req['meeting_slots'])}")
            for slot in req['meeting_slots']:
                print(f"      - {slot['date']} at {slot['time']} ({slot['meeting_type']})")
        
        # Get client and lawyer names
        client = await db.users.find_one({"_id": req["client_id"]})
        lawyer = await db.users.find_one({"_id": req["lawyer_id"]})
        
        if client:
            print(f"   👤 Client: {client['first_name']} {client['last_name']} ({client['email']})")
        if lawyer:
            print(f"   ⚖️ Lawyer: {lawyer['first_name']} {lawyer['last_name']} ({lawyer['email']})")

if __name__ == "__main__":
    asyncio.run(check_accepted_requests())