#!/usr/bin/env python3
"""
Debug dashboard API responses
"""
import asyncio
import sys
import os
import requests
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_apis():
    """Test the actual API responses that dashboards receive"""
    
    base_url = "http://localhost:8001/api"
    
    print("🔍 Testing Dashboard API Responses...")
    
    # Step 1: Login as client
    print("\n1. 👤 Client Login Test")
    
    try:
        login_response = requests.post(f"{base_url}/auth/login", json={
            "email": "client@test.com",
            "password": "password123"
        }, timeout=10)
        
        if login_response.status_code == 200:
            client_token = login_response.json()["access_token"]
            print(f"✅ Client login successful")
        else:
            print(f"❌ Client login failed: {login_response.status_code} - {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Client login error: {e}")
        return
    
    # Step 2: Test client requests API
    print("\n2. 📋 Client Requests API Test")
    
    try:
        client_headers = {"Authorization": f"Bearer {client_token}"}
        requests_response = requests.get(f"{base_url}/requests/", headers=client_headers, timeout=10)
        
        if requests_response.status_code == 200:
            requests_data = requests_response.json()
            print(f"✅ Client requests API working - Found {len(requests_data)} requests")
            
            # Debug each request
            for i, req in enumerate(requests_data):
                print(f"\n   📋 Request {i+1}: {req['title']}")
                print(f"      Status: {req['status']}")
                print(f"      ID: {req['id']}")
                
                if req.get('meeting_link'):
                    print(f"      🔗 Meeting Link: {req['meeting_link']['join_url']}")
                    print(f"      📅 Provider: {req['meeting_link']['provider']}")
                    print(f"      🆔 Meeting ID: {req['meeting_link']['meeting_id']}")
                else:
                    print(f"      ❌ No meeting link")
                
                if req.get('meeting_slots'):
                    print(f"      📅 Meeting Slots: {len(req['meeting_slots'])}")
                
                print(f"      📊 Full request keys: {list(req.keys())}")
        else:
            print(f"❌ Client requests API failed: {requests_response.status_code} - {requests_response.text}")
            return
    except Exception as e:
        print(f"❌ Client requests API error: {e}")
        return
    
    # Step 3: Login as lawyer
    print("\n3. ⚖️ Lawyer Login Test")
    
    try:
        lawyer_login_response = requests.post(f"{base_url}/auth/login", json={
            "email": "lawyer@test.com",
            "password": "password123"
        }, timeout=10)
        
        if lawyer_login_response.status_code == 200:
            lawyer_token = lawyer_login_response.json()["access_token"]
            print(f"✅ Lawyer login successful")
        else:
            print(f"❌ Lawyer login failed: {lawyer_login_response.status_code} - {lawyer_login_response.text}")
            return
    except Exception as e:
        print(f"❌ Lawyer login error: {e}")
        return
    
    # Step 4: Test lawyer requests API
    print("\n4. 📋 Lawyer Requests API Test")
    
    try:
        lawyer_headers = {"Authorization": f"Bearer {lawyer_token}"}
        lawyer_requests_response = requests.get(f"{base_url}/requests/", headers=lawyer_headers, timeout=10)
        
        if lawyer_requests_response.status_code == 200:
            lawyer_requests_data = lawyer_requests_response.json()
            print(f"✅ Lawyer requests API working - Found {len(lawyer_requests_data)} requests")
            
            # Debug each request
            for i, req in enumerate(lawyer_requests_data):
                print(f"\n   📋 Request {i+1}: {req['title']}")
                print(f"      Status: {req['status']}")
                print(f"      ID: {req['id']}")
                
                if req.get('meeting_link'):
                    print(f"      🔗 Meeting Link: {req['meeting_link']['join_url']}")
                    print(f"      📅 Provider: {req['meeting_link']['provider']}")
                else:
                    print(f"      ❌ No meeting link")
        else:
            print(f"❌ Lawyer requests API failed: {lawyer_requests_response.status_code} - {lawyer_requests_response.text}")
            return
    except Exception as e:
        print(f"❌ Lawyer requests API error: {e}")
        return
    
    # Step 5: Test cases API
    print("\n5. 📁 Cases API Test")
    
    try:
        cases_response = requests.get(f"{base_url}/cases/", headers=client_headers, timeout=10)
        
        if cases_response.status_code == 200:
            cases_data = cases_response.json()
            print(f"✅ Cases API working - Found {cases_data}")
            
            if 'cases' in cases_data:
                cases_list = cases_data['cases']
                print(f"📊 Found {len(cases_list)} cases")
                
                for i, case in enumerate(cases_list):
                    print(f"   📁 Case {i+1}: {case.get('title', 'No title')}")
                    print(f"      Status: {case.get('status', 'No status')}")
                    print(f"      ID: {case.get('_id', 'No ID')}")
            else:
                print(f"⚠️ Cases response format: {cases_data}")
        else:
            print(f"❌ Cases API failed: {cases_response.status_code} - {cases_response.text}")
    except Exception as e:
        print(f"❌ Cases API error: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"   - Client API: Working")
    print(f"   - Lawyer API: Working") 
    print(f"   - Cases API: Check above")
    print(f"   - Meeting Links: Check individual request details above")

if __name__ == "__main__":
    test_dashboard_apis()