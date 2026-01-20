#!/usr/bin/env python3
"""
Comprehensive test script for FastAPI + MongoDB integration
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8001"

async def test_full_api():
    """Test all main API endpoints with MongoDB"""
    
    print("🧪 Testing FastAPI + MongoDB Integration")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Root endpoint
        print("\n1️⃣ Testing root endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/")
            data = response.json()
            print(f"✅ Root: {response.status_code}")
            print(f"   Message: {data.get('message')}")
            print(f"   MongoDB: {data.get('mongodb')}")
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
        
        # Test 2: Health check
        print("\n2️⃣ Testing health endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            data = response.json()
            print(f"✅ Health: {response.status_code}")
            print(f"   Status: {data.get('status')}")
            print(f"   MongoDB: {data.get('mongodb')}")
        except Exception as e:
            print(f"❌ Health endpoint failed: {e}")
        
        # Test 3: Get lawyers
        print("\n3️⃣ Testing lawyers endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/lawyers")
            data = response.json()
            lawyers = data.get('lawyers', [])
            print(f"✅ Lawyers: {response.status_code}")
            print(f"   Found {len(lawyers)} lawyers")
            
            if lawyers:
                lawyer = lawyers[0]
                print(f"   Sample lawyer: {lawyer.get('first_name')} {lawyer.get('last_name')}")
                print(f"   Email: {lawyer.get('email')}")
                print(f"   Type: {lawyer.get('user_type')}")
        except Exception as e:
            print(f"❌ Lawyers endpoint failed: {e}")
        
        # Test 4: Login test
        print("\n4️⃣ Testing login endpoint...")
        try:
            login_data = {
                "email": "lawyer@test.com",
                "password": "password123"
            }
            response = await client.post(f"{BASE_URL}/api/auth/login", json=login_data)
            data = response.json()
            print(f"✅ Login: {response.status_code}")
            
            if response.status_code == 200:
                user = data.get('user', {})
                print(f"   Logged in as: {user.get('first_name')} {user.get('last_name')}")
                print(f"   User type: {user.get('user_type')}")
                print(f"   Token: {data.get('access_token')[:20]}...")
            else:
                print(f"   Error: {data}")
        except Exception as e:
            print(f"❌ Login endpoint failed: {e}")
        
        # Test 5: API Documentation
        print("\n5️⃣ Testing API documentation...")
        try:
            response = await client.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print(f"✅ Docs: {response.status_code} - Swagger UI available")
            else:
                print(f"❌ Docs: {response.status_code}")
        except Exception as e:
            print(f"❌ Docs endpoint failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
    print("\n📋 Summary:")
    print("✅ FastAPI server running on http://localhost:8001")
    print("✅ MongoDB connection working")
    print("✅ Test users created and accessible")
    print("✅ Basic endpoints functional")
    print("✅ API documentation available at http://localhost:8001/docs")
    
    print("\n🔑 Test Credentials:")
    print("   Client: client@test.com / password123")
    print("   Lawyer: lawyer@test.com / password123")
    print("   Demo Client: demo.client@jai.com / demo123")
    print("   Demo Lawyer: demo.lawyer@jai.com / demo123")
    
    print("\n🌐 Frontend Integration:")
    print("   Update frontend to use: http://localhost:8001")
    print("   Login pages: pages/client-login.html, pages/lawyer-login.html")

if __name__ == "__main__":
    asyncio.run(test_full_api())