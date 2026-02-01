#!/usr/bin/env python3
"""
Test script to verify the request flow is working
"""

import asyncio
import httpx
import json

# API Configuration
API_BASE = "http://localhost:8001/api"

async def test_request_flow():
    """Test the request sending and receiving flow"""
    print("🧪 Testing Request Flow")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Check if test users exist
            print("1. 🔍 Checking test users...")
            debug_response = await client.get(f"{API_BASE}/debug/requests")
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                print(f"   📊 Found {debug_data.get('total_requests', 0)} existing requests")
            
            # 2. Get lawyers to find a lawyer ID
            print("\n2. 👥 Getting lawyers...")
            lawyers_response = await client.get(f"{API_BASE}/public/lawyers")
            if lawyers_response.status_code != 200:
                print(f"❌ Failed to get lawyers: {lawyers_response.text}")
                return
            
            lawyers_data = lawyers_response.json()
            if not lawyers_data.get("lawyers"):
                print("❌ No lawyers found")
                return
            
            lawyer = lawyers_data["lawyers"][0]
            lawyer_id = lawyer["id"]
            print(f"   ✅ Found lawyer: {lawyer['first_name']} {lawyer['last_name']} (ID: {lawyer_id})")
            
            # 3. Send a request
            print("\n3. 📤 Sending request to lawyer...")
            request_data = {
                "title": "Test Contract Review",
                "description": "I need help reviewing a test contract for my business.",
                "category": "Contract and Agreement Law",
                "urgency_level": "medium",
                "budget_min": 500,
                "budget_max": 1000,
                "lawyer_id": lawyer_id
            }
            
            send_response = await client.post(f"{API_BASE}/requests/", json=request_data)
            print(f"   📡 Response status: {send_response.status_code}")
            
            if send_response.status_code == 200:
                send_result = send_response.json()
                request_id = send_result["request_id"]
                print(f"   ✅ Request sent successfully! ID: {request_id}")
            else:
                print(f"   ❌ Failed to send request: {send_response.text}")
                return
            
            # 4. Check pending requests
            print("\n4. 📋 Checking pending requests...")
            pending_response = await client.get(f"{API_BASE}/requests/pending")
            print(f"   📡 Response status: {pending_response.status_code}")
            
            if pending_response.status_code == 200:
                pending_requests = pending_response.json()
                print(f"   ✅ Found {len(pending_requests)} pending request(s)")
                
                if pending_requests:
                    for req in pending_requests:
                        print(f"      📋 Request: {req['title']} from {req['client_name']}")
                else:
                    print("   ⚠️ No pending requests found")
            else:
                print(f"   ❌ Failed to get pending requests: {pending_response.text}")
            
            # 5. Check all requests in database
            print("\n5. 🗄️ Checking all requests in database...")
            all_requests_response = await client.get(f"{API_BASE}/debug/requests")
            if all_requests_response.status_code == 200:
                all_data = all_requests_response.json()
                print(f"   📊 Total requests in database: {all_data.get('total_requests', 0)}")
                
                for req in all_data.get('requests', []):
                    print(f"      📋 {req['title']} - Status: {req['status']} - Client: {req['client_name']} - Lawyer: {req['lawyer_name']}")
            
            print("\n" + "=" * 40)
            print("🎉 Request flow test completed!")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting request flow test...")
    print("Make sure the backend server is running on http://localhost:8001")
    print()
    
    asyncio.run(test_request_flow())