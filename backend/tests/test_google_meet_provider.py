"""
Property-based tests for Google Meet provider
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import asyncio
import sys
import os
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from services.providers.google_meet_provider import GoogleMeetProvider
from services.meeting_service import MeetingRequest, MeetingResponse
from models.meeting import GoogleMeetCredentials

# Test data generators
@st.composite
def google_credentials_strategy(draw):
    """Generate Google Meet credentials"""
    client_id = draw(st.text(min_size=10, max_size=100))
    client_secret = draw(st.text(min_size=10, max_size=100))
    refresh_token = draw(st.text(min_size=10, max_size=200))
    
    return GoogleMeetCredentials(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token
    )

@st.composite
def meeting_request_strategy(draw):
    """Generate valid meeting requests"""
    title = draw(st.text(min_size=1, max_size=200))
    description = draw(st.text(min_size=10, max_size=1000))
    
    # Generate future datetime
    base_time = datetime.utcnow()
    hours_ahead = draw(st.integers(min_value=1, max_value=168))  # 1 hour to 1 week
    start_time = base_time + timedelta(hours=hours_ahead)
    
    duration = draw(st.integers(min_value=15, max_value=480))  # 15 min to 8 hours
    
    host_email = draw(st.emails())
    attendee_emails = draw(st.lists(st.emails(), min_size=1, max_size=10))
    
    return MeetingRequest(
        title=title,
        description=description,
        start_time=start_time,
        duration_minutes=duration,
        host_email=host_email,
        attendee_emails=attendee_emails,
        timezone="UTC",
        meeting_type="online"
    )

class MockAsyncResponse:
    """Mock aiohttp response for testing"""
    
    def __init__(self, status=200, json_data=None, text_data=""):
        self.status = status
        self._json_data = json_data or {}
        self._text_data = text_data
    
    async def json(self):
        return self._json_data
    
    async def text(self):
        return self._text_data

class TestGoogleMeetProviderProperties:
    """Property-based tests for Google Meet provider"""
    
    @given(google_credentials_strategy(), meeting_request_strategy())
    @settings(max_examples=50)
    def test_property_2_provider_selection_and_api_usage(self, credentials, meeting_request):
        """
        Property 2: Provider Selection and API Usage
        For any configured video provider (Google Meet or Zoom), the system should use
        the correct API endpoints and authentication methods specific to that provider
        when creating meetings.
        
        **Validates: Requirements 1.5, 3.2, 3.3**
        """
        async def run_test():
            provider = GoogleMeetProvider(credentials)
            
            # Mock successful token refresh
            mock_token_response = MockAsyncResponse(
                status=200,
                json_data={
                    "access_token": "mock_access_token",
                    "expires_in": 3600
                }
            )
            
            # Mock successful calendar event creation
            mock_event_response = MockAsyncResponse(
                status=200,
                json_data={
                    "id": "test_event_id",
                    "conferenceData": {
                        "entryPoints": [{
                            "entryPointType": "video",
                            "uri": "https://meet.google.com/test-meeting"
                        }]
                    }
                }
            )
            
            with patch('aiohttp.ClientSession') as mock_session:
                # Setup mock session
                mock_session_instance = AsyncMock()
                mock_session.return_value.__aenter__.return_value = mock_session_instance
                
                # Mock token refresh call
                mock_session_instance.post.return_value.__aenter__.return_value = mock_token_response
                
                # Test credential validation
                is_valid = await provider.validate_credentials()
                assert is_valid is True
                
                # Verify correct Google OAuth endpoint was called
                mock_session_instance.post.assert_called_with(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                        "refresh_token": credentials.refresh_token,
                        "grant_type": "refresh_token"
                    }
                )
                
                # Reset mock for meeting creation test
                mock_session_instance.reset_mock()
                mock_session_instance.post.return_value.__aenter__.return_value = mock_event_response
                
                # Test meeting creation
                response = await provider.create_meeting(meeting_request)
                
                # Verify response structure
                assert response.provider == "google_meet"
                assert response.meeting_id == "test_event_id"
                assert response.join_url == "https://meet.google.com/test-meeting"
                assert response.host_url == "https://meet.google.com/test-meeting"
                
                # Verify correct Google Calendar API endpoint was called
                expected_url = f"https://www.googleapis.com/calendar/v3/calendars/{meeting_request.host_email}/events"
                mock_session_instance.post.assert_called()
                
                # Get the actual call arguments
                call_args = mock_session_instance.post.call_args
                assert call_args[0][0] == expected_url  # URL
                
                # Verify the event data structure
                event_data = call_args[1]['json']
                assert event_data['summary'] == meeting_request.title
                assert event_data['description'] == meeting_request.description
                assert 'conferenceData' in event_data
                assert event_data['conferenceData']['createRequest']['conferenceSolutionKey']['type'] == 'hangoutsMeet'
        
        # Run async test
        asyncio.run(run_test())
    
    @given(google_credentials_strategy())
    @settings(max_examples=50)
    def test_credential_validation_with_invalid_credentials(self, credentials):
        """
        Test that invalid credentials are properly detected and handled
        """
        async def run_test():
            provider = GoogleMeetProvider(credentials)
            
            # Mock failed token refresh (invalid credentials)
            mock_error_response = MockAsyncResponse(
                status=401,
                text_data='{"error": "invalid_client", "error_description": "The OAuth client was not found."}'
            )
            
            with patch('aiohttp.ClientSession') as mock_session:
                mock_session_instance = AsyncMock()
                mock_session.return_value.__aenter__.return_value = mock_session_instance
                mock_session_instance.post.return_value.__aenter__.return_value = mock_error_response
                
                # Should return False for invalid credentials
                is_valid = await provider.validate_credentials()
                assert is_valid is False
        
        asyncio.run(run_test())
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=50)
    def test_meeting_cancellation_api_usage(self, meeting_id):
        """
        Test that meeting cancellation uses correct Google Calendar API
        """
        async def run_test():
            credentials = GoogleMeetCredentials(
                client_id="test_client",
                client_secret="test_secret",
                refresh_token="test_token"
            )
            provider = GoogleMeetProvider(credentials)
            
            # Mock successful token refresh
            mock_token_response = MockAsyncResponse(
                status=200,
                json_data={"access_token": "mock_token", "expires_in": 3600}
            )
            
            # Mock successful event deletion
            mock_delete_response = MockAsyncResponse(status=204)
            
            with patch('aiohttp.ClientSession') as mock_session:
                mock_session_instance = AsyncMock()
                mock_session.return_value.__aenter__.return_value = mock_session_instance
                
                # Setup token refresh mock
                mock_session_instance.post.return_value.__aenter__.return_value = mock_token_response
                
                # Setup delete mock
                mock_session_instance.delete.return_value.__aenter__.return_value = mock_delete_response
                
                # Test cancellation
                result = await provider.cancel_meeting(meeting_id)
                assert result is True
                
                # Verify correct Google Calendar delete endpoint was called
                expected_url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{meeting_id}"
                mock_session_instance.delete.assert_called_with(
                    expected_url,
                    headers={"Authorization": "Bearer mock_token"}
                )
        
        asyncio.run(run_test())

if __name__ == "__main__":
    # Run a simple test to verify the setup
    async def test_basic():
        credentials = GoogleMeetCredentials(
            client_id="test_client",
            client_secret="test_secret",
            refresh_token="test_token"
        )
        provider = GoogleMeetProvider(credentials)
        
        # This will fail with mock credentials, which is expected
        try:
            is_valid = await provider.validate_credentials()
            print(f"Credentials valid: {is_valid}")
        except Exception as e:
            print(f"Expected error: {e}")
    
    asyncio.run(test_basic())
    print("Google Meet provider property test setup verified!")