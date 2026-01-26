from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# MongoDB connection
client: AsyncIOMotorClient = None
database = None

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "jai_database")

async def connect_to_mongo():
    """Create database connection"""
    global client, database
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        database = client[DATABASE_NAME]
        
        # Test the connection
        await client.admin.command('ping')
        logging.info(f"Connected to MongoDB: {DATABASE_NAME}")
        
        # Create indexes for better performance
        await create_indexes()
        
    except ConnectionFailure as e:
        logging.warning(f"Failed to connect to MongoDB: {e}")
        logging.warning("Server will run without database functionality")
        client = None
        database = None
    except Exception as e:
        logging.warning(f"MongoDB connection error: {e}")
        logging.warning("Server will run without database functionality")
        client = None
        database = None

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        logging.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        await database.users.create_index("email", unique=True)
        await database.users.create_index("user_type")
        
        # Lawyers collection indexes
        await database.lawyers.create_index("user_id", unique=True)
        await database.lawyers.create_index("specializations")
        await database.lawyers.create_index("bar_number", unique=True)
        await database.lawyers.create_index("rating")
        
        # Cases collection indexes
        await database.cases.create_index("client_id")
        await database.cases.create_index("lawyer_id")
        await database.cases.create_index("status")
        await database.cases.create_index("category")
        await database.cases.create_index("created_at")
        
        # Lawyer requests collection indexes
        await database.lawyer_requests.create_index("client_id")
        await database.lawyer_requests.create_index("lawyer_id")
        await database.lawyer_requests.create_index("status")
        await database.lawyer_requests.create_index("created_at")
        
        # AI matches collection indexes
        await database.ai_matches.create_index("case_id")
        await database.ai_matches.create_index("lawyer_id")
        await database.ai_matches.create_index("match_score")
        
        # Chat messages collection indexes
        await database.chat_messages.create_index("request_id")
        await database.chat_messages.create_index("sender_id")
        await database.chat_messages.create_index("timestamp")
        await database.chat_messages.create_index([("request_id", 1), ("timestamp", 1)])
        await database.chat_messages.create_index([("request_id", 1), ("is_read", 1)])
        
        logging.info("Database indexes created successfully")
        
    except Exception as e:
        logging.error(f"Error creating indexes: {e}")

def get_database():
    """Get database instance"""
    return database