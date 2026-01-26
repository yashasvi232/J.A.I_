"""
Zoom Provider - Creates meetings using Zoom REST API
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import aiohttp
import asyncio
import base64
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.meeting_service import VideoProvider, MeetingRequest, MeetingResponse
from models.meeting import ZoomCredentials

logger = logging.getLogger(__name__)

class ZoomProvider(VideoProvider):
    """Zoom video provider using Zoom REST API"""
    
    def __init__(self, credentials: ZoomCredentials):
        self.credentials = credentials
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.logger = logging.getLogger(__name__)
    
    async def validate_credentials(self) -> bool:
        """Validate Zoom credentials by attempting to get an access token"""
        try:
            await self._ensure_valid_token()
            return True
        except Exception as e:
            self.logger.error(f"Zoom credentials validation failed: {str(e)}")
            return False
    
    async def create_meeting(self, request: MeetingRequest) -> MeetingResponse:
        """Create a Zoom meeting via Zoom REST API"""
        try:
            await self._ensure_valid_token()
            
            # Create meeting data
            meeting_data = {
                "topic": request.title,
                "type": 2,  # Scheduled meeting
                "start_time": request.start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "duration": request.duration_minutes,
                "timezone": request.timezone,
                "agenda": request.description,
                "settings": {
                    "host_video": True,
                    "participant_video": True,
                    "cn_meeting": False,
                    "in_meeting": False,
                    "join_before_host": False,
                    "mute_upon_entry": True,
                    "watermark": False,
                    "use_pmi": False,
                    "approval_type": 0,  # Automatically approve
                    "audio": "both",  # Both telephony and VoIP
                    "auto_recording": "none",
                    "enforce_login": False,
                    "enforce_login_domains": "",
                    "alternative_hosts": "",
                    "close_registration": False,
                    "show_share_button": True,
                    "allow_multiple_devices": True,
                    "registrants_confirmation_email": True,
                    "waiting_room": True,  # Enable waiting room for security
                    "request_permission_to_unmute_participants": False,
                    "global_dial_in_countries": ["US"],
                    "global_dial_in_numbers": [],
                    "contact_name": "",
                    "contact_email": "",
                    "registrants_email_notification": True,
                    "meeting_authentication": False,
                    "encryption_type": "enhanced_encryption",
                    "approved_or_denied_countries_or_regions": {
                        "enable": False
                    },
                    "breakout_room": {
                        "enable": False
                    },
                    "internal_meeting": False,
                    "continuous_meeting_chat": {
                        "enable": False,
                        "auto_add_invited_external_users": False
                    },
                    "participant_focused_meeting": False,
                    "push_change_to_calendar": False,
                    "resources": [],
                    "auto_start_meeting_summary": False,
                    "auto_start_ai_companion_questions": False
                }
            }
            
            # Make API call to create meeting
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                url = "https://api.zoom.us/v2/users/me/meetings"
                
                async with session.post(url, json=meeting_data, headers=headers) as response:
                    if response.status != 201:
                        error_text = await response.text()
                        raise Exception(f"Zoom API error: {response.status} - {error_text}")
                    
                    meeting = await response.json()
            
            # Extract meeting information
            meeting_id = str(meeting["id"])
            join_url = meeting["join_url"]
            start_url = meeting.get("start_url", "")
            password = meeting.get("password", "")
            
            self.logger.info(f"Zoom meeting created successfully: {meeting_id}")
            
            return MeetingResponse(
                meeting_id=meeting_id,
                join_url=join_url,
                host_url=start_url,
                start_url=start_url,
                password=password,
                provider="zoom",
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create Zoom meeting: {str(e)}")
            raise
    
    async def cancel_meeting(self, meeting_id: str) -> bool:
        """Cancel a Zoom meeting by deleting it"""
        try:
            await self._ensure_valid_token()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.zoom.us/v2/meetings/{meeting_id}"
                
                async with session.delete(url, headers=headers) as response:
                    if response.status == 204:
                        self.logger.info(f"Zoom meeting cancelled successfully: {meeting_id}")
                        return True
                    elif response.status == 404:
                        self.logger.warning(f"Zoom meeting not found: {meeting_id}")
                        return False
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to cancel Zoom meeting: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Error cancelling Zoom meeting {meeting_id}: {str(e)}")
            return False
    
    async def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if (self.access_token is None or 
            self.token_expires_at is None or 
            datetime.utcnow() >= self.token_expires_at - timedelta(minutes=5)):
            
            await self._get_access_token()
    
    async def _get_access_token(self):
        """Get access token using Server-to-Server OAuth"""
        try:
            # Create authorization header for Server-to-Server OAuth
            auth_string = f"{self.credentials.api_key}:{self.credentials.api_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "account_credentials",
                "account_id": self.credentials.account_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post("https://zoom.us/oauth/token", data=data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Token request failed: {response.status} - {error_text}")
                    
                    token_data = await response.json()
            
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            self.logger.info("Zoom access token obtained successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to get Zoom access token: {str(e)}")
            raise

# Simple test function
async def test_zoom_provider():
    """Test Zoom provider with mock credentials"""
    # This would normally use real credentials
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
    
    print("Zoom provider test completed")

if __name__ == "__main__":
    asyncio.run(test_zoom_provider())