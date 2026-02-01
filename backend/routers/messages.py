from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from database import get_database
from models.message import MessageCreate, MessageResponse, ConversationResponse, MarkAsReadRequest
from routers.auth import get_current_user

router = APIRouter()

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(current_user: dict = Depends(get_current_user)):
    """Get all conversations for the current user"""
    try:
        db = get_database()
        user_id = ObjectId(current_user["id"])
        user_type = current_user["user_type"]
        
        # Find all accepted requests involving this user
        if user_type == "client":
            requests_query = {"client_id": user_id, "status": "accepted"}
        else:  # lawyer
            requests_query = {"lawyer_id": user_id, "status": "accepted"}
        
        conversations = []
        
        async for request in db.lawyer_requests.find(requests_query).sort("updated_at", -1):
            # Get client and lawyer info
            client = await db.users.find_one({"_id": request["client_id"]})
            lawyer = await db.users.find_one({"_id": request["lawyer_id"]})
            
            if not client or not lawyer:
                continue
            
            # Get last message and unread count
            last_message = None
            unread_count = 0
            
            last_msg = await db.messages.find_one(
                {"request_id": request["_id"]},
                sort=[("created_at", -1)]
            )
            
            if last_msg:
                sender = client if last_msg["sender_id"] == request["client_id"] else lawyer
                last_message = MessageResponse(
                    id=str(last_msg["_id"]),
                    request_id=str(last_msg["request_id"]),
                    sender_id=str(last_msg["sender_id"]),
                    sender_type=last_msg["sender_type"],
                    sender_name=f"{sender['first_name']} {sender['last_name']}",
                    content=last_msg["content"],
                    message_type=last_msg["message_type"],
                    file_url=last_msg.get("file_url"),
                    file_name=last_msg.get("file_name"),
                    is_read=last_msg["is_read"],
                    created_at=last_msg["created_at"],
                    updated_at=last_msg["updated_at"]
                )
            
            # Count unread messages for current user
            unread_count = await db.messages.count_documents({
                "request_id": request["_id"],
                "sender_id": {"$ne": user_id},
                "is_read": False
            })
            
            conversation = ConversationResponse(
                request_id=str(request["_id"]),
                request_title=request["title"],
                client_name=f"{client['first_name']} {client['last_name']}",
                lawyer_name=f"{lawyer['first_name']} {lawyer['last_name']}",
                status=request["status"],
                last_message=last_message,
                unread_count=unread_count,
                messages=[],  # Will be loaded separately
                created_at=request["created_at"],
                updated_at=request["updated_at"]
            )
            
            conversations.append(conversation)
        
        return conversations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")

@router.get("/conversations/{request_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all messages for a specific conversation"""
    try:
        db = get_database()
        user_id = ObjectId(current_user["id"])
        request_obj_id = ObjectId(request_id)
        
        # Verify user has access to this conversation
        request_doc = await db.lawyer_requests.find_one({"_id": request_obj_id})
        if not request_doc:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if request_doc["client_id"] != user_id and request_doc["lawyer_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
        
        # Get all messages for this request
        messages = []
        async for message in db.messages.find({"request_id": request_obj_id}).sort("created_at", 1):
            # Get sender info
            sender = await db.users.find_one({"_id": message["sender_id"]})
            if not sender:
                continue
            
            message_response = MessageResponse(
                id=str(message["_id"]),
                request_id=str(message["request_id"]),
                sender_id=str(message["sender_id"]),
                sender_type=message["sender_type"],
                sender_name=f"{sender['first_name']} {sender['last_name']}",
                content=message["content"],
                message_type=message["message_type"],
                file_url=message.get("file_url"),
                file_name=message.get("file_name"),
                is_read=message["is_read"],
                created_at=message["created_at"],
                updated_at=message["updated_at"]
            )
            messages.append(message_response)
        
        # Mark messages as read for current user
        await db.messages.update_many(
            {
                "request_id": request_obj_id,
                "sender_id": {"$ne": user_id},
                "is_read": False
            },
            {"$set": {"is_read": True, "updated_at": datetime.utcnow()}}
        )
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")

@router.post("/conversations/{request_id}/messages", response_model=MessageResponse)
async def send_message(
    request_id: str,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Send a message in a conversation"""
    try:
        db = get_database()
        user_id = ObjectId(current_user["id"])
        request_obj_id = ObjectId(request_id)
        
        # Verify user has access to this conversation
        request_doc = await db.lawyer_requests.find_one({"_id": request_obj_id})
        if not request_doc:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if request_doc["client_id"] != user_id and request_doc["lawyer_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
        
        # Only allow messaging in accepted requests
        if request_doc["status"] != "accepted":
            raise HTTPException(status_code=400, detail="Can only message in accepted requests")
        
        # Create message document
        message_doc = {
            "request_id": request_obj_id,
            "sender_id": user_id,
            "sender_type": current_user["user_type"],
            "content": message_data.content,
            "message_type": message_data.message_type,
            "file_url": message_data.file_url,
            "file_name": message_data.file_name,
            "is_read": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert message
        result = await db.messages.insert_one(message_doc)
        
        # Update request's updated_at timestamp
        await db.lawyer_requests.update_one(
            {"_id": request_obj_id},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
        
        # Get sender info for response
        sender = await db.users.find_one({"_id": user_id})
        
        return MessageResponse(
            id=str(result.inserted_id),
            request_id=request_id,
            sender_id=str(user_id),
            sender_type=current_user["user_type"],
            sender_name=f"{sender['first_name']} {sender['last_name']}",
            content=message_data.content,
            message_type=message_data.message_type,
            file_url=message_data.file_url,
            file_name=message_data.file_name,
            is_read=False,
            created_at=message_doc["created_at"],
            updated_at=message_doc["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.put("/messages/mark-read")
async def mark_messages_as_read(
    mark_read_data: MarkAsReadRequest,
    current_user: dict = Depends(get_current_user)
):
    """Mark specific messages as read"""
    try:
        db = get_database()
        user_id = ObjectId(current_user["id"])
        
        # Convert message IDs to ObjectIds
        message_ids = [ObjectId(msg_id) for msg_id in mark_read_data.message_ids]
        
        # Update messages (only those not sent by current user)
        result = await db.messages.update_many(
            {
                "_id": {"$in": message_ids},
                "sender_id": {"$ne": user_id},
                "is_read": False
            },
            {"$set": {"is_read": True, "updated_at": datetime.utcnow()}}
        )
        
        return {"message": f"Marked {result.modified_count} messages as read"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking messages as read: {str(e)}")

@router.get("/conversations/{request_id}/info")
async def get_conversation_info(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get conversation details and participants"""
    try:
        db = get_database()
        user_id = ObjectId(current_user["id"])
        request_obj_id = ObjectId(request_id)
        
        # Get request details
        request_doc = await db.lawyer_requests.find_one({"_id": request_obj_id})
        if not request_doc:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if request_doc["client_id"] != user_id and request_doc["lawyer_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
        
        # Get client and lawyer info
        client = await db.users.find_one({"_id": request_doc["client_id"]})
        lawyer = await db.users.find_one({"_id": request_doc["lawyer_id"]})
        
        return {
            "request_id": request_id,
            "title": request_doc["title"],
            "description": request_doc["description"],
            "category": request_doc["category"],
            "status": request_doc["status"],
            "client": {
                "id": str(client["_id"]),
                "name": f"{client['first_name']} {client['last_name']}",
                "email": client["email"]
            },
            "lawyer": {
                "id": str(lawyer["_id"]),
                "name": f"{lawyer['first_name']} {lawyer['last_name']}",
                "email": lawyer["email"]
            },
            "meeting_slots": request_doc.get("meeting_slots", []),
            "selected_meeting": request_doc.get("selected_meeting"),
            "created_at": request_doc["created_at"],
            "updated_at": request_doc["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversation info: {str(e)}")