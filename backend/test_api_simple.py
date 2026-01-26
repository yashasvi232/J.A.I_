#!/usr/bin/env python3
"""
Simple API test for meeting links
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from database import connect_to_mongo

async def test_api_simple():
    """Simple API test for meeting links"""
    
    # Connect to database first
    await connect_to_mongo()
    
    print("🧪 Testing API endpoints with TestClient...")
    
    # Create test client
    with TestClient(app) as client:
        
        # Step 1: Login as client
        print("\n1. 👤 Testing client login...")
        
        login_response = client.post("/api/auth/login", json={
            "email": "client@test.com",
            "password": "password123"
        })
        
        if login_response.status_code == 200:
            client_token = login_response.json()["access_token"]
            print(f"✅ Client login successful")
        else:
            print(f"❌ Client login failed: {login_response.status_code} - {login_response.text}")
            return
        
        # Step 2: Get client requests
        print("\n2. 📋 Testing client requests endpoint...")
        
        client_headers = {"Authorization": f"Bearer {client_token}"}
        
        requests_response = client.get("/api/requests/", headers=client_headers)
        
        if requests_response.status_code == 200:
            requests_data = requests_response.json()
            print(f"✅ Found {len(requests_data)} requests for client")
            
            # Check for meeting links
            meeting_link_count = 0
            for req in requests_data:
                print(f"   📋 Request: {req['title']} - Status: {req['status']}")
                if req.get("meeting_link"):
                    meeting_link_count += 1
                    print(f"      🔗 Meeting Link: {req['meeting_link']['join_url']}")
                    print(f"      📅 Provider: {req['meeting_link']['provider']}")
            
            print(f"📊 {meeting_link_count} requests have meeting links")
            
        else:
            print(f"❌ Failed to get client requests: {requests_response.status_code} - {requests_response.text}")
        
        print(f"\n🎉 API test complete!")

if __name__ == "__main__":
    asyncio.run(test_api_simple())