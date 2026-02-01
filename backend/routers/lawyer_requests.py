from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from models.user import UserInDB
from models.lawyer_request import (
    LawyerRequestCreate, LawyerRequestResponse, RequestActionRequest,
    RequestUpdateRequest, LawyerRequestInDB, RequestStatus
)
from routers.auth import get_current_user
from database import get_database

router = APIRouter()

@router.post("/", response_model=LawyerRequestResponse)
async def create_lawyer_request(
    request_data: LawyerRequestCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create a new lawyer request (client only)"""
    if current_user.user_type != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can create lawyer requests"
        )
    
    db = get_database()
    
    # Verify lawyer exists
    lawyer = await db.users.find_one({
        "_id": ObjectId(request_data.lawyer_id),
        "user_type": "lawyer"
    })
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )
    
    # Create request document
    request_dict = request_data.dict()
    request_dict["client_id"] = ObjectId(current_user.id)
    request_dict["lawyer_id"] = ObjectId(request_data.lawyer_id)
    request_dict["status"] = RequestStatus.PENDING
    request_dict["created_at"] = datetime.utcnow()
    request_dict["updated_at"] = datetime.utcnow()
    
    # Insert into database
    result = await db.lawyer_requests.insert_one(request_dict)
    created_request = await db.lawyer_requests.find_one({"_id": result.inserted_id})
    
    # Get client and lawyer info for response
    client = await db.users.find_one({"_id": ObjectId(current_user.id)})
    
    # Format response
    response_data = LawyerRequestResponse(
        id=str(created_request["_id"]),
        title=created_request["title"],
        description=created_request["description"],
        category=created_request["category"],
        urgency_level=created_request["urgency_level"],
        budget_min=created_request.get("budget_min"),
        budget_max=created_request.get("budget_max"),
        preferred_meeting_type=created_request.get("preferred_meeting_type"),
        location=created_request.get("location"),
        additional_notes=created_request.get("additional_notes"),
        status=created_request["status"],
        created_at=created_request["created_at"],
        updated_at=created_request["updated_at"],
        response_message=created_request.get("response_message"),
        responded_at=created_request.get("responded_at"),
        meeting_slots=created_request.get("meeting_slots"),
        selected_meeting=created_request.get("selected_meeting"),
        client_name=f"{client['first_name']} {client['last_name']}",
        client_email=client["email"],
        lawyer_name=f"{lawyer['first_name']} {lawyer['last_name']}",
        lawyer_email=lawyer["email"]
    )
    
    return response_data

@router.get("/", response_model=List[LawyerRequestResponse])
async def get_user_requests(current_user: UserInDB = Depends(get_current_user)):
    """Get requests for current user (different view for clients vs lawyers)"""
    db = get_database()
    
    if current_user.user_type == "client":
        # Get requests sent by this client
        requests = await db.lawyer_requests.find({
            "client_id": ObjectId(current_user.id)
        }).sort("created_at", -1).to_list(length=100)
        
        # Get lawyer info for each request
        response_list = []
        for req in requests:
            lawyer = await db.users.find_one({"_id": req["lawyer_id"]})
            client = await db.users.find_one({"_id": req["client_id"]})
            
            response_data = LawyerRequestResponse(
                id=str(req["_id"]),
                title=req["title"],
                description=req["description"],
                category=req["category"],
                urgency_level=req["urgency_level"],
                budget_min=req.get("budget_min"),
                budget_max=req.get("budget_max"),
                preferred_meeting_type=req.get("preferred_meeting_type"),
                location=req.get("location"),
                additional_notes=req.get("additional_notes"),
                status=req["status"],
                created_at=req["created_at"],
                updated_at=req["updated_at"],
                response_message=req.get("response_message"),
                responded_at=req.get("responded_at"),
                meeting_slots=req.get("meeting_slots"),
                selected_meeting=req.get("selected_meeting"),
                client_name=f"{client['first_name']} {client['last_name']}",
                client_email=client["email"],
                lawyer_name=f"{lawyer['first_name']} {lawyer['last_name']}" if lawyer else None,
                lawyer_email=lawyer["email"] if lawyer else None
            )
            response_list.append(response_data)
            
    elif current_user.user_type == "lawyer":
        # Get requests sent to this lawyer
        requests = await db.lawyer_requests.find({
            "lawyer_id": ObjectId(current_user.id)
        }).sort("created_at", -1).to_list(length=100)
        
        # Get client info for each request
        response_list = []
        for req in requests:
            client = await db.users.find_one({"_id": req["client_id"]})
            lawyer = await db.users.find_one({"_id": req["lawyer_id"]})
            
            response_data = LawyerRequestResponse(
                id=str(req["_id"]),
                title=req["title"],
                description=req["description"],
                category=req["category"],
                urgency_level=req["urgency_level"],
                budget_min=req.get("budget_min"),
                budget_max=req.get("budget_max"),
                preferred_meeting_type=req.get("preferred_meeting_type"),
                location=req.get("location"),
                additional_notes=req.get("additional_notes"),
                status=req["status"],
                created_at=req["created_at"],
                updated_at=req["updated_at"],
                response_message=req.get("response_message"),
                responded_at=req.get("responded_at"),
                meeting_slots=req.get("meeting_slots"),
                selected_meeting=req.get("selected_meeting"),
                client_name=f"{client['first_name']} {client['last_name']}" if client else "Unknown Client",
                client_email=client["email"] if client else "",
                lawyer_name=f"{lawyer['first_name']} {lawyer['last_name']}" if lawyer else None,
                lawyer_email=lawyer["email"] if lawyer else None
            )
            response_list.append(response_data)
    else:
        response_list = []
    
    return response_list

@router.get("/pending", response_model=List[LawyerRequestResponse])
async def get_pending_requests(current_user: UserInDB = Depends(get_current_user)):
    """Get pending requests for current lawyer"""
    if current_user.user_type != "lawyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lawyers can view pending requests"
        )
    
    db = get_database()
    
    # Get pending requests for this lawyer
    requests = await db.lawyer_requests.find({
        "lawyer_id": ObjectId(current_user.id),
        "status": RequestStatus.PENDING
    }).sort("created_at", -1).to_list(length=100)
    
    # Get client info for each request
    response_list = []
    for req in requests:
        client = await db.users.find_one({"_id": req["client_id"]})
        lawyer = await db.users.find_one({"_id": req["lawyer_id"]})
        
        response_data = LawyerRequestResponse(
            id=str(req["_id"]),
            title=req["title"],
            description=req["description"],
            category=req["category"],
            urgency_level=req["urgency_level"],
            budget_min=req.get("budget_min"),
            budget_max=req.get("budget_max"),
            preferred_meeting_type=req.get("preferred_meeting_type"),
            location=req.get("location"),
            additional_notes=req.get("additional_notes"),
            status=req["status"],
            created_at=req["created_at"],
            updated_at=req["updated_at"],
            response_message=req.get("response_message"),
            responded_at=req.get("responded_at"),
            meeting_slots=req.get("meeting_slots"),
            selected_meeting=req.get("selected_meeting"),
            client_name=f"{client['first_name']} {client['last_name']}" if client else "Unknown Client",
            client_email=client["email"] if client else "",
            lawyer_name=f"{lawyer['first_name']} {lawyer['last_name']}" if lawyer else None,
            lawyer_email=lawyer["email"] if lawyer else None
        )
        response_list.append(response_data)
    
    return response_list

@router.post("/{request_id}/respond")
async def respond_to_request(
    request_id: str,
    action_data: RequestActionRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Accept or reject a lawyer request (lawyer only)"""
    if current_user.user_type != "lawyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lawyers can respond to requests"
        )
    
    if action_data.action not in ["accept", "reject"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be 'accept' or 'reject'"
        )
    
    db = get_database()
    
    # Find the request
    request_doc = await db.lawyer_requests.find_one({
        "_id": ObjectId(request_id),
        "lawyer_id": ObjectId(current_user.id)
    })
    
    if not request_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    if request_doc["status"] != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request has already been responded to"
        )
    
    # Update request status
    new_status = RequestStatus.ACCEPTED if action_data.action == "accept" else RequestStatus.REJECTED
    
    update_data = {
        "status": new_status,
        "response_message": action_data.response_message,
        "responded_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Add meeting slots if accepting and slots are provided
    if action_data.action == "accept" and action_data.meeting_slots:
        meeting_slots = []
        for slot in action_data.meeting_slots:
            meeting_slots.append({
                "date": slot.date,
                "time": slot.time,
                "duration": slot.duration,
                "meeting_type": slot.meeting_type,
                "available": True
            })
        update_data["meeting_slots"] = meeting_slots
    
    await db.lawyer_requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": update_data}
    )
    
    # If accepted, create a case
    if action_data.action == "accept":
        case_data = {
            "title": request_doc["title"],
            "description": request_doc["description"],
            "category": request_doc["category"],
            "urgency_level": request_doc["urgency_level"],
            "budget_min": request_doc.get("budget_min"),
            "budget_max": request_doc.get("budget_max"),
            "client_id": request_doc["client_id"],
            "lawyer_id": request_doc["lawyer_id"],
            "status": "open",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "request_id": ObjectId(request_id)  # Link back to original request
        }
        
        await db.cases.insert_one(case_data)
    
    return {
        "message": f"Request {action_data.action}ed successfully",
        "status": new_status,
        "case_created": action_data.action == "accept"
    }

@router.get("/{request_id}", response_model=LawyerRequestResponse)
async def get_request_details(
    request_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get details of a specific request"""
    db = get_database()
    
    # Find the request
    request_doc = await db.lawyer_requests.find_one({"_id": ObjectId(request_id)})
    
    if not request_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check if user has permission to view this request
    if (current_user.user_type == "client" and str(request_doc["client_id"]) != current_user.id) or \
       (current_user.user_type == "lawyer" and str(request_doc["lawyer_id"]) != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this request"
        )
    
    # Get client and lawyer info
    client = await db.users.find_one({"_id": request_doc["client_id"]})
    lawyer = await db.users.find_one({"_id": request_doc["lawyer_id"]})
    
    response_data = LawyerRequestResponse(
        id=str(request_doc["_id"]),
        title=request_doc["title"],
        description=request_doc["description"],
        category=request_doc["category"],
        urgency_level=request_doc["urgency_level"],
        budget_min=request_doc.get("budget_min"),
        budget_max=request_doc.get("budget_max"),
        preferred_meeting_type=request_doc.get("preferred_meeting_type"),
        location=request_doc.get("location"),
        additional_notes=request_doc.get("additional_notes"),
        status=request_doc["status"],
        created_at=request_doc["created_at"],
        updated_at=request_doc["updated_at"],
        response_message=request_doc.get("response_message"),
        responded_at=request_doc.get("responded_at"),
        meeting_slots=request_doc.get("meeting_slots"),
        selected_meeting=request_doc.get("selected_meeting"),
        client_name=f"{client['first_name']} {client['last_name']}" if client else "Unknown Client",
        client_email=client["email"] if client else "",
        lawyer_name=f"{lawyer['first_name']} {lawyer['last_name']}" if lawyer else None,
        lawyer_email=lawyer["email"] if lawyer else None
    )
    
    return response_data

@router.post("/{request_id}/select-meeting")
async def select_meeting_slot(
    request_id: str,
    meeting_data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """Select a meeting slot for an accepted request (client only)"""
    if current_user.user_type != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can select meeting slots"
        )
    
    db = get_database()
    
    # Find the request
    request_doc = await db.lawyer_requests.find_one({
        "_id": ObjectId(request_id),
        "client_id": ObjectId(current_user.id)
    })
    
    if not request_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    if request_doc["status"] != RequestStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only select meeting slots for accepted requests"
        )
    
    # Update the selected meeting slot
    selected_meeting = {
        "date": meeting_data.get("date"),
        "time": meeting_data.get("time"),
        "duration": meeting_data.get("duration", 60),
        "meeting_type": meeting_data.get("meeting_type", "online"),
        "selected_at": datetime.utcnow()
    }
    
    await db.lawyer_requests.update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {
                "selected_meeting": selected_meeting,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "message": "Meeting slot selected successfully",
        "selected_meeting": selected_meeting
    }