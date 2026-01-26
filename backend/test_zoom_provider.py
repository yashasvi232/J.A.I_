"""
Test script for Zoom provider
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.providers.zoom_provider import ZoomProvider
from models.meeting import ZoomCredentials

async def test_zoom_provider():
    """Test Zoom provider"""
    print("Testing Zoom Provider...")
    
    # Mock credentials for testing
    mock_credentials = ZoomCredentials(
        api_key="test_api_key",
        api_secret="test_api_secret",
        account_id="test_account_id"
    )
    
    provider = ZoomProvider(mock_credentials)
    
    # Test credential validation (will fail with mock credentials)
    try:
        is_valid = await provider.validate_credentials()
        print(f"Credentials valid: {is_valid}")
    except Exception as e:
        print(f"Expected error with mock credentials: {e}")
    
    print("Zoom provider basic test completed!")

if __name__ == "__main__":
    asyncio.run(test_zoom_provider())