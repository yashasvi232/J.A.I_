"""
Meeting Link Generator - Simple service to generate meeting links for requests
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from services.meeting_config import get_meeting_config
from services.meeting_service import MeetingRequest
from models.lawyer_request import MeetingLinkData

logger = logging.getLogger(__name__)

async def generate_meeting_link_for_request(
    request_title: str,
    request_description: str,
    selected_meeting: Dict[str, Any],
    host_email: str,
    attendee_emails: list
) -> Optional[MeetingLinkData]:
    """
    Generate a meeting link for an accepted lawyer request
    
    Args:
        request_title: Title of the request
        request_description: Description of the request
        selected_meeting: Selected meeting slot data
        host_email: Lawyer's email (host)
        attendee_emails: List of attendee emails (client)
    
    Returns:
        MeetingLinkData if successful, None if failed
    """
    try:
        config = get_meeting_config()
        
        if not config.is_configured():
            logger.warning("No meeting provider configured - cannot generate meeting link")
            return None
        
        meeting_service = config.get_meeting_service()
        if not meeting_service:
            logger.error("Failed to get meeting service")
            return None
        
        # Parse meeting date and time
        meeting_date = selected_meeting.get('date')
        meeting_time = selected_meeting.get('time')
        duration = selected_meeting.get('duration', 60)
        
        if not meeting_date or not meeting_time:
            logger.error("Missing meeting date or time")
            return None
        
        # Convert to datetime
        # This is a simple parser - in production you'd want more robust date parsing
        try:
            # Assume format: "2024-01-25" and "10:00 AM"
            date_str = f"{meeting_date} {meeting_time}"
            start_time = datetime.strptime(date_str, "%Y-%m-%d %I:%M %p")
        except ValueError:
            try:
                # Try 24-hour format
                date_str = f"{meeting_date} {meeting_time}"
                start_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                logger.error(f"Failed to parse meeting date/time: {meeting_date} {meeting_time}")
                return None
        
        # Create meeting request
        meeting_request = MeetingRequest(
            title=f"Legal Consultation: {request_title}",
            description=f"Legal consultation regarding: {request_description}",
            start_time=start_time,
            duration_minutes=duration,
            host_email=host_email,
            attendee_emails=attendee_emails,
            timezone="UTC",
            meeting_type=selected_meeting.get('meeting_type', 'online')
        )
        
        # Generate meeting
        meeting_response = await meeting_service.create_meeting(meeting_request)
        
        # Convert to MeetingLinkData
        meeting_link = MeetingLinkData(
            meeting_id=meeting_response.meeting_id,
            join_url=meeting_response.join_url,
            host_url=meeting_response.host_url,
            provider=meeting_response.provider,
            created_at=meeting_response.created_at,
            expires_at=meeting_response.expires_at,
            meeting_password=meeting_response.password
        )
        
        logger.info(f"Meeting link generated successfully: {meeting_response.meeting_id}")
        return meeting_link
        
    except Exception as e:
        logger.error(f"Failed to generate meeting link: {str(e)}")
        return None

async def generate_simple_meeting_link(
    title: str,
    description: str,
    host_email: str,
    attendee_email: str
) -> Optional[str]:
    """
    Generate a simple meeting link (for immediate testing)
    Returns just the join URL
    """
    try:
        # For now, return a simple Google Meet link format
        # This is a placeholder until we have real credentials configured
        import hashlib
        import time
        
        # Generate a simple meeting ID based on the request
        meeting_data = f"{title}-{host_email}-{attendee_email}-{int(time.time())}"
        meeting_hash = hashlib.md5(meeting_data.encode()).hexdigest()[:10]
        
        # Return a Google Meet style URL (this won't actually work, but shows the format)
        meeting_url = f"https://meet.google.com/{meeting_hash}"
        
        logger.info(f"Generated placeholder meeting link: {meeting_url}")
        return meeting_url
        
    except Exception as e:
        logger.error(f"Failed to generate simple meeting link: {str(e)}")
        return None