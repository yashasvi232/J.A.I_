#!/usr/bin/env python3
"""
Test accepting a request and generating meeting link
"""
import asyncio
import aiohttp
import json

async def test_accept_request():
    """Test the complete flow of accepting a request"""
    
    base_url = "http://localhost:8001/api"
    
    # Step 1: Login as lawyer
    print("🔐 Logging in as lawyer...")
    
    async with aiohttp.ClientSession() as session:
        login_data = {
            "email": "lawyer@test.com",
            "password": "password123"
        }
        
        async with session.post(f"{base_url}/auth/login", json=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                token = login_result["access_token"]
                print(f"✅ Login successful! Token: {token[:20]}...")
            else:
                error = await response.text()
                print(f"❌ Login failed: {error}")
                return
        
        # Step 2: Get pending requests
        print("\n📋 Getting pending requests...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        async with session.get(f"{base_url}/requests/pending", headers=headers) as response:
            if response.status == 200:
                requests = await response.json()
                print(f"✅ Found {len(requests)} pending requests")
                
                if len(requests) == 0:
                    print("❌ No pending requests to test with")
                    return
                
                # Use the first pending request
                test_request = requests[0]
                request_id = test_request["id"]
                print(f"🎯 Testing with request: {test_request['title']}")
                print(f"   Request ID: {request_id}")
                
            else:
                error = await response.text()
                print(f"❌ Failed to get pending requests: {error}")
                return
        
        # Step 3: Accept the request with meeting slots
        print(f"\n✅ Accepting request {request_id}...")
        
        accept_data = {
            "action": "accept",
            "response_message": "I would be happy to help with your case. Let's schedule a meeting.",
            "meeting_slots": [
                {
                    "date": "2025-01-28",
                    "time": "10:00 AM",
                    "meeting_type": "online",
                    "duration": 60
                }
            ]
        }
        
        async with session.post(f"{base_url}/requests/{request_id}/respond", 
                               json=accept_data, headers=headers) as response:
            if response.status == 200:
                accept_result = await response.json()
                print(f"✅ Request accepted successfully!")
                print(f"   Status: {accept_result['status']}")
                print(f"   Case created: {accept_result['case_created']}")
            else:
                error = await response.text()
                print(f"❌ Failed to accept request: {error}")
                return
        
        # Step 4: Check if meeting link was generated
        print(f"\n🔗 Checking for meeting link...")
        
        await asyncio.sleep(1)  # Give it a moment to process
        
        async with session.get(f"{base_url}/requests/{request_id}", headers=headers) as response:
            if response.status == 200:
                request_details = await response.json()
                
                if request_details.get("meeting_link"):
                    meeting_link = request_details["meeting_link"]
                    print(f"🎉 SUCCESS! Meeting link generated:")
                    print(f"   Join URL: {meeting_link['join_url']}")
                    print(f"   Provider: {meeting_link['provider']}")
                    print(f"   Meeting ID: {meeting_link['meeting_id']}")
                    print(f"   Created: {meeting_link['created_at']}")
                else:
                    print(f"⚠️ Request accepted but no meeting link found")
                    print(f"   Status: {request_details['status']}")
                    print(f"   Response: {request_details.get('response_message', 'No response')}")
            else:
                error = await response.text()
                print(f"❌ Failed to get request details: {error}")
        
        # Step 5: Test as client - view the request
        print(f"\n👤 Testing client view...")
        
        # Login as client
        client_login_data = {
            "email": "client@test.com",
            "password": "password123"
        }
        
        async with session.post(f"{base_url}/auth/login", json=client_login_data) as response:
            if response.status == 200:
                client_login_result = await response.json()
                client_token = client_login_result["access_token"]
                print(f"✅ Client login successful!")
            else:
                error = await response.text()
                print(f"❌ Client login failed: {error}")
                return
        
        # Get client requests
        client_headers = {"Authorization": f"Bearer {client_token}"}
        
        async with session.get(f"{base_url}/requests/", headers=client_headers) as response:
            if response.status == 200:
                client_requests = await response.json()
                
                # Find our test request
                test_request_client = None
                for req in client_requests:
                    if req["id"] == request_id:
                        test_request_client = req
                        break
                
                if test_request_client and test_request_client.get("meeting_link"):
                    print(f"✅ Client can see meeting link:")
                    print(f"   Join URL: {test_request_client['meeting_link']['join_url']}")
                else:
                    print(f"⚠️ Client cannot see meeting link")
            else:
                error = await response.text()
                print(f"❌ Failed to get client requests: {error}")

if __name__ == "__main__":
    asyncio.run(test_accept_request())