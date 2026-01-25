#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_database
from bson import ObjectId

async def check_meeting_slots():
    print("🗓️ CHECKING MEETING SLOTS IN REQUESTS")
    print("=" * 50)
    
    db = get_database()
    
    # Get all requests
    requests = await db.lawyer_requests.find({}).to_list(length=100)
    
    print(f"📋 Total requests: {len(requests)}")
    print()
    
    for i, req in enumerate(requests, 1):
        print(f"{i}. {req['title']}")
        print(f"   Status: {req['status']}")
        print(f"   Client ID: {req['client_id']}")
        print(f"   Lawyer ID: {req['lawyer_id']}")
        
        # Check for meeting slots
        meeting_slots = req.get('meeting_slots')
        if meeting_slots:
            print(f"   ✅ Meeting Slots: {len(meeting_slots)} available")
            for j, slot in enumerate(meeting_slots, 1):
                print(f"      {j}. {slot.get('date')} at {slot.get('time')} ({slot.get('meeting_type')}, {slot.get('duration')}min)")
        else:
            print(f"   ❌ Meeting Slots: None")
        
        # Check for selected meeting
        selected_meeting = req.get('selected_meeting')
        if selected_meeting:
            print(f"   🎯 Selected Meeting: {selected_meeting.get('date')} at {selected_meeting.get('time')}")
        else:
            print(f"   ⏳ Selected Meeting: None")
        
        print()

if __name__ == "__main__":
    asyncio.run(check_meeting_slots())