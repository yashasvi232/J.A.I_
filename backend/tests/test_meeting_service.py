"""
Property-based tests for meeting service infrastructure
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from services.meeting_service import (
    MeetingService, VideoProvider, MeetingRequest, MeetingResponse
)
from models.meeting import MeetingProvider

# Test data generators
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

@st.composite
def meeting_response_strategy(draw):
    """Generate valid meeting responses"""
    meeting_id = draw(st.text(min_size=5, max_size=50))
    join_url = draw(st.text(min_size=10, max_size=200))
    provider = draw(st.sampled_from(["google_meet", "zoom"]))
    
    return MeetingResponse(
        meeting_id=meeting_id,
        join_url=join_url,
        provider=provider,
        created_at=datetime.utcnow()
    )

class MockVideoProvider(VideoProvider):
    """Mock video provider for testing"""
    
    def __init__(self, should_fail=False, credentials_valid=True):
        self.should_fail = should_fail
        self.credentials_valid = credentials_valid
        self.created_meetings = []
        self.cancelled_meetings = []
    
    async def create_meeting(self, request: MeetingRequest) -> MeetingResponse:
        if self.should_fail:
            raise Exception("Provider API failure")
        
        response = MeetingResponse(
            meeting_id=f"test-{len(self.created_meetings)}",
            join_url=f"https://test.com/join/{len(self.created_meetings)}",
            provider="test_provider",
            created_at=datetime.utcnow()
        )
        
        self.created_meetings.append((request, response))
        return response
    
    async def cancel_meeting(self, meeting_id: str) -> bool:
        if self.should_fail:
            return False
        
        self.cancelled_meetings.append(meeting_id)
        return True
    
    async def validate_credentials(self) -> bool:
        return self.credentials_valid

class TestMeetingServiceProperties:
    """Property-based tests for meeting service"""
    
    @given(meeting_request_strategy())
    @settings(max_examples=100)
    def test_property_6_configuration_management(self, meeting_request):
        """
        Property 6: Configuration Management
        For any provider configuration change, the system should validate credentials,
        use the correct provider for subsequent meeting creation, and handle invalid
        credentials gracefully with appropriate error logging.
        
        **Validates: Requirements 3.1, 3.4, 3.5**
        """
        async def run_test():
            # Test with valid credentials
            valid_provider = MockVideoProvider(credentials_valid=True)
            service = MeetingService(valid_provider)
            
            # Should successfully create meeting with valid credentials
            response = await service.create_meeting(meeting_request)
            assert response is not None
            assert response.meeting_id is not None
            assert response.join_url is not None
            
            # Test with invalid credentials
            invalid_provider = MockVideoProvider(credentials_valid=False)
            service_invalid = MeetingService(invalid_provider)
            
            # Should fail gracefully with invalid credentials
            with pytest.raises(Exception, match="Invalid provider credentials"):
                await service_invalid.create_meeting(meeting_request)
        
        # Run async test
        asyncio.run(run_test())
    
    @given(meeting_request_strategy())
    @settings(max_examples=100)
    def test_meeting_creation_expiration_calculation(self, meeting_request):
        """
        Test that meeting expiration times are calculated correctly
        (duration + 15 minute buffer)
        """
        async def run_test():
            provider = MockVideoProvider()
            service = MeetingService(provider)
            
            response = await service.create_meeting(meeting_request)
            
            # Verify expiration time is calculated correctly
            expected_expiration = meeting_request.start_time + timedelta(
                minutes=meeting_request.duration_minutes + 15
            )
            
            assert response.expires_at is not None
            # Allow small time difference due to processing time
            time_diff = abs((response.expires_at - expected_expiration).total_seconds())
            assert time_diff < 5  # Less than 5 seconds difference
        
        asyncio.run(run_test())
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_meeting_cancellation_handling(self, meeting_id):
        """
        Test that meeting cancellation works correctly and handles failures
        """
        async def run_test():
            # Test successful cancellation
            success_provider = MockVideoProvider(should_fail=False)
            service = MeetingService(success_provider)
            
            result = await service.cancel_meeting(meeting_id)
            assert result is True
            assert meeting_id in success_provider.cancelled_meetings
            
            # Test failed cancellation
            fail_provider = MockVideoProvider(should_fail=True)
            service_fail = MeetingService(fail_provider)
            
            result = await service_fail.cancel_meeting(meeting_id)
            assert result is False
        
        asyncio.run(run_test())
    
    @given(meeting_request_strategy())
    @settings(max_examples=50)
    def test_provider_api_failure_handling(self, meeting_request):
        """
        Test that API failures are handled gracefully
        """
        async def run_test():
            failing_provider = MockVideoProvider(should_fail=True)
            service = MeetingService(failing_provider)
            
            # Should raise exception on API failure
            with pytest.raises(Exception):
                await service.create_meeting(meeting_request)
        
        asyncio.run(run_test())

if __name__ == "__main__":
    # Run a simple test to verify the setup
    import sys
    sys.path.append('..')
    
    # Test basic functionality
    async def test_basic():
        provider = MockVideoProvider()
        service = MeetingService(provider)
        
        request = MeetingRequest(
            title="Test Meeting",
            description="Test Description",
            start_time=datetime.utcnow() + timedelta(hours=1),
            duration_minutes=60,
            host_email="host@test.com",
            attendee_emails=["attendee@test.com"],
            timezone="UTC",
            meeting_type="online"
        )
        
        response = await service.create_meeting(request)
        print(f"Created meeting: {response.meeting_id}")
        
        cancelled = await service.cancel_meeting(response.meeting_id)
        print(f"Cancelled meeting: {cancelled}")
    
    asyncio.run(test_basic())
    print("Basic meeting service test passed!")