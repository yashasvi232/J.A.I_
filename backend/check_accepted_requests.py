#!/usr/bin/env python3
"""
Check accepted requests and their meeting slots
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import json

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "jai_database")

async def check_accepted_requests():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Find accepted requests
    accepted_requests = await db.lawyer_requests.find({"status": "accepted"}).to_list(length=100)
    
    print(f"Found {len(accepted_requests)} accepted requests:")
    print()
    
    for i, req in enumerate(accepted_requests, 1):
        print(f"{i}. Title: {req.get('title', 'No title')}")
        print(f"   Status: {req.get('status', 'unknown')}")
        print(f"   Response: {req.get('response_message', 'No response')}")
        
        meeting_slots = req.get('meeting_slots')
        if meeting_slots:
            print(f"   Meeting Slots: {json.dumps(meeting_slots, indent=4, default=str)}")
        else:
            print("   Meeting Slots: None")
        
        selected_meeting = req.get('selected_meeting')
        if selected_meeting:
            print(f"   Selected Meeting: {json.dumps(selected_meeting, indent=4, default=str)}")
        else:
            print("   Selected Meeting: None")
        
        print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_accepted_requests())