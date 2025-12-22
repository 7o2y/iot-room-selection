from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import db
from app.models.calendar import (
    CalendarEventResponse,
    CalendarEvent,
    RoomAvailability,
    EventStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/events",
    response_model=CalendarEventResponse,
    summary="Get calendar events",
    description="""
    Retrieve calendar events (room bookings) within a time range.

    **Query Parameters:**
    - `room_name`: Filter by specific room (optional)
    - `start`: Start of time range (ISO 8601 format)
    - `end`: End of time range (ISO 8601 format)
    - `status`: Filter by event status (confirmed, tentative, cancelled)

    **Returns:**
    - List of calendar events
    - Total count of events
    """
)
async def get_events(
    room_name: Optional[str] = Query(
        None,
        description="Filter by room name (e.g., 'Room_1')"
    ),
    start: Optional[datetime] = Query(
        None,
        description="Start of time range (ISO 8601 format)"
    ),
    end: Optional[datetime] = Query(
        None,
        description="End of time range (ISO 8601 format)"
    ),
    status: Optional[EventStatus] = Query(
        None,
        description="Filter by event status"
    )
):
    """Get calendar events with optional filtering."""
    try:
        # Build query filter
        query_filter = {}

        if room_name:
            query_filter["room_name"] = room_name

        if status:
            query_filter["status"] = status.value

        # Time range filter - find events that overlap with the requested range
        if start or end:
            time_filter = {}
            if start:
                # Event ends after the requested start
                time_filter["end_time"] = {"$gte": start}
            if end:
                # Event starts before the requested end
                time_filter["start_time"] = {"$lte": end}
            query_filter.update(time_filter)

        # Query database
        collection = db.get_collection("calendar_events")
        cursor = collection.find(query_filter).sort("start_time", 1).limit(500)
        events_list = await cursor.to_list(length=500)

        # Convert to Pydantic models
        events = [
            CalendarEvent(
                room_name=doc["room_name"],
                event_id=doc.get("event_id"),
                title=doc["title"],
                start_time=doc["start_time"],
                end_time=doc["end_time"],
                status=EventStatus(doc.get("status", "confirmed")),
                organizer=doc.get("organizer"),
                description=doc.get("description"),
                created_at=doc.get("created_at"),
                synced_at=doc.get("synced_at")
            )
            for doc in events_list
        ]

        return CalendarEventResponse(
            events=events,
            total=len(events)
        )

    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/availability/{room_name}",
    response_model=RoomAvailability,
    summary="Check room availability",
    description="""
    Check if a specific room is available at a given time.

    **Parameters:**
    - `room_name`: Room identifier (e.g., 'Room_1')
    - `requested_time`: Time to check availability (ISO 8601 format)

    **Returns:**
    - Boolean indicating availability
    - Current event if room is occupied
    - When the room becomes available next
    """
)
async def check_availability(
    room_name: str,
    requested_time: datetime = Query(
        ...,
        description="Time to check availability (ISO 8601 format)"
    )
):
    """Check if a room is available at a specific time."""
    try:
        collection = db.get_collection("calendar_events")

        # Find event that overlaps with the requested time
        current_event_doc = await collection.find_one({
            "room_name": room_name,
            "status": EventStatus.CONFIRMED.value,
            "start_time": {"$lte": requested_time},
            "end_time": {"$gte": requested_time}
        })

        is_available = current_event_doc is None
        current_event = None
        next_available = None

        if current_event_doc:
            # Room is occupied
            current_event = CalendarEvent(
                room_name=current_event_doc["room_name"],
                event_id=current_event_doc.get("event_id"),
                title=current_event_doc["title"],
                start_time=current_event_doc["start_time"],
                end_time=current_event_doc["end_time"],
                status=EventStatus(current_event_doc.get("status", "confirmed")),
                organizer=current_event_doc.get("organizer")
            )
            next_available = current_event_doc["end_time"]

            # Check if there's another event right after
            next_event = await collection.find_one({
                "room_name": room_name,
                "status": EventStatus.CONFIRMED.value,
                "start_time": {"$lte": current_event_doc["end_time"]},
                "end_time": {"$gt": current_event_doc["end_time"]}
            })

            if next_event:
                next_available = next_event["end_time"]

        return RoomAvailability(
            room_name=room_name,
            requested_time=requested_time,
            is_available=is_available,
            current_event=current_event,
            next_available=next_available
        )

    except Exception as e:
        logger.error(f"Error checking availability for {room_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/availability/{room_name}/range",
    summary="Check availability for time range",
    description="""
    Check if a room is available for a continuous time range.

    **Parameters:**
    - `room_name`: Room identifier
    - `start_time`: Start of desired time slot
    - `end_time`: End of desired time slot (or use duration_minutes)
    - `duration_minutes`: Alternative to end_time - specify duration

    **Returns:**
    - Boolean indicating if room is free for the entire duration
    - List of conflicting events (if any)
    """
)
async def check_availability_range(
    room_name: str,
    start_time: datetime = Query(
        ...,
        description="Start of desired time slot (ISO 8601)"
    ),
    end_time: Optional[datetime] = Query(
        None,
        description="End of desired time slot (ISO 8601)"
    ),
    duration_minutes: Optional[int] = Query(
        None,
        ge=15,
        le=480,
        description="Duration in minutes (alternative to end_time)"
    )
):
    """Check if a room is available for a continuous time range."""
    try:
        # Calculate end_time if duration is provided
        if not end_time and duration_minutes:
            end_time = start_time + timedelta(minutes=duration_minutes)
        elif not end_time:
            raise HTTPException(
                status_code=400,
                detail="Either end_time or duration_minutes must be provided"
            )

        # Find conflicting events
        collection = db.get_collection("calendar_events")
        cursor = collection.find({
            "room_name": room_name,
            "status": EventStatus.CONFIRMED.value,
            "$or": [
                # Event starts during our requested time
                {
                    "start_time": {"$gte": start_time, "$lt": end_time}
                },
                # Event ends during our requested time
                {
                    "end_time": {"$gt": start_time, "$lte": end_time}
                },
                # Event completely overlaps our requested time
                {
                    "start_time": {"$lte": start_time},
                    "end_time": {"$gte": end_time}
                }
            ]
        })

        conflicting_events = await cursor.to_list(length=100)

        is_available = len(conflicting_events) == 0

        # Convert to CalendarEvent models
        conflicts = [
            {
                "title": event["title"],
                "start_time": event["start_time"].isoformat(),
                "end_time": event["end_time"].isoformat(),
                "organizer": event.get("organizer")
            }
            for event in conflicting_events
        ]

        return {
            "room_name": room_name,
            "requested_start": start_time.isoformat(),
            "requested_end": end_time.isoformat(),
            "is_available": is_available,
            "conflicting_events": conflicts,
            "conflict_count": len(conflicts)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking availability range for {room_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
