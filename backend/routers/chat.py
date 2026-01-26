from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from models.user import UserInDB
from models.chat import (
    ChatMessage, ChatMessageCreate, ChatMessageResponse, 
    ChatSummary, MessageType
)
from routers.auth import get_current_user
from database import get_database

router = APIRouter()

@router.post("/send", response_model=ChatMessageResponse)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Send a message in a request chat"""
    db = get_database()
    
    # Verify the request exists and user has access
    request_doc = await db.lawyer_requests.find_one({"_id": ObjectId(message_data.request_id)})
    
    if not request_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check if user is part of this request (client or lawyer)
    user_id = ObjectId(current_user.id)
    if user_id not in [request_doc["client_id"], request_doc["lawyer_id"]]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this chat"
        )
    
    # Only allow chat for accepted or rejected requests (not pending)
    if request_doc["status"] == "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat is only available after the lawyer responds to the request"
        )
    
    # Create message document
    message_dict = {
        "request_id": ObjectId(message_data.request_id),
        "sender_id": user_id,
        "sender_type": current_user.user_type,
        "sender_name": f"{current_user.first_name} {current_user.last_name}",
        "message_type": message_data.message_type,
        "content": message_data.content,
        "file_url": message_data.file_url,
        "file_name": message_data.file_name,
        "timestamp": datetime.utcnow(),
        "is_read": False,
        "edited_at": None
    }
    
    # Insert message
    result = await db.chat_messages.insert_one(message_dict)
    created_message = await db.chat_messages.find_one({"_id": result.inserted_id})
    
    # Update request's last activity
    await db.lawyer_requests.update_one(
        {"_id": ObjectId(message_data.request_id)},
        {"$set": {"last_activity": datetime.utcnow()}}
    )
    
    # Return response
    return ChatMessageResponse(
        id=str(created_message["_id"]),
        request_id=message_data.request_id,
        sender_id=str(created_message["sender_id"]),
        sender_type=created_message["sender_type"],
        sender_name=created_message["sender_name"],
        message_type=created_message["message_type"],
        content=created_message["content"],
        file_url=created_message.get("file_url"),
        file_name=created_message.get("file_name"),
        timestamp=created_message["timestamp"],
        is_read=created_message["is_read"],
        edited_at=created_message.get("edited_at")
    )

@router.get("/{request_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    request_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get messages for a specific request chat"""
    db = get_database()
    
    # Verify the request exists and user has access
    request_doc = await db.lawyer_requests.find_one({"_id": ObjectId(request_id)})
    
    if not request_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check if user is part of this request
    user_id = ObjectId(current_user.id)
    if user_id not in [request_doc["client_id"], request_doc["lawyer_id"]]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this chat"
        )
    
    # Get messages
    messages = await db.chat_messages.find({
        "request_id": ObjectId(request_id)
    }).sort("timestamp", 1).skip(offset).limit(limit).to_list(length=limit)
    
    # Mark messages as read for current user
    await db.chat_messages.update_many(
        {
            "request_id": ObjectId(request_id),
            "sender_id": {"$ne": user_id},
            "is_read": False
        },
        {"$set": {"is_read": True}}
    )
    
    # Format response
    response_messages = []
    for msg in messages:
        response_messages.append(ChatMessageResponse(
            id=str(msg["_id"]),
            request_id=request_id,
            sender_id=str(msg["sender_id"]),
            sender_type=msg["sender_type"],
            sender_name=msg["sender_name"],
            message_type=msg["message_type"],
            content=msg["content"],
            file_url=msg.get("file_url"),
            file_name=msg.get("file_name"),
            timestamp=msg["timestamp"],
            is_read=msg["is_read"],
            edited_at=msg.get("edited_at")
        ))
    
    return response_messages

@router.get("/conversations", response_model=List[ChatSummary])
async def get_user_conversations(current_user: UserInDB = Depends(get_current_user)):
    """Get all chat conversations for current user"""
    db = get_database()
    
    # Get accepted requests for current user
    if current_user.user_type == "client":
        requests = await db.lawyer_requests.find({
            "client_id": ObjectId(current_user.id),
            "status": "accepted"
        }).to_list(length=100)
    else:  # lawyer
        requests = await db.lawyer_requests.find({
            "lawyer_id": ObjectId(current_user.id),
            "status": "accepted"
        }).to_list(length=100)
    
    conversations = []
    
    for request_doc in requests:
        # Get client and lawyer info
        client = await db.users.find_one({"_id": request_doc["client_id"]})
        lawyer = await db.users.find_one({"_id": request_doc["lawyer_id"]})
        
        # Get last message
        last_message_doc = await db.chat_messages.find_one(
            {"request_id": request_doc["_id"]},
            sort=[("timestamp", -1)]
        )
        
        # Count unread messages for current user
        unread_count = await db.chat_messages.count_documents({
            "request_id": request_doc["_id"],
            "sender_id": {"$ne": ObjectId(current_user.id)},
            "is_read": False
        })
        
        # Count total messages
        total_messages = await db.chat_messages.count_documents({
            "request_id": request_doc["_id"]
        })
        
        conversation = ChatSummary(
            request_id=str(request_doc["_id"]),
            request_title=request_doc["title"],
            client_name=f"{client['first_name']} {client['last_name']}" if client else "Unknown",
            lawyer_name=f"{lawyer['first_name']} {lawyer['last_name']}" if lawyer else "Unknown",
            last_message=last_message_doc["content"] if last_message_doc else None,
            last_message_time=last_message_doc["timestamp"] if last_message_doc else None,
            unread_count=unread_count,
            total_messages=total_messages
        )
        
        conversations.append(conversation)
    
    # Sort by last message time (most recent first)
    conversations.sort(key=lambda x: x.last_message_time or datetime.min, reverse=True)
    
    return conversations

@router.post("/{request_id}/mark-read")
async def mark_messages_read(
    request_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Mark all messages in a chat as read"""
    db = get_database()
    
    # Verify access
    request_doc = await db.lawyer_requests.find_one({"_id": ObjectId(request_id)})
    if not request_doc:
        raise HTTPException(status_code=404, detail="Request not found")
    
    user_id = ObjectId(current_user.id)
    if user_id not in [request_doc["client_id"], request_doc["lawyer_id"]]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Mark messages as read
    result = await db.chat_messages.update_many(
        {
            "request_id": ObjectId(request_id),
            "sender_id": {"$ne": user_id},
            "is_read": False
        },
        {"$set": {"is_read": True}}
    )
    
    return {"message": f"Marked {result.modified_count} messages as read"}

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete a message (only sender can delete)"""
    db = get_database()
    
    # Find message
    message = await db.chat_messages.find_one({"_id": ObjectId(message_id)})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Check if current user is the sender
    if str(message["sender_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own messages")
    
    # Delete message
    await db.chat_messages.delete_one({"_id": ObjectId(message_id)})
    
    return {"message": "Message deleted successfully"}

@router.put("/{message_id}")
async def edit_message(
    message_id: str,
    new_content: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """Edit a message (only sender can edit)"""
    db = get_database()
    
    # Find message
    message = await db.chat_messages.find_one({"_id": ObjectId(message_id)})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Check if current user is the sender
    if str(message["sender_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own messages")
    
    # Update message
    await db.chat_messages.update_one(
        {"_id": ObjectId(message_id)},
        {
            "$set": {
                "content": new_content.get("content", message["content"]),
                "edited_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Message updated successfully"}