#!/usr/bin/env python3
"""
Debug the lawyer cases API 500 error
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_database
from bson import ObjectId
import requests

async def debug_lawyer_cases():
    """Debug the lawyer cases API issue"""
    
    print("🔍 Debugging Lawyer Cases API...")
    
    # First, let's check what's in the database
    db = get_database()
    
    # Get lawyer user info
    print("\n1. 👨‍⚖️ Finding Lawyer User")
    lawyer_user = await db.users.find_one({"email": "lawyer@test.com"})
    if lawyer_user:
        lawyer_id = str(lawyer_user["_id"])
        print(f"✅ Found lawyer: {lawyer_user['first_name']} {lawyer_user['last_name']}")
        print(f"   Lawyer ID: {lawyer_id}")
        print(f"   User Type: {lawyer_user.get('user_type', 'Not set')}")
    else:
        print("❌ Lawyer user not found")
        return
    
    # Check cases collection
    print("\n2. 📁 Checking Cases Collection")
    all_cases = await db.cases.find({}).to_list(length=100)
    print(f"📊 Total cases in database: {len(all_cases)}")
    
    # Check cases for this lawyer
    print(f"\n3. 🔍 Looking for cases with lawyer_id: {lawyer_id}")
    
    # Try different ObjectId formats
    try:
        # Method 1: String comparison
        lawyer_cases_str = await db.cases.find({"lawyer_id": lawyer_id}).to_list(length=100)
        print(f"   String search: {len(lawyer_cases_str)} cases")
        
        # Method 2: ObjectId comparison
        lawyer_cases_obj = await db.cases.find({"lawyer_id": ObjectId(lawyer_id)}).to_list(length=100)
        print(f"   ObjectId search: {len(lawyer_cases_obj)} cases")
        
        # Show all cases with their lawyer_id types
        print(f"\n4. 📋 All Cases Analysis:")
        for i, case in enumerate(all_cases):
            lawyer_id_in_case = case.get("lawyer_id")
            lawyer_id_type = type(lawyer_id_in_case).__name__
            matches_str = str(lawyer_id_in_case) == lawyer_id
            matches_obj = lawyer_id_in_case == ObjectId(lawyer_id) if lawyer_id_in_case else False
            
            print(f"   Case {i+1}: {case.get('title', 'No title')}")
            print(f"      lawyer_id: {lawyer_id_in_case} (type: {lawyer_id_type})")
            print(f"      Matches string: {matches_str}")
            print(f"      Matches ObjectId: {matches_obj}")
            print()
            
    except Exception as e:
        print(f"❌ Database query error: {e}")
        return
    
    # Test the actual API endpoint
    print("\n5. 🌐 Testing API Endpoint")
    try:
        # Login as lawyer
        login_response = requests.post("http://localhost:8001/api/auth/login", json={
            "email": "lawyer@test.com",
            "password": "password123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print("✅ Lawyer login successful")
            
            # Test cases endpoint
            cases_response = requests.get("http://localhost:8001/api/cases/", headers={
                "Authorization": f"Bearer {token}"
            })
            
            print(f"📊 Cases API response: {cases_response.status_code}")
            if cases_response.status_code != 200:
                print(f"❌ Error response: {cases_response.text}")
            else:
                cases_data = cases_response.json()
                print(f"✅ Success: {len(cases_data.get('cases', []))} cases returned")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_lawyer_cases())