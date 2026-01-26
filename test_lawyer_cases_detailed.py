#!/usr/bin/env python3
"""
Test lawyer cases API with detailed error reporting
"""
import requests
import json

def test_lawyer_cases_detailed():
    base_url = 'http://localhost:8001/api'
    
    print("🔍 Testing Lawyer Cases API with detailed error reporting...")
    
    # Login as lawyer
    print("\n1. ⚖️ Lawyer Login")
    login_response = requests.post(f'{base_url}/auth/login', json={
        'email': 'lawyer@test.com',
        'password': 'password123'
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        print("✅ Lawyer login successful")
        
        # Get lawyer profile to verify user info
        print("\n2. 👤 Get Lawyer Profile")
        profile_response = requests.get(f'{base_url}/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"✅ Lawyer profile: {profile_data['first_name']} {profile_data['last_name']}")
            print(f"   User ID: {profile_data.get('id', 'Not found')}")
            print(f"   User Type: {profile_data['user_type']}")
            print(f"   Email: {profile_data['email']}")
            print(f"   Full profile: {json.dumps(profile_data, indent=2)}")
        else:
            print(f"❌ Profile request failed: {profile_response.status_code}")
            return
        
        # Test cases endpoint with detailed error handling
        print("\n3. 📁 Fetching Lawyer Cases")
        try:
            cases_response = requests.get(f'{base_url}/cases/', headers={
                'Authorization': f'Bearer {token}'
            }, timeout=30)
            
            print(f"📊 Response Status: {cases_response.status_code}")
            print(f"📊 Response Headers: {dict(cases_response.headers)}")
            
            if cases_response.status_code == 200:
                cases_data = cases_response.json()
                print(f"✅ Success: {len(cases_data.get('cases', []))} cases returned")
                print(f"📋 Cases data: {json.dumps(cases_data, indent=2)}")
            else:
                print(f"❌ Error Status: {cases_response.status_code}")
                print(f"❌ Error Headers: {dict(cases_response.headers)}")
                print(f"❌ Error Text: {cases_response.text}")
                
                # Try to parse as JSON for detailed error
                try:
                    error_json = cases_response.json()
                    print(f"❌ Error JSON: {json.dumps(error_json, indent=2)}")
                except:
                    print("❌ Could not parse error as JSON")
                    
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
        except requests.exceptions.ConnectionError:
            print("❌ Connection error")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"❌ Login error: {login_response.text}")

if __name__ == "__main__":
    test_lawyer_cases_detailed()