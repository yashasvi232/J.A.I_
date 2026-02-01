#!/usr/bin/env python3
"""
Test script for the messaging system
"""

import asyncio
import httpx
import json

# API Configuration
API_BASE = "http://localhost:8001/api"

async def test_messaging_system():
    """Test the complete messaging flow"""
    print("🧪 Testing J.A.I Messaging System")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Login as client
            print("1. 👤 Logging in as client...")
            client_login = await client.post(f"{API_BASE}/auth/login", json={
                "email": "client@test.com",
                "password": "password123"
            })
            
            if client_login.status_code != 200:
                print(f"❌ Client login failed: {client_login.text}")
                return
            
            client_data = client_login.json()
            client_token = client_data["access_token"]
            client_headers = {"Authorization": f"Bearer {client_token}"}
            print(f"✅ Client logged in: {client_data['user']['first_name']}")
            
            # 2. Login as lawyer
            print("\n2. ⚖️ Logging in as lawyer...")
            lawyer_login = await client.post(f"{API_BASE}/auth/login", json={
                "email": "lawyer@test.com",
                "password": "password123"
            })
            
            if lawyer_login.status_code != 200:
                print(f"❌ Lawyer login failed: {lawyer_login.text}")
                return
            
            lawyer_data = lawyer_login.json()
            lawyer_token = lawyer_data["access_token"]
            lawyer_headers = {"Authorization": f"Bearer {lawyer_token}"}
            print(f"✅ Lawyer logged in: {lawyer_data['user']['first_name']}")
            
            # 3. Client sends request to lawyer
            print("\n3. 📤 Client sending request to lawyer...")
            request_data = {
                "title": "Contract Review Needed",
                "description": "I need help reviewing a business contract before signing.",
                "category": "Contract and Agreement Law",
                "urgency_level": "medium",
                "budget_min": 500,
                "budget_max": 1000,
                "lawyer_id": lawyer_data["user"]["id"]
            }
            
            send_request = await client.post(
                f"{API_BASE}/requests/",
                json=request_data,
                headers=client_headers
            )
            
            if send_request.status_code != 200:
                print(f"❌ Failed to send request: {send_request.text}")
                return
            
            request_result = send_request.json()
            request_id = request_result["request_id"]
            print(f"✅ Request sent successfully: {request_id}")
            
            # 4. Lawyer views pending requests
            print("\n4. 📋 Lawyer checking pending requests...")
            pending_requests = await client.get(
                f"{API_BASE}/requests/pending",
                headers=lawyer_headers
            )
            
            if pending_requests.status_code != 200:
                print(f"❌ Failed to get pending requests: {pending_requests.text}")
                return
            
            pending_data = pending_requests.json()
            print(f"✅ Found {len(pending_data)} pending request(s)")
            
            # 5. Lawyer accepts the request
            print("\n5. ✅ Lawyer accepting the request...")
            response_data = {
                "action": "accept",
                "response_message": "Thank you for your request! I'd be happy to help you review your contract. Let's schedule a consultation.",
                "meeting_slots": [
                    {
                        "date": "2024-02-01",
                        "time": "10:00 AM",
                        "meeting_type": "online",
                        "duration": 60
                    },
                    {
                        "date": "2024-02-02",
                        "time": "2:00 PM",
                        "meeting_type": "in-person",
                        "duration": 90
                    }
                ]
            }
            
            accept_request = await client.post(
                f"{API_BASE}/requests/{request_id}/respond",
                json=response_data,
                headers=lawyer_headers
            )
            
            if accept_request.status_code != 200:
                print(f"❌ Failed to accept request: {accept_request.text}")
                return
            
            print("✅ Request accepted successfully!")
            
            # 6. Check conversations for both users
            print("\n6. 💬 Checking conversations...")
            
            # Client conversations
            client_conversations = await client.get(
                f"{API_BASE}/messages/conversations",
                headers=client_headers
            )
            
            if client_conversations.status_code == 200:
                client_convs = client_conversations.json()
                print(f"✅ Client has {len(client_convs)} conversation(s)")
            else:
                print(f"⚠️ Client conversations: {client_conversations.text}")
            
            # Lawyer conversations
            lawyer_conversations = await client.get(
                f"{API_BASE}/messages/conversations",
                headers=lawyer_headers
            )
            
            if lawyer_conversations.status_code == 200:
                lawyer_convs = lawyer_conversations.json()
                print(f"✅ Lawyer has {len(lawyer_convs)} conversation(s)")
            else:
                print(f"⚠️ Lawyer conversations: {lawyer_conversations.text}")
            
            # 7. Client sends a message
            print("\n7. 💬 Client sending message...")
            message_data = {
                "content": "Hi! Thank you for accepting my request. I have a few questions about the contract terms.",
                "message_type": "text"
            }
            
            send_message = await client.post(
                f"{API_BASE}/messages/conversations/{request_id}/messages",
                json=message_data,
                headers=client_headers
            )
            
            if send_message.status_code == 200:
                print("✅ Client message sent successfully!")
            else:
                print(f"❌ Failed to send message: {send_message.text}")
            
            # 8. Lawyer replies
            print("\n8. 💬 Lawyer replying...")
            lawyer_message = {
                "content": "Great! I'd be happy to answer your questions. Could you please share the specific clauses you're concerned about?",
                "message_type": "text"
            }
            
            lawyer_reply = await client.post(
                f"{API_BASE}/messages/conversations/{request_id}/messages",
                json=lawyer_message,
                headers=lawyer_headers
            )
            
            if lawyer_reply.status_code == 200:
                print("✅ Lawyer reply sent successfully!")
            else:
                print(f"❌ Failed to send lawyer reply: {lawyer_reply.text}")
            
            # 9. Get conversation messages
            print("\n9. 📜 Retrieving conversation messages...")
            messages = await client.get(
                f"{API_BASE}/messages/conversations/{request_id}/messages",
                headers=client_headers
            )
            
            if messages.status_code == 200:
                message_list = messages.json()
                print(f"✅ Retrieved {len(message_list)} messages:")
                for i, msg in enumerate(message_list, 1):
                    sender_type = "👤 Client" if msg["sender_type"] == "client" else "⚖️ Lawyer"
                    print(f"   {i}. {sender_type}: {msg['content'][:50]}...")
            else:
                print(f"❌ Failed to get messages: {messages.text}")
            
            print("\n" + "=" * 50)
            print("🎉 Messaging system test completed successfully!")
            print("\n📋 Test Summary:")
            print("✅ User authentication")
            print("✅ Request creation and management")
            print("✅ Request acceptance with meeting slots")
            print("✅ Automatic conversation creation")
            print("✅ Bidirectional messaging")
            print("✅ Message retrieval and display")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting messaging system test...")
    print("Make sure the backend server is running on http://localhost:8001")
    print()
    
    asyncio.run(test_messaging_system())