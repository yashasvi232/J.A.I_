#!/usr/bin/env python3
"""
Test cases API to see if accepted requests create cases properly
"""
import requests
import json

def test_cases_api():
    base_url = 'http://localhost:8001/api'
    
    print("🔍 Testing Cases API...")
    
    # Login as client
    print("\n1. 👤 Client Login")
    login_response = requests.post(f'{base_url}/auth/login', json={
        'email': 'client@test.com',
        'password': 'password123'
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        print("✅ Client login successful")
        
        # Get cases
        print("\n2. 📁 Fetching Cases")
        cases_response = requests.get(f'{base_url}/cases/', headers={
            'Authorization': f'Bearer {token}'
        })
        
        if cases_response.status_code == 200:
            cases_data = cases_response.json()
            print("✅ Cases API working")
            print(f"📊 Raw response: {json.dumps(cases_data, indent=2)}")
            
            if 'cases' in cases_data:
                cases_list = cases_data['cases']
                print(f"\n📋 Found {len(cases_list)} cases:")
                
                for i, case in enumerate(cases_list):
                    print(f"   Case {i+1}:")
                    print(f"      Title: {case.get('title', 'No title')}")
                    print(f"      Status: {case.get('status', 'No status')}")
                    print(f"      Created: {case.get('created_at', 'No date')}")
                    print(f"      Request ID: {case.get('request_id', 'No request ID')}")
                    print(f"      Client ID: {case.get('client_id', 'No client ID')}")
                    print(f"      Lawyer ID: {case.get('lawyer_id', 'No lawyer ID')}")
                    print()
            else:
                print("❌ No 'cases' key in response")
        else:
            print(f"❌ Cases API failed: {cases_response.status_code} - {cases_response.text}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
    
    # Also test lawyer view
    print("\n3. ⚖️ Lawyer Login")
    lawyer_login_response = requests.post(f'{base_url}/auth/login', json={
        'email': 'lawyer@test.com',
        'password': 'password123'
    })
    
    if lawyer_login_response.status_code == 200:
        lawyer_token = lawyer_login_response.json()['access_token']
        print("✅ Lawyer login successful")
        
        # Get lawyer cases
        print("\n4. 📁 Fetching Lawyer Cases")
        lawyer_cases_response = requests.get(f'{base_url}/cases/', headers={
            'Authorization': f'Bearer {lawyer_token}'
        })
        
        if lawyer_cases_response.status_code == 200:
            lawyer_cases_data = lawyer_cases_response.json()
            print("✅ Lawyer cases API working")
            
            if 'cases' in lawyer_cases_data:
                lawyer_cases_list = lawyer_cases_data['cases']
                print(f"📋 Lawyer has {len(lawyer_cases_list)} cases:")
                
                for i, case in enumerate(lawyer_cases_list):
                    print(f"   Case {i+1}: {case.get('title', 'No title')} - {case.get('status', 'No status')}")
            else:
                print("❌ No 'cases' key in lawyer response")
        else:
            print(f"❌ Lawyer cases API failed: {lawyer_cases_response.status_code}")
    else:
        print(f"❌ Lawyer login failed: {lawyer_login_response.status_code}")

if __name__ == "__main__":
    test_cases_api()