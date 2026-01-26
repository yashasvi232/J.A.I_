# J.A.I Chat System

## Overview
The J.A.I platform now includes a real-time chat system that allows clients and lawyers to communicate directly once a request has been accepted.

## Features

### 🗨️ Real-time Messaging
- Send and receive messages instantly
- Message history is preserved
- Read/unread status tracking
- Auto-refresh every 30 seconds

### 👥 User Access Control
- Only clients and lawyers involved in an accepted request can chat
- Secure authentication required
- Messages are private to the request participants

### 📱 Modern Interface
- Clean, WhatsApp-style chat interface
- Conversation list with unread counts
- Message timestamps and sender identification
- Responsive design for all devices

## API Endpoints

### Chat Messages
- `POST /api/chat/send` - Send a message
- `GET /api/chat/{request_id}/messages` - Get messages for a request
- `GET /api/chat/conversations` - Get all user conversations
- `POST /api/chat/{request_id}/mark-read` - Mark messages as read
- `DELETE /api/chat/{message_id}` - Delete a message
- `PUT /api/chat/{message_id}` - Edit a message

## How It Works

### 1. Request Acceptance
When a lawyer accepts a client's request, a chat becomes available for that specific request.

### 2. Chat Access
Both the client and lawyer can access the chat through:
- Direct link: `/pages/chat.html`
- Navigation menu in their dashboards
- Quick action buttons

### 3. Message Flow
```
Client sends message → Stored in database → Lawyer receives message
Lawyer replies → Stored in database → Client receives reply
```

### 4. Database Structure
Messages are stored in the `chat_messages` collection with:
- Request ID (links to the original request)
- Sender information (ID, type, name)
- Message content and metadata
- Timestamps and read status

## Usage Instructions

### For Clients:
1. Send a request to a lawyer
2. Wait for lawyer to accept the request
3. Access chat via dashboard or direct link
4. Start messaging with the lawyer

### For Lawyers:
1. Accept a client request
2. Access chat via dashboard or direct link
3. Communicate with the client about their legal needs
4. Coordinate meeting times and case details

## Testing

Use the test file `test_chat_system.html` to:
1. Create and accept a test request
2. Test chat functionality
3. Verify message sending and receiving
4. Open the full chat interface

## Security Features

- JWT token authentication required
- Users can only access chats for their own requests
- Messages are encrypted in transit
- Database indexes for optimal performance

## Future Enhancements

- File sharing capabilities
- Voice message support
- Video call integration
- Message search functionality
- Push notifications
- Mobile app support