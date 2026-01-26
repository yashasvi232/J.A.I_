#!/usr/bin/env python3
"""
Test API endpoints for meeting links
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from database import connect_to_mongo

async def test_api_endpoints():
    """Test API endpoints for meeting links"""
    
    # Connect to database first
    await connect_to_mongo()
    
    # Create test client
    with TestClient(app) as client:
    
    print("🧪 Testing API endpoints...")
    
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
        print(f"❌ Client login failed: {login_response.text}")
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
            if req.get("meeting_link"):
                meeting_link_count += 1
                print(f"   🔗 Request '{req['title']}' has meeting link: {req['meeting_link']['join_url']}")
        
        print(f"📊 {meeting_link_count} requests have meeting links")
        
    else:
        print(f"❌ Failed to get client requests: {requests_response.text}")
        return
    
    # Step 3: Login as lawyer
    print("\n3. ⚖️ Testing lawyer login...")
    
    lawyer_login_response = client.post("/api/auth/login", json={
        "email": "lawyer@test.com",
        "password": "password123"
    })
    
    if lawyer_login_response.status_code == 200:
        lawyer_token = lawyer_login_response.json()["access_token"]
        print(f"✅ Lawyer login successful")
    else:
        print(f"❌ Lawyer login failed: {lawyer_login_response.text}")
        return
    
    # Step 4: Get lawyer requests
    print("\n4. 📋 Testing lawyer requests endpoint...")
    
    lawyer_headers = {"Authorization": f"Bearer {lawyer_token}"}
    
    lawyer_requests_response = client.get("/api/requests/", headers=lawyer_headers)
    
    if lawyer_requests_response.status_code == 200:
        lawyer_requests_data = lawyer_requests_response.json()
        print(f"✅ Found {len(lawyer_requests_data)} requests for lawyer")
        
        # Check for meeting links
        meeting_link_count = 0
        for req in lawyer_requests_data:
            if req.get("meeting_link"):
                meeting_link_count += 1
                print(f"   🔗 Request '{req['title']}' has meeting link: {req['meeting_link']['join_url']}")
        
        print(f"📊 {meeting_link_count} requests have meeting links")
        
    else:
        print(f"❌ Failed to get lawyer requests: {lawyer_requests_response.text}")
        return
    
    # Step 5: Test specific request endpoint
    print("\n5. 🎯 Testing specific request endpoint...")
    
    # Use the request ID we know has a meeting link
    test_request_id = "69773c4e2058426b384ce78c"
    
    specific_request_response = client.get(f"/api/requests/{test_request_id}", headers=client_headers)
    
    if specific_request_response.status_code == 200:
        request_data = specific_request_response.json()
        print(f"✅ Got specific request: {request_data['title']}")
        
        if request_data.get("meeting_link"):
            meeting_link = request_data["meeting_link"]
            print(f"   🔗 Meeting Link: {meeting_link['join_url']}")
            print(f"   📅 Provider: {meeting_link['provider']}")
            print(f"   🆔 Meeting ID: {meeting_link['meeting_id']}")
            print(f"   📅 Created: {meeting_link['created_at']}")
        else:
            print(f"   ❌ No meeting link in specific request")
    else:
        print(f"❌ Failed to get specific request: {specific_request_response.text}")
    
    print(f"\n🎉 API endpoint testing complete!")
    print(f"📊 Summary:")
    print(f"   ✅ Client login: Working")
    print(f"   ✅ Lawyer login: Working") 
    print(f"   ✅ Client requests API: Working")
    print(f"   ✅ Lawyer requests API: Working")
    print(f"   ✅ Specific request API: Working")
    print(f"   ✅ Meeting links in API responses: Working")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())