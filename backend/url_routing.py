"""
Clean URL Routing System for J.A.I Platform
Provides clean URLs instead of file-based paths
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
from fastapi import Request, HTTPException, Depends
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)

@dataclass
class RouteConfig:
    """Configuration for a clean URL route"""
    clean_path: str
    html_file: str
    requires_auth: bool = False
    allowed_user_types: Optional[List[str]] = None
    redirect_if_unauthenticated: str = "/login"

@dataclass
class UserContext:
    """User authentication context for routing decisions"""
    user_id: Optional[str] = None
    user_type: Optional[str] = None
    email: Optional[str] = None
    is_authenticated: bool = False
    
    @property
    def is_client(self) -> bool:
        return self.user_type == "client"
    
    @property
    def is_lawyer(self) -> bool:
        return self.user_type == "lawyer"

# Route configuration mapping
ROUTE_MAPPINGS: Dict[str, RouteConfig] = {
    "/": RouteConfig("/", "index.html"),
    "/login": RouteConfig("/login", "client-login.html"),
    "/dashboard": RouteConfig("/dashboard", "client-dashboard.html", requires_auth=True),
    "/lawyers": RouteConfig("/lawyers", "lawyers.html"),
    "/terms": RouteConfig("/terms", "terms.html"),
}

# Legacy URL to clean URL mappings for redirects
LEGACY_REDIRECTS: Dict[str, str] = {
    "index": "/",
    "client-login": "/login",
    "lawyer-login": "/login?type=lawyer",
    "client-dashboard": "/dashboard",
    "lawyer-dashboard": "/dashboard",
    "lawyers": "/lawyers",
    "terms": "/terms",
    "client-terms": "/terms?type=client",
    "lawyer-terms": "/terms?type=lawyer",
}

async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserContext]:
    """
    Extract user context from request (optional - returns None if not authenticated)
    This is a placeholder implementation - integrate with your existing auth system
    """
    try:
        # TODO: Integrate with your existing JWT authentication system
        # For now, return a basic context based on session or headers
        
        # Check for user info in session/cookies (placeholder)
        user_type = request.headers.get("X-User-Type")  # Temporary for testing
        user_id = request.headers.get("X-User-ID")      # Temporary for testing
        
        if user_type and user_id:
            return UserContext(
                user_id=user_id,
                user_type=user_type,
                is_authenticated=True
            )
        
        return None
        
    except Exception as e:
        logger.warning(f"Error extracting user context: {e}")
        return None

async def get_current_user_required(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserContext:
    """
    Extract user context from request (required - raises exception if not authenticated)
    """
    user_context = await get_current_user_optional(request, credentials)
    
    if not user_context or not user_context.is_authenticated:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return user_context

def get_html_file_for_route(clean_path: str, user_context: Optional[UserContext] = None) -> str:
    """
    Determine which HTML file to serve for a given clean path and user context
    """
    route_config = ROUTE_MAPPINGS.get(clean_path)
    
    if not route_config:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Handle user-type-specific routing
    if clean_path == "/login":
        # Check for type parameter or user context to determine login page
        return "lawyer-login.html"  # This will be determined by query params in the handler
    
    elif clean_path == "/dashboard":
        if user_context and user_context.is_lawyer:
            return "lawyer-dashboard.html"
        else:
            return "client-dashboard.html"
    
    elif clean_path == "/terms":
        # Default to general terms, can be overridden by query params
        return "terms.html"
    
    return route_config.html_file

def build_file_path(html_file: str) -> str:
    """Build the full file path for an HTML file"""
    return f"../pages/{html_file}"

def file_exists(file_path: str) -> bool:
    """Check if a file exists"""
    return os.path.exists(file_path)

async def handle_clean_url(
    clean_path: str,
    request: Request,
    user_context: Optional[UserContext] = None
) -> FileResponse:
    """
    Handle a clean URL request and return the appropriate HTML file
    """
    try:
        # Get route configuration
        route_config = ROUTE_MAPPINGS.get(clean_path)
        
        if not route_config:
            raise HTTPException(status_code=404, detail="Page not found")
        
        # Check authentication requirements
        if route_config.requires_auth:
            if not user_context or not user_context.is_authenticated:
                # Redirect to login with return URL
                return RedirectResponse(
                    url=f"{route_config.redirect_if_unauthenticated}?next={clean_path}",
                    status_code=302
                )
        
        # Handle special routing logic
        html_file = route_config.html_file
        
        # Special handling for login page based on query parameters
        if clean_path == "/login":
            login_type = request.query_params.get("type", "client")
            if login_type == "lawyer":
                html_file = "lawyer-login.html"
            else:
                html_file = "client-login.html"
        
        # Special handling for dashboard based on user type
        elif clean_path == "/dashboard":
            if user_context and user_context.is_lawyer:
                html_file = "lawyer-dashboard.html"
            else:
                html_file = "client-dashboard.html"
        
        # Special handling for terms based on query parameters
        elif clean_path == "/terms":
            terms_type = request.query_params.get("type")
            if terms_type == "client":
                html_file = "client-terms.html"
            elif terms_type == "lawyer":
                html_file = "lawyer-terms.html"
            else:
                html_file = "terms.html"
        
        # Build file path and check if it exists
        file_path = build_file_path(html_file)
        
        if not file_exists(file_path):
            logger.error(f"HTML file not found: {file_path}")
            raise HTTPException(status_code=404, detail="Page not found")
        
        # Serve the file with appropriate headers
        return FileResponse(
            file_path,
            headers={
                "Cache-Control": "public, max-age=300",  # 5 minutes cache
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling clean URL {clean_path}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def handle_legacy_redirect(
    filename: str,
    request: Request
) -> RedirectResponse:
    """
    Handle legacy HTML file URLs and redirect to clean URLs
    """
    try:
        # Get the clean URL for this legacy filename
        clean_url = LEGACY_REDIRECTS.get(filename)
        
        if not clean_url:
            # If no mapping exists, try to serve the file directly (fallback)
            raise HTTPException(status_code=404, detail="Page not found")
        
        # Preserve query parameters
        query_string = str(request.query_params)
        if query_string:
            clean_url += f"?{query_string}"
        
        # Return permanent redirect (301)
        return RedirectResponse(url=clean_url, status_code=301)
        
    except Exception as e:
        logger.error(f"Error handling legacy redirect for {filename}: {e}")
        raise HTTPException(status_code=404, detail="Page not found")

def suggest_similar_urls(invalid_path: str) -> List[str]:
    """
    Suggest similar valid URLs for a given invalid path
    """
    suggestions = []
    
    # Simple similarity matching based on common patterns
    invalid_lower = invalid_path.lower().strip("/")
    
    for valid_path in ROUTE_MAPPINGS.keys():
        valid_lower = valid_path.lower().strip("/")
        
        # Check for partial matches
        if invalid_lower in valid_lower or valid_lower in invalid_lower:
            suggestions.append(valid_path)
        
        # Check for common typos
        if len(invalid_lower) > 0 and len(valid_lower) > 0:
            # Simple edit distance check (very basic)
            if abs(len(invalid_lower) - len(valid_lower)) <= 2:
                suggestions.append(valid_path)
    
    # Remove duplicates and limit to 3 suggestions
    return list(set(suggestions))[:3]

async def handle_404_error(request: Request) -> FileResponse:
    """
    Handle 404 errors with a custom error page
    """
    try:
        # Log the invalid URL attempt
        logger.warning(f"404 error for URL: {request.url.path}")
        
        # Get suggestions for similar URLs
        suggestions = suggest_similar_urls(request.url.path)
        
        # For now, serve a basic 404 page
        # TODO: Create a custom 404.html page with navigation and suggestions
        error_page_path = "../pages/index.html"  # Fallback to home page
        
        if file_exists(error_page_path):
            return FileResponse(
                error_page_path,
                status_code=404,
                headers={
                    "Cache-Control": "no-cache",
                    "X-Suggestions": ",".join(suggestions) if suggestions else ""
                }
            )
        else:
            raise HTTPException(status_code=404, detail="Page not found")
            
    except Exception as e:
        logger.error(f"Error handling 404: {e}")
        raise HTTPException(status_code=404, detail="Page not found")