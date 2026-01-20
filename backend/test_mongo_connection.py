#!/usr/bin/env python3
"""
Quick MongoDB connection test script
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB connection using the same config as the app"""
    
    # Get connection details from environment
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "jai_database")
    
    print(f"🔗 Testing MongoDB connection...")
    print(f"📍 URL: {mongodb_url}")
    print(f"🗄️  Database: {database_name}")
    print("-" * 50)
    
    try:
        # Create client
        client = AsyncIOMotorClient(mongodb_url)
        
        # Test connection with ping
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get database
        db = client[database_name]
        
        # Test basic operations
        print("\n🧪 Testing basic operations...")
        
        # Insert a test document
        test_collection = db.connection_test
        test_doc = {"test": "connection", "status": "success"}
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Insert test: Document ID {result.inserted_id}")
        
        # Read the document back
        found_doc = await test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Read test: Found document {found_doc}")
        
        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleanup: Test document removed")
        
        # List existing collections
        collections = await db.list_collection_names()
        print(f"\n📋 Existing collections: {collections}")
        
        # Close connection
        client.close()
        print("\n🎉 All tests passed! MongoDB is ready for FastAPI.")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure MongoDB is running locally")
        print("2. Check if MongoDB service is started")
        print("3. Verify the connection URL in .env file")
        print("4. Try: mongosh mongodb://localhost:27017")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mongodb_connection())
    sys.exit(0 if success else 1)