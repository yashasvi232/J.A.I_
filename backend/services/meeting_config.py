"""
Meeting Configuration Service - Simple configuration for meeting providers
"""
from typing import Optional
from models.meeting import MeetingProvider, GoogleMeetCredentials, ZoomCredentials
from services.providers.google_meet_provider import GoogleMeetProvider
from services.providers.zoom_provider import ZoomProvider
from services.meeting_service import MeetingService, VideoProvider
import logging

logger = logging.getLogger(__name__)

class MeetingConfigService:
    """Simple meeting configuration service"""
    
    def __init__(self):
        self.current_provider: Optional[VideoProvider] = None
        self.current_provider_type: Optional[MeetingProvider] = None
        self.logger = logging.getLogger(__name__)
    
    def configure_google_meet(self, credentials: GoogleMeetCredentials) -> bool:
        """Configure Google Meet as the provider"""
        try:
            provider = GoogleMeetProvider(credentials)
            self.current_provider = provider
            self.current_provider_type = MeetingProvider.GOOGLE_MEET
            self.logger.info("Google Meet provider configured")
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure Google Meet: {str(e)}")
            return False
    
    def configure_zoom(self, credentials: ZoomCredentials) -> bool:
        """Configure Zoom as the provider"""
        try:
            provider = ZoomProvider(credentials)
            self.current_provider = provider
            self.current_provider_type = MeetingProvider.ZOOM
            self.logger.info("Zoom provider configured")
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure Zoom: {str(e)}")
            return False
    
    def get_meeting_service(self) -> Optional[MeetingService]:
        """Get configured meeting service"""
        if self.current_provider is None:
            self.logger.warning("No meeting provider configured")
            return None
        
        return MeetingService(self.current_provider)
    
    def is_configured(self) -> bool:
        """Check if a provider is configured"""
        return self.current_provider is not None
    
    def get_provider_type(self) -> Optional[MeetingProvider]:
        """Get current provider type"""
        return self.current_provider_type

# Global configuration instance
_meeting_config = MeetingConfigService()

def get_meeting_config() -> MeetingConfigService:
    """Get the global meeting configuration"""
    return _meeting_config

def configure_default_provider():
    """Configure a default provider for testing"""
    # For now, we'll use a simple mock configuration
    # In production, this would read from environment variables or database
    
    # Try to configure Google Meet with environment variables
    import os
    
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    google_refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    
    if google_client_id and google_client_secret and google_refresh_token:
        credentials = GoogleMeetCredentials(
            client_id=google_client_id,
            client_secret=google_client_secret,
            refresh_token=google_refresh_token
        )
        if _meeting_config.configure_google_meet(credentials):
            logger.info("Default Google Meet provider configured from environment")
            return
    
    # Try to configure Zoom with environment variables
    zoom_api_key = os.getenv('ZOOM_API_KEY')
    zoom_api_secret = os.getenv('ZOOM_API_SECRET')
    zoom_account_id = os.getenv('ZOOM_ACCOUNT_ID')
    
    if zoom_api_key and zoom_api_secret and zoom_account_id:
        credentials = ZoomCredentials(
            api_key=zoom_api_key,
            api_secret=zoom_api_secret,
            account_id=zoom_account_id
        )
        if _meeting_config.configure_zoom(credentials):
            logger.info("Default Zoom provider configured from environment")
            return
    
    logger.warning("No meeting provider configured - meeting links will not be generated")

# Configure default provider on import
configure_default_provider()