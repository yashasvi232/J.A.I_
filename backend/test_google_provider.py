"""
Test script for Google Meet provider
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.providers.google_meet_provider import GoogleMeetProvider
from models.meeting import GoogleMeetCredentials

async def test_google_provider():
    """Test Google Meet provider"""
    print("Testing Google Meet Provider...")
    
    # Mock credentials for testing
    mock_credentials = GoogleMeetCredentials(
        client_id="test_client_id",
        client_secret="test_client_secret", 
        refresh_token="test_refresh_token"
    )
    
    provider = GoogleMeetProvider(mock_credentials)
    
    # Test credential validation (will fail with mock credentials)
    try:
        is_valid = await provider.validate_credentials()
        print(f"Credentials valid: {is_valid}")
    except Exception as e:
        print(f"Expected error with mock credentials: {e}")
    
    print("Google Meet provider basic test completed!")

if __name__ == "__main__":
    asyncio.run(test_google_provider())