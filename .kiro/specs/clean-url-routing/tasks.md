# Implementation Plan: Clean URL Routing System

## Overview

This implementation plan converts the existing file-based URL system to clean URL routing using FastAPI. The approach involves creating new route handlers for clean URLs, implementing user context-aware routing, and maintaining backward compatibility through redirects.

## Tasks

- [ ] 1. Set up clean URL routing infrastructure
  - Create URL mapping configuration system
  - Define route configuration data structures
  - Set up user context service for authentication-aware routing
  - _Requirements: 1.1, 1.2, 2.4_

- [ ]* 1.1 Write property test for URL mapping configuration
  - **Property 1: Clean URL Mapping**
  - **Validates: Requirements 1.1, 1.3, 1.4**

- [ ] 2. Implement user context service
  - [ ] 2.1 Create UserContext data model and authentication helpers
    - Implement UserContext dataclass with user type detection
    - Create get_current_user_optional and get_current_user_required functions
    - Add JWT token parsing and validation
    - _Requirements: 2.4_

  - [ ]* 2.2 Write property test for user context extraction
    - **Property 4: User Context Extraction**
    - **Validates: Requirements 2.4**

- [ ] 3. Create clean URL route handlers
  - [ ] 3.1 Implement main clean URL handler function
    - Create handle_clean_url FastAPI endpoint
    - Add route resolution logic using configuration mapping
    - Implement file serving with proper HTTP headers
    - _Requirements: 1.1, 1.3, 1.4, 5.1, 5.2_

  - [ ] 3.2 Implement user-type-specific dashboard routing
    - Add logic to serve different dashboards based on user type
    - Handle authentication requirements for protected routes
    - Implement redirect to login for unauthenticated users
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 3.3 Write property tests for dashboard routing
    - **Property 2: User-Type-Specific Dashboard Routing**
    - **Property 3: Authentication-Based Access Control**
    - **Validates: Requirements 2.1, 2.2, 2.3**

- [ ] 4. Checkpoint - Test core routing functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement backward compatibility system
  - [ ] 5.1 Create legacy URL redirect handler
    - Implement redirect_legacy_url FastAPI endpoint
    - Add mapping from legacy HTML URLs to clean URLs
    - Ensure 301 redirects with query parameter preservation
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ]* 5.2 Write property test for legacy URL redirection
    - **Property 5: Legacy URL Redirection**
    - **Validates: Requirements 3.1, 3.2, 3.3**

- [ ] 6. Implement error handling and 404 pages
  - [ ] 6.1 Create custom 404 error handling
    - Implement custom 404 error page with navigation options
    - Add URL suggestion system for similar valid routes
    - Implement request logging for monitoring invalid URLs
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ]* 6.2 Write property tests for error handling
    - **Property 7: 404 Error Handling**
    - **Property 8: Request Logging**
    - **Property 9: URL Suggestion**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ] 7. Ensure static asset compatibility
  - [ ] 7.1 Verify static file serving continues to work
    - Test that CSS, JS, and image files are served correctly
    - Ensure clean URL routing doesn't interfere with static assets
    - Add proper caching headers for static files
    - _Requirements: 3.4_

  - [ ]* 7.2 Write property test for static asset serving
    - **Property 6: Static Asset Serving**
    - **Validates: Requirements 3.4**

- [ ] 8. Add HTTP optimization features
  - [ ] 8.1 Implement HTTP compression and caching
    - Add HTTP compression support for HTML responses
    - Implement proper caching headers for SEO optimization
    - Add meta tags for SEO in served HTML pages
    - _Requirements: 5.1, 5.2, 5.4_

  - [ ]* 8.2 Write property tests for HTTP optimization
    - **Property 10: HTTP Headers and Caching**
    - **Property 11: HTTP Compression Support**
    - **Validates: Requirements 5.1, 5.2, 5.4**

- [ ] 9. Integration and route registration
  - [ ] 9.1 Register all new routes in main FastAPI application
    - Add clean URL routes to the main app before existing catch-all routes
    - Ensure proper route precedence and ordering
    - Update existing route handlers to avoid conflicts
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ] 9.2 Update existing HTML files for clean URL navigation
    - Update navigation links in HTML files to use clean URLs
    - Ensure form actions and redirects use clean URLs
    - Test that all internal links work with new routing system
    - _Requirements: 1.5_

- [ ]* 9.3 Write integration tests for complete routing system
  - Test end-to-end user journeys with clean URLs
  - Verify authentication flows work with new routing
  - Test backward compatibility with legacy URLs

- [ ] 10. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Route registration must happen before existing catch-all routes to avoid conflicts