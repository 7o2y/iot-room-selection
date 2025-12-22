from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import db
from app.models.ranking import (
    RankingRequest,
    RankedRoom,
    RankingResponse,
)
from app.models.calendar import EventStatus

logger = logging.getLogger(__name__)


class RankingService:
    """
    Service for room ranking using AHP (Analytic Hierarchy Process).

    This service:
    1. Fetches all relevant room data (sensors, facilities, calendar)
    2. Applies user preferences and filters
    3. Calculates AHP scores using Fede's algorithm
    4. Returns ranked rooms sorted by score
    """

    async def rank_rooms(self, request: RankingRequest) -> RankingResponse:
        """
        Rank rooms based on user preferences.

        Args:
            request: RankingRequest with criteria weights and preferences

        Returns:
            RankingResponse with ranked rooms
        """
        # Step 1: Get all rooms
        rooms = await self._fetch_all_rooms()

        # Step 2: Filter rooms by facility requirements
        if request.facility_requirements:
            rooms = self._filter_by_facilities(rooms, request.facility_requirements)

        if not rooms:
            return RankingResponse(
                ranked_rooms=[],
                total_rooms_evaluated=0,
                timestamp=datetime.utcnow(),
                request_summary=self._build_request_summary(request)
            )

        # Step 3: Enrich rooms with sensor data
        rooms_with_data = await self._enrich_with_sensor_data(rooms)

        # Step 4: Check calendar availability if requested
        if request.requested_time:
            rooms_with_data = await self._enrich_with_availability(
                rooms_with_data,
                request.requested_time,
                request.duration_minutes
            )

        # Step 5: Calculate AHP scores
        ranked_rooms = await self._calculate_ahp_scores(
            rooms_with_data,
            request
        )

        # Step 6: Sort by score (descending) and assign ranks
        ranked_rooms.sort(key=lambda x: x.overall_score, reverse=True)
        for idx, room in enumerate(ranked_rooms, start=1):
            room.rank = idx

        return RankingResponse(
            ranked_rooms=ranked_rooms,
            total_rooms_evaluated=len(ranked_rooms),
            timestamp=datetime.utcnow(),
            request_summary=self._build_request_summary(request)
        )

    async def _fetch_all_rooms(self) -> list[dict]:
        """Fetch all rooms from database."""
        collection = db.get_collection("rooms")
        cursor = collection.find({})
        return await cursor.to_list(length=100)

    def _filter_by_facilities(
        self,
        rooms: list[dict],
        requirements
    ) -> list[dict]:
        """
        Filter rooms based on facility requirements.

        Removes rooms that don't meet the minimum requirements.
        """
        filtered = []

        for room in rooms:
            facilities = room["facilities"]

            # Check each requirement
            if requirements.videoprojector is not None:
                if facilities.get("videoprojector", False) != requirements.videoprojector:
                    continue

            if requirements.min_seating is not None:
                if facilities.get("seating_capacity", 0) < requirements.min_seating:
                    continue

            if requirements.computers is not None:
                has_computers = facilities.get("computers", 0) > 0
                if has_computers != requirements.computers:
                    continue

            if requirements.whiteboard is not None:
                if facilities.get("whiteboard", False) != requirements.whiteboard:
                    continue

            filtered.append(room)

        return filtered

    async def _enrich_with_sensor_data(self, rooms: list[dict]) -> list[dict]:
        """
        Enrich rooms with latest sensor readings.

        Gets the average of the last 10 readings for each sensor type.
        """
        sensor_collection = db.get_collection("sensor_readings")

        for room in rooms:
            room_name = room["name"]

            # Get recent sensor data (last 10 readings per sensor type)
            pipeline = [
                {"$match": {"room_name": room_name}},
                {"$sort": {"timestamp": -1}},
                {
                    "$group": {
                        "_id": "$sensor_type",
                        "recent_values": {"$push": "$value"},
                        "latest_timestamp": {"$first": "$timestamp"}
                    }
                },
                {
                    "$project": {
                        "sensor_type": "$_id",
                        "average": {"$avg": {"$slice": ["$recent_values", 10]}},
                        "latest_timestamp": 1
                    }
                }
            ]

            results = await sensor_collection.aggregate(pipeline).to_list(length=10)

            # Convert to dict
            sensor_data = {}
            for doc in results:
                sensor_type = doc["sensor_type"]
                sensor_data[sensor_type] = {
                    "value": doc["average"],
                    "timestamp": doc["latest_timestamp"]
                }

            room["sensor_data"] = sensor_data

        return rooms

    async def _enrich_with_availability(
        self,
        rooms: list[dict],
        requested_time: datetime,
        duration_minutes: Optional[int]
    ) -> list[dict]:
        """
        Check calendar availability for each room.

        Marks rooms as available/unavailable.
        """
        calendar_collection = db.get_collection("calendar_events")

        # Calculate time range
        end_time = requested_time
        if duration_minutes:
            end_time = requested_time + timedelta(minutes=duration_minutes)

        for room in rooms:
            room_name = room["name"]

            # Check for conflicting events
            conflict = await calendar_collection.find_one({
                "room_name": room_name,
                "status": EventStatus.CONFIRMED.value,
                "$or": [
                    {
                        "start_time": {"$gte": requested_time, "$lt": end_time}
                    },
                    {
                        "end_time": {"$gt": requested_time, "$lte": end_time}
                    },
                    {
                        "start_time": {"$lte": requested_time},
                        "end_time": {"$gte": end_time}
                    }
                ]
            })

            room["is_available"] = conflict is None

        return rooms

    async def _calculate_ahp_scores(
        self,
        rooms: list[dict],
        request: RankingRequest
    ) -> list[RankedRoom]:
        """
        Calculate AHP scores for each room.

        TODO: Integrate with Fede's AHP algorithm implementation.

        For now, this is a placeholder with a simple scoring system.
        """
        ranked_rooms = []

        for room in rooms:
            # Extract sensor data
            sensor_data = room.get("sensor_data", {})

            # Calculate individual criterion scores (0-1 scale)
            criteria_scores = {}

            # Temperature score (if preferences provided)
            if request.environmental_preferences and request.environmental_preferences.temperature_min:
                temp_data = sensor_data.get("temperature", {})
                temp_value = temp_data.get("value", 20)  # Default to 20°C if missing
                criteria_scores["temperature"] = self._score_temperature(
                    temp_value,
                    request.environmental_preferences.temperature_min,
                    request.environmental_preferences.temperature_max or 25.0
                )
            else:
                criteria_scores["temperature"] = 0.5  # Neutral score

            # CO2 score
            if request.environmental_preferences and request.environmental_preferences.co2_max:
                co2_data = sensor_data.get("co2", {})
                co2_value = co2_data.get("value", 600)
                criteria_scores["co2"] = self._score_co2(
                    co2_value,
                    request.environmental_preferences.co2_max
                )
            else:
                criteria_scores["co2"] = 0.5

            # Humidity score
            if request.environmental_preferences and request.environmental_preferences.humidity_min:
                humidity_data = sensor_data.get("humidity", {})
                humidity_value = humidity_data.get("value", 50)
                criteria_scores["humidity"] = self._score_humidity(
                    humidity_value,
                    request.environmental_preferences.humidity_min,
                    request.environmental_preferences.humidity_max or 70.0
                )
            else:
                criteria_scores["humidity"] = 0.5

            # Sound score
            if request.environmental_preferences and request.environmental_preferences.sound_max:
                sound_data = sensor_data.get("sound", {})
                sound_value = sound_data.get("value", 45)
                criteria_scores["sound"] = self._score_sound(
                    sound_value,
                    request.environmental_preferences.sound_max
                )
            else:
                criteria_scores["sound"] = 0.5

            # Facilities score (based on facility requirements match)
            criteria_scores["facilities"] = self._score_facilities(
                room["facilities"],
                request.facility_requirements
            )

            # Availability score
            criteria_scores["availability"] = 1.0 if room.get("is_available", True) else 0.0

            # Calculate weighted overall score
            # Normalize weights to sum to 1
            weights = request.criteria_weights
            total_weight = (
                weights.temperature +
                weights.co2 +
                weights.humidity +
                weights.sound +
                weights.facilities +
                weights.availability
            )

            overall_score = (
                (weights.temperature / total_weight) * criteria_scores["temperature"] +
                (weights.co2 / total_weight) * criteria_scores["co2"] +
                (weights.humidity / total_weight) * criteria_scores["humidity"] +
                (weights.sound / total_weight) * criteria_scores["sound"] +
                (weights.facilities / total_weight) * criteria_scores["facilities"] +
                (weights.availability / total_weight) * criteria_scores["availability"]
            )

            # Build current conditions dict
            current_conditions = {
                sensor_type: data.get("value")
                for sensor_type, data in sensor_data.items()
            }

            ranked_rooms.append(RankedRoom(
                room_name=room["name"],
                rank=1,  # Will be updated after sorting
                overall_score=round(overall_score, 3),
                criteria_scores={
                    k: round(v, 3) for k, v in criteria_scores.items()
                },
                current_conditions=current_conditions if current_conditions else None,
                facilities=room["facilities"],
                is_available=room.get("is_available", True)
            ))

        return ranked_rooms

    def _score_temperature(self, value: float, min_pref: float, max_pref: float) -> float:
        """Score temperature (1.0 = perfect, 0.0 = very bad)."""
        if min_pref <= value <= max_pref:
            return 1.0  # Perfect range
        elif value < min_pref:
            # Too cold - penalize linearly
            deviation = min_pref - value
            return max(0.0, 1.0 - (deviation / 5.0))
        else:
            # Too hot - penalize linearly
            deviation = value - max_pref
            return max(0.0, 1.0 - (deviation / 5.0))

    def _score_co2(self, value: float, max_pref: float) -> float:
        """Score CO2 level (lower is better)."""
        if value <= max_pref:
            return 1.0
        else:
            # Penalize linearly above threshold
            deviation = value - max_pref
            return max(0.0, 1.0 - (deviation / max_pref))

    def _score_humidity(self, value: float, min_pref: float, max_pref: float) -> float:
        """Score humidity (within range is best)."""
        if min_pref <= value <= max_pref:
            return 1.0
        elif value < min_pref:
            deviation = min_pref - value
            return max(0.0, 1.0 - (deviation / 20.0))
        else:
            deviation = value - max_pref
            return max(0.0, 1.0 - (deviation / 20.0))

    def _score_sound(self, value: float, max_pref: float) -> float:
        """Score sound level (lower is better)."""
        if value <= max_pref:
            return 1.0
        else:
            deviation = value - max_pref
            return max(0.0, 1.0 - (deviation / 30.0))

    def _score_facilities(self, facilities: dict, requirements) -> float:
        """
        Score facilities (1.0 if all requirements met, scaled down otherwise).

        Since requirements were already used to filter, this checks
        for "nice to have" facilities.
        """
        score = 0.5  # Base score

        # Bonus for projector
        if facilities.get("videoprojector", False):
            score += 0.1

        # Bonus for computers
        if facilities.get("computers", 0) > 0:
            score += 0.1

        # Bonus for whiteboard
        if facilities.get("whiteboard", False):
            score += 0.1

        # Bonus for high seating capacity
        capacity = facilities.get("seating_capacity", 0)
        if capacity >= 50:
            score += 0.2
        elif capacity >= 30:
            score += 0.1

        return min(1.0, score)

    def _build_request_summary(self, request: RankingRequest) -> dict:
        """Build a summary of the user's request for the response."""
        weights = request.criteria_weights

        # Find top 3 criteria by weight
        criteria_list = [
            ("temperature", weights.temperature),
            ("co2", weights.co2),
            ("humidity", weights.humidity),
            ("sound", weights.sound),
            ("facilities", weights.facilities),
            ("availability", weights.availability),
        ]
        criteria_list.sort(key=lambda x: x[1], reverse=True)
        top_criteria = [c[0] for c in criteria_list[:3]]

        return {
            "top_criteria": top_criteria,
            "facility_requirements": request.facility_requirements is not None,
            "environmental_preferences": request.environmental_preferences is not None,
            "time_specific": request.requested_time is not None
        }


# Global service instance
ranking_service = RankingService()
