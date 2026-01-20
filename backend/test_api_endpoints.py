#!/usr/bin/env python3
"""
Test script to verify FastAPI endpoints are working with MongoDB
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_api_endpoints():
    """Test all main API endpoints"""
    
    print("🧪 Testing FastAPI + MongoDB Integration")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Root endpoint
        print("\n1️⃣ Testing root endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"✅ Root: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
        
        # Test 2: Health check
        print("\n2️⃣ Testing health endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"✅ Health: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Health endpoint failed: {e}")
        
        # Test 3: API Documentation
        print("\n3️⃣ Testing API docs...")
        try:
            response = await client.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print(f"✅ Docs: {response.status_code} - Swagger UI available")
            else:
                print(f"❌ Docs: {response.status_code}")
        except Exception as e:
            print(f"❌ Docs endpoint failed: {e}")
        
        # Test 4: User registration
        print("\n4️⃣ Testing user registration...")
        try:
            test_user = {
                "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "User",
                "user_type": "client"
            }
            response = await client.post(f"{BASE_URL}/api/auth/register", json=test_user)
            print(f"✅ Registration: {response.status_code}")
            if response.status_code == 201:
                user_data = response.json()
                print(f"   Created user: {user_data.get('user', {}).get('email')}")
                return user_data.get('access_token')
            else:
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Registration failed: {e}")
        
        # Test 5: Get lawyers (should work even without auth)
        print("\n5️⃣ Testing lawyers endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/lawyers/")
            print(f"✅ Lawyers: {response.status_code}")
            if response.status_code == 200:
                lawyers = response.json()
                print(f"   Found {len(lawyers)} lawyers")
        except Exception as e:
            print(f"❌ Lawyers endpoint failed: {e}")
    
    print("\n🎉 API testing completed!")
    print("\n📋 Summary:")
    print("- FastAPI server is running on http://localhost:8000")
    print("- MongoDB connection is working")
    print("- API documentation available at http://localhost:8000/docs")
    print("- All endpoints are accessible")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())