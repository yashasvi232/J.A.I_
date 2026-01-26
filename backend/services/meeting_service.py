"""
Meeting Service - Core service for managing video meeting links
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class MeetingRequest(BaseModel):
    """Request data for creating a meeting"""
    title: str
    description: str
    start_time: datetime
    duration_minutes: int = 60
    host_email: str
    attendee_emails: List[str]
    timezone: str = "UTC"
    meeting_type: str = "online"

class MeetingResponse(BaseModel):
    """Response data from meeting creation"""
    meeting_id: str
    join_url: str
    host_url: Optional[str] = None
    start_url: Optional[str] = None  # For Zoom
    password: Optional[str] = None
    provider: str
    created_at: datetime
    expires_at: Optional[datetime] = None

class MeetingLink(BaseModel):
    """Meeting link data for database storage"""
    meeting_id: str
    join_url: str
    host_url: Optional[str] = None
    provider: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    meeting_password: Optional[str] = None

class VideoProvider(ABC):
    """Abstract base class for video conferencing providers"""
    
    @abstractmethod
    async def create_meeting(self, request: MeetingRequest) -> MeetingResponse:
        """Create a video meeting"""
        pass
    
    @abstractmethod
    async def cancel_meeting(self, meeting_id: str) -> bool:
        """Cancel a video meeting"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate provider credentials"""
        pass

class MeetingService:
    """Core meeting service that manages video meeting creation"""
    
    def __init__(self, provider: VideoProvider):
        self.provider = provider
        self.logger = logging.getLogger(__name__)
    
    async def create_meeting(self, request: MeetingRequest) -> MeetingResponse:
        """Create a video meeting using the configured provider"""
        try:
            self.logger.info(f"Creating meeting: {request.title}")
            
            # Validate provider credentials
            if not await self.provider.validate_credentials():
                raise Exception("Invalid provider credentials")
            
            # Create meeting with provider
            response = await self.provider.create_meeting(request)
            
            # Calculate expiration time (meeting duration + 15 min buffer)
            expires_at = request.start_time + timedelta(
                minutes=request.duration_minutes + 15
            )
            response.expires_at = expires_at
            
            self.logger.info(f"Meeting created successfully: {response.meeting_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create meeting: {str(e)}")
            raise
    
    async def cancel_meeting(self, meeting_id: str) -> bool:
        """Cancel a video meeting"""
        try:
            self.logger.info(f"Cancelling meeting: {meeting_id}")
            result = await self.provider.cancel_meeting(meeting_id)
            
            if result:
                self.logger.info(f"Meeting cancelled successfully: {meeting_id}")
            else:
                self.logger.warning(f"Failed to cancel meeting: {meeting_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error cancelling meeting {meeting_id}: {str(e)}")
            return False
    
    async def get_meeting_details(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting details (if supported by provider)"""
        # This would be implemented based on provider capabilities
        return None