#!/usr/bin/env python3
"""
Simple test user creation without MongoDB
Creates a JSON file with test credentials
"""

import json
import os
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_simple_test_users():
    """Create test users in JSON format"""
    
    print("🔧 Creating simple test users (no MongoDB required)...")
    
    # Test users data
    test_users = [
        {
            "id": "client_1",
            "email": "client@test.com",
            "password": "password123",
            "password_hash": pwd_context.hash("password123"),
            "first_name": "John",
            "last_name": "Client",
            "phone": "+1234567890",
            "user_type": "client",
            "is_verified": True,
            "is_active": True
        },
        {
            "id": "lawyer_1",
            "email": "lawyer@test.com", 
            "password": "password123",
            "password_hash": pwd_context.hash("password123"),
            "first_name": "Sarah",
            "last_name": "Attorney",
            "phone": "+1234567891",
            "user_type": "lawyer",
            "is_verified": True,
            "is_active": True
        }
    ]
    
    # Save to JSON file
    with open('test_users.json', 'w') as f:
        json.dump(test_users, f, indent=2)
    
    print("✅ Test users created in test_users.json")
    
    # Print credentials
    print("\n" + "=" * 50)
    print("🔑 TEST LOGIN CREDENTIALS")
    print("=" * 50)
    
    print("\n👤 CLIENT LOGIN:")
    print("Email:    client@test.com")
    print("Password: password123")
    
    print("\n⚖️  LAWYER LOGIN:")
    print("Email:    lawyer@test.com")
    print("Password: password123")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Install MongoDB or use Docker")
    print("2. Run: python start_server.py")
    print("3. Open pages/client-login.html or pages/lawyer-login.html")
    print("4. Use the credentials above")

if __name__ == "__main__":
    create_simple_test_users()