"""
Google Meet Provider - Creates meetings using Google Calendar API
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import aiohttp
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.meeting_service import VideoProvider, MeetingRequest, MeetingResponse
from models.meeting import GoogleMeetCredentials

logger = logging.getLogger(__name__)

class GoogleMeetProvider(VideoProvider):
    """Google Meet video provider using Google Calendar API"""
    
    def __init__(self, credentials: GoogleMeetCredentials):
        self.credentials = credentials
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.logger = logging.getLogger(__name__)
    
    async def validate_credentials(self) -> bool:
        """Validate Google Meet credentials by attempting to get an access token"""
        try:
            await self._ensure_valid_token()
            return True
        except Exception as e:
            self.logger.error(f"Google Meet credentials validation failed: {str(e)}")
            return False
    
    async def create_meeting(self, request: MeetingRequest) -> MeetingResponse:
        """Create a Google Meet meeting via Google Calendar API"""
        try:
            await self._ensure_valid_token()
            
            # Create calendar event with Google Meet
            event_data = {
                "summary": request.title,
                "description": request.description,
                "start": {
                    "dateTime": request.start_time.isoformat() + "Z",
                    "timeZone": request.timezone
                },
                "end": {
                    "dateTime": (request.start_time + timedelta(minutes=request.duration_minutes)).isoformat() + "Z",
                    "timeZone": request.timezone
                },
                "attendees": [{"email": email} for email in request.attendee_emails],
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"meet-{int(datetime.utcnow().timestamp())}",
                        "conferenceSolutionKey": {
                            "type": "hangoutsMeet"
                        }
                    }
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},  # 24 hours
                        {"method": "popup", "minutes": 60}        # 1 hour
                    ]
                }
            }
            
            # Make API call to create calendar event
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"https://www.googleapis.com/calendar/v3/calendars/{request.host_email}/events"
                params = {"conferenceDataVersion": "1"}
                
                async with session.post(url, json=event_data, headers=headers, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Google Calendar API error: {response.status} - {error_text}")
                    
                    event = await response.json()
            
            # Extract meeting information
            meeting_id = event["id"]
            join_url = None
            
            if "conferenceData" in event and "entryPoints" in event["conferenceData"]:
                for entry_point in event["conferenceData"]["entryPoints"]:
                    if entry_point["entryPointType"] == "video":
                        join_url = entry_point["uri"]
                        break
            
            if not join_url:
                raise Exception("Failed to create Google Meet link")
            
            self.logger.info(f"Google Meet created successfully: {meeting_id}")
            
            return MeetingResponse(
                meeting_id=meeting_id,
                join_url=join_url,
                host_url=join_url,  # Same URL for Google Meet
                provider="google_meet",
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create Google Meet: {str(e)}")
            raise
    
    async def cancel_meeting(self, meeting_id: str) -> bool:
        """Cancel a Google Meet by deleting the calendar event"""
        try:
            await self._ensure_valid_token()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            # We need to know which calendar the event is in
            # For now, we'll try the primary calendar
            async with aiohttp.ClientSession() as session:
                url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{meeting_id}"
                
                async with session.delete(url, headers=headers) as response:
                    if response.status == 204:
                        self.logger.info(f"Google Meet cancelled successfully: {meeting_id}")
                        return True
                    elif response.status == 404:
                        self.logger.warning(f"Google Meet not found: {meeting_id}")
                        return False
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to cancel Google Meet: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Error cancelling Google Meet {meeting_id}: {str(e)}")
            return False
    
    async def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if (self.access_token is None or 
            self.token_expires_at is None or 
            datetime.utcnow() >= self.token_expires_at - timedelta(minutes=5)):
            
            await self._refresh_access_token()
    
    async def _refresh_access_token(self):
        """Refresh the access token using the refresh token"""
        try:
            data = {
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "refresh_token": self.credentials.refresh_token,
                "grant_type": "refresh_token"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post("https://oauth2.googleapis.com/token", data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Token refresh failed: {response.status} - {error_text}")
                    
                    token_data = await response.json()
            
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            self.logger.info("Google access token refreshed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh Google access token: {str(e)}")
            raise

# Simple test function
async def test_google_meet_provider():
    """Test Google Meet provider with mock credentials"""
    # This would normally use real credentials
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
    
    print("Google Meet provider test completed")

if __name__ == "__main__":
    asyncio.run(test_google_meet_provider())