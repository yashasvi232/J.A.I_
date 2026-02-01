from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from database import get_database
from routers.auth import get_current_user

router = APIRouter()

@router.post("/")
async def send_lawyer_request(request_data: dict, current_user: dict = Depends(get_current_user)):
    """Send a request to a lawyer"""
    try:
        db = get_database()
        
        # Validate required fields
        required_fields = ["title", "description", "category", "lawyer_id"]
        for field in required_fields:
            if not request_data.get(field):
                raise HTTPException(status_code=400, detail=f"{field} is required")
        
        # Create request document
        request_doc = {
            "client_id": ObjectId(current_user["id"]),
            "lawyer_id": ObjectId(request_data["lawyer_id"]),
            "title": request_data["title"],
            "description": request_data["description"],
            "category": request_data["category"],
            "urgency_level": request_data.get("urgency_level", "medium"),
            "budget_min": request_data.get("budget_min"),
            "budget_max": request_data.get("budget_max"),
            "preferred_meeting_type": request_data.get("preferred_meeting_type"),
            "location": request_data.get("location"),
            "additional_notes": request_data.get("additional_notes"),
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "response_message": None,
            "responded_at": None,
            "meeting_slots": None,
            "selected_meeting": None
        }
        
        result = await db.lawyer_requests.insert_one(request_doc)
        
        return {
            "message": "Request sent successfully",
            "request_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending request: {str(e)}")

@router.get("/")
async def get_user_requests(current_user: dict = Depends(get_current_user)):
    """Get all requests for the current user"""
    try:
        db = get_database()
        user_id = ObjectId(current_user["id"])
        user_type = current_user["user_type"]
        
        # Build query based on user type
        if user_type == "client":
            query = {"client_id": user_id}
        else:  # lawyer
            query = {"lawyer_id": user_id}
        
        requests = []
        async for request in db.lawyer_requests.find(query).sort("created_at", -1):
            # Get client and lawyer info
            client = await db.users.find_one({"_id": request["client_id"]})
            lawyer = await db.users.find_one({"_id": request["lawyer_id"]})
            
            if not client or not lawyer:
                continue
            
            request_data = {
                "id": str(request["_id"]),
                "title": request["title"],
                "description": request["description"],
                "category": request["category"],
                "urgency_level": request["urgency_level"],
                "budget_min": request.get("budget_min"),
                "budget_max": request.get("budget_max"),
                "status": request["status"],
                "created_at": request["created_at"],
                "updated_at": request["updated_at"],
                "response_message": request.get("response_message"),
                "responded_at": request.get("responded_at"),
                "meeting_slots": request.get("meeting_slots"),
                "selected_meeting": request.get("selected_meeting"),
                "client_name": f"{client['first_name']} {client['last_name']}",
                "client_email": client["email"],
                "lawyer_name": f"{lawyer['first_name']} {lawyer['last_name']}",
                "lawyer_email": lawyer["email"]
            }
            requests.append(request_data)
        
        return requests
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching requests: {str(e)}")

@router.get("/pending")
async def get_pending_requests(current_user: dict = Depends(get_current_user)):
    """Get pending requests for lawyers"""
    try:
        if current_user["user_type"] != "lawyer":
            raise HTTPException(status_code=403, detail="Only lawyers can access pending requests")
        
        db = get_database()
        lawyer_id = ObjectId(current_user["id"])
        
        requests = []
        async for request in db.lawyer_requests.find({
            "lawyer_id": lawyer_id,
            "status": "pending"
        }).sort("created_at", -1):
            # Get client info
            client = await db.users.find_one({"_id": request["client_id"]})
            if not client:
                continue
            
            request_data = {
                "id": str(request["_id"]),
                "title": request["title"],
                "description": request["description"],
                "category": request["category"],
                "urgency_level": request["urgency_level"],
                "budget_min": request.get("budget_min"),
                "budget_max": request.get("budget_max"),
                "preferred_meeting_type": request.get("preferred_meeting_type"),
                "location": request.get("location"),
                "additional_notes": request.get("additional_notes"),
                "status": request["status"],
                "created_at": request["created_at"],
                "client_name": f"{client['first_name']} {client['last_name']}",
                "client_email": client["email"]
            }
            requests.append(request_data)
        
        return requests
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pending requests: {str(e)}")

@router.post("/{request_id}/respond")
async def respond_to_request(
    request_id: str,
    response_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Respond to a lawyer request (accept/reject)"""
    try:
        if current_user["user_type"] != "lawyer":
            raise HTTPException(status_code=403, detail="Only lawyers can respond to requests")
        
        db = get_database()
        request_obj_id = ObjectId(request_id)
        lawyer_id = ObjectId(current_user["id"])
        
        # Get the request
        request_doc = await db.lawyer_requests.find_one({
            "_id": request_obj_id,
            "lawyer_id": lawyer_id,
            "status": "pending"
        })
        
        if not request_doc:
            raise HTTPException(status_code=404, detail="Request not found or already responded")
        
        action = response_data.get("action")
        if action not in ["accept", "reject"]:
            raise HTTPException(status_code=400, detail="Action must be 'accept' or 'reject'")
        
        # Update request
        update_data = {
            "status": "accepted" if action == "accept" else "rejected",
            "response_message": response_data.get("response_message"),
            "responded_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Add meeting slots if accepting
        if action == "accept" and response_data.get("meeting_slots"):
            update_data["meeting_slots"] = response_data["meeting_slots"]
        
        await db.lawyer_requests.update_one(
            {"_id": request_obj_id},
            {"$set": update_data}
        )
        
        # If accepted, send a welcome message to start the conversation
        if action == "accept":
            # Create a formatted message with meeting slots
            meeting_slots_text = ""
            if response_data.get("meeting_slots"):
                meeting_slots_text = "\n\n📅 Available Meeting Times:\n"
                for i, slot in enumerate(response_data["meeting_slots"], 1):
                    meeting_type_emoji = {"online": "💻", "in-person": "🏢", "phone": "📞"}.get(slot.get("meeting_type", "online"), "💻")
                    meeting_slots_text += f"{i}. {slot['date']} at {slot['time']} ({meeting_type_emoji} {slot.get('meeting_type', 'online').title()}) - {slot.get('duration', 60)} minutes\n"
                meeting_slots_text += "\nPlease let me know which time works best for you!"
            
            welcome_content = response_data.get("response_message", "Thank you for your request. I'm happy to help with your case. Let's discuss the details.") + meeting_slots_text
            
            welcome_message = {
                "request_id": request_obj_id,
                "sender_id": lawyer_id,
                "sender_type": "lawyer",
                "content": welcome_content,
                "message_type": "text",
                "is_read": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.messages.insert_one(welcome_message)
        
        return {"message": f"Request {action}ed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error responding to request: {str(e)}")

@router.put("/{request_id}")
async def update_request(
    request_id: str,
    update_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update a request (only by client who created it)"""
    try:
        db = get_database()
        request_obj_id = ObjectId(request_id)
        client_id = ObjectId(current_user["id"])
        
        # Verify ownership
        request_doc = await db.lawyer_requests.find_one({
            "_id": request_obj_id,
            "client_id": client_id
        })
        
        if not request_doc:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Only allow updates to pending requests
        if request_doc["status"] != "pending":
            raise HTTPException(status_code=400, detail="Can only update pending requests")
        
        # Prepare update data
        allowed_fields = [
            "title", "description", "category", "urgency_level",
            "budget_min", "budget_max", "preferred_meeting_type",
            "location", "additional_notes"
        ]
        
        update_fields = {}
        for field in allowed_fields:
            if field in update_data:
                update_fields[field] = update_data[field]
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        update_fields["updated_at"] = datetime.utcnow()
        
        await db.lawyer_requests.update_one(
            {"_id": request_obj_id},
            {"$set": update_fields}
        )
        
        return {"message": "Request updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating request: {str(e)}")

@router.delete("/{request_id}")
async def cancel_request(request_id: str, current_user: dict = Depends(get_current_user)):
    """Cancel a request (only by client who created it)"""
    try:
        db = get_database()
        request_obj_id = ObjectId(request_id)
        client_id = ObjectId(current_user["id"])
        
        # Verify ownership
        request_doc = await db.lawyer_requests.find_one({
            "_id": request_obj_id,
            "client_id": client_id
        })
        
        if not request_doc:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Only allow cancellation of pending requests
        if request_doc["status"] != "pending":
            raise HTTPException(status_code=400, detail="Can only cancel pending requests")
        
        # Update status to cancelled
        await db.lawyer_requests.update_one(
            {"_id": request_obj_id},
            {"$set": {
                "status": "cancelled",
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {"message": "Request cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling request: {str(e)}")