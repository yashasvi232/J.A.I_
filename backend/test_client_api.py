#!/usr/bin/env python3
"""
Test client requests API to see what data is returned
"""

import asyncio
import httpx
import json

async def test_client_requests_api():
    async with httpx.AsyncClient() as client:
        # Login as client
        login_response = await client.post('http://localhost:8001/api/auth/login', 
            json={'email': 'client@test.com', 'password': 'password123'})
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            print('✅ Client login successful')
            
            # Get client requests
            headers = {'Authorization': f'Bearer {token}'}
            requests_response = await client.get('http://localhost:8001/api/requests/', headers=headers)
            
            if requests_response.status_code == 200:
                requests = requests_response.json()
                print(f'✅ Found {len(requests)} requests for client')
                print()
                
                for i, req in enumerate(requests, 1):
                    print(f"{i}. Request: {req.get('title', 'No title')}")
                    print(f"   Status: {req.get('status', 'unknown')}")
                    print(f"   Response: {req.get('response_message', 'No response')}")
                    
                    if req.get('meeting_slots'):
                        print(f"   Meeting slots: {len(req['meeting_slots'])} available")
                        print(f"   Slots data: {json.dumps(req['meeting_slots'], indent=4)}")
                    else:
                        print("   Meeting slots: None")
                    
                    if req.get('selected_meeting'):
                        print(f"   Selected meeting: {json.dumps(req['selected_meeting'], indent=4)}")
                    else:
                        print("   Selected meeting: None")
                    
                    print()
            else:
                print(f'❌ Failed to get requests: {requests_response.status_code}')
                print(requests_response.text)
        else:
            print(f'❌ Login failed: {login_response.status_code}')

if __name__ == "__main__":
    asyncio.run(test_client_requests_api())