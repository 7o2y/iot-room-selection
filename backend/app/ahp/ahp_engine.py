"""
AHP Engine - Main Orchestrator for Room Selection.

This module provides the main entry point for the AHP algorithm,
coordinating all components to produce room rankings.

Usage:
    from backend.app.ahp.ahp_engine import AHPEngine
    
    engine = AHPEngine()
    engine.set_user_preferences({...})
    engine.load_room_data(rooms)
    ranking = engine.evaluate_rooms()
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

from .pairwise_matrix import (
    PairwiseMatrix,
    create_default_criteria_matrix,
    create_comfort_subcriteria_matrix,
    create_health_subcriteria_matrix,
    create_usability_subcriteria_matrix,
)
from .eigenvector import (
    calculate_priority_weights,
    calculate_consistency_ratio,
    validate_matrix_consistency,
)
from .score_mapping import (
    map_temperature, map_co2, map_humidity, map_light,
    map_noise, map_voc, map_air_quality,
    map_seating_capacity, map_equipment, map_av_facilities,
)
from .aggregation import (
    aggregate_with_hierarchy,
    rank_rooms,
    RoomScore,
    CriterionScore,
    AggregationMethod,
)


@dataclass
class RoomData:
    """Input data for a single room."""
    room_id: str
    room_name: str
    
    # Average sensor values (from time window)
    temperature: Optional[float] = None
    co2: Optional[float] = None
    humidity: Optional[float] = None
    light: Optional[float] = None
    noise: Optional[float] = None
    voc: Optional[float] = None
    air_quality: Optional[float] = None
    
    # Facilities
    seating_capacity: int = 0
    has_projector: bool = False
    computers: int = 0
    has_robots: bool = False


@dataclass
class UserRequirements:
    """User's requirements for room selection."""
    required_seats: int = 0
    need_projector: bool = False
    need_computers: int = 0
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None


@dataclass
class AHPResult:
    """Complete result of AHP evaluation."""
    rankings: List[RoomScore]
    weights: Dict[str, float]
    main_criteria_weights: Dict[str, float]
    consistency_ratios: Dict[str, float]
    is_consistent: bool
    evaluation_time: datetime = field(default_factory=datetime.now)


class AHPEngine:
    """
    Main AHP algorithm orchestrator.
    
    Coordinates the complete AHP process:
    1. Set up criteria hierarchy with weights
    2. Accept user preference adjustments
    3. Map room sensor data to scores
    4. Aggregate scores using hierarchy
    5. Produce final room rankings
    """
    
    # Criteria structure
    MAIN_CRITERIA = ["Comfort", "Health", "Usability"]
    
    SUB_CRITERIA = {
        "Comfort": ["Temperature", "Lighting", "Noise", "Humidity"],
        "Health": ["CO2", "AirQuality", "VOC"],
        "Usability": ["SeatingCapacity", "Equipment", "AVFacilities"],
    }
    
    def __init__(self):
        """Initialize the AHP engine with default weights."""
        self._main_matrix: Optional[PairwiseMatrix] = None
        self._sub_matrices: Dict[str, PairwiseMatrix] = {}
        
        self._main_weights: Dict[str, float] = {}
        self._sub_weights: Dict[str, Dict[str, float]] = {}
        self._global_weights: Dict[str, float] = {}
        
        self._rooms: List[RoomData] = []
        self._requirements: UserRequirements = UserRequirements()
        
        self._consistency_ratios: Dict[str, float] = {}
        self._is_consistent: bool = True
        
        # Initialize with defaults
        self._initialize_default_weights()
    
    def _initialize_default_weights(self):
        """Set up default pairwise matrices and calculate weights."""
        # Main criteria
        self._main_matrix = create_default_criteria_matrix()
        self._main_weights = self._calculate_weights(
            self._main_matrix, "main"
        )
        
        # Sub-criteria
        self._sub_matrices["Comfort"] = create_comfort_subcriteria_matrix()
        self._sub_matrices["Health"] = create_health_subcriteria_matrix()
        self._sub_matrices["Usability"] = create_usability_subcriteria_matrix()
        
        for main_crit in self.MAIN_CRITERIA:
            if main_crit in self._sub_matrices:
                self._sub_weights[main_crit] = self._calculate_weights(
                    self._sub_matrices[main_crit], main_crit
                )
        
        # Calculate global weights
        self._calculate_global_weights()
    
    def _calculate_weights(
        self, 
        matrix: PairwiseMatrix, 
        name: str
    ) -> Dict[str, float]:
        """Calculate and validate weights from a pairwise matrix."""
        np_matrix = matrix.get_matrix()
        weights = calculate_priority_weights(np_matrix)
        
        # Validate consistency
        cr, is_consistent = calculate_consistency_ratio(np_matrix)
        self._consistency_ratios[name] = cr
        
        if not is_consistent:
            self._is_consistent = False
        
        return dict(zip(matrix.criteria, weights))
    
    def _calculate_global_weights(self):
        """Calculate global weights (main weight × sub weight)."""
        self._global_weights = {}
        
        for main_crit, main_weight in self._main_weights.items():
            if main_crit in self._sub_weights:
                for sub_crit, sub_weight in self._sub_weights[main_crit].items():
                    self._global_weights[sub_crit] = main_weight * sub_weight
    
    def set_user_preferences(
        self,
        main_comparisons: Optional[Dict[tuple, float]] = None,
        sub_comparisons: Optional[Dict[str, Dict[tuple, float]]] = None
    ):
        """
        Update weights based on user preferences.
        
        Args:
            main_comparisons: Dict of {(crit_a, crit_b): value} for main criteria
                Example: {("Comfort", "Health"): 3} means Comfort is 3x more important
            sub_comparisons: Nested dict by main criterion
                Example: {"Comfort": {("Temperature", "Lighting"): 2}}
        """
        if main_comparisons:
            for (crit_a, crit_b), value in main_comparisons.items():
                self._main_matrix.set_comparison(crit_a, crit_b, value)
            self._main_weights = self._calculate_weights(
                self._main_matrix, "main"
            )
        
        if sub_comparisons:
            for main_crit, comparisons in sub_comparisons.items():
                if main_crit not in self._sub_matrices:
                    continue
                for (crit_a, crit_b), value in comparisons.items():
                    self._sub_matrices[main_crit].set_comparison(crit_a, crit_b, value)
                self._sub_weights[main_crit] = self._calculate_weights(
                    self._sub_matrices[main_crit], main_crit
                )
        
        self._calculate_global_weights()
    
    def set_requirements(self, requirements: UserRequirements):
        """Set user's room requirements."""
        self._requirements = requirements
    
    def load_room_data(self, rooms: List[RoomData]):
        """Load room data for evaluation."""
        self._rooms = rooms
    
    def load_room_data_from_dict(self, rooms_data: List[Dict[str, Any]]):
        """Load room data from dictionary format (e.g., from JSON)."""
        self._rooms = []
        for data in rooms_data:
            room = RoomData(
                room_id=data.get("id", data.get("name", "")),
                room_name=data.get("name", ""),
                temperature=data.get("temperature"),
                co2=data.get("co2"),
                humidity=data.get("humidity"),
                light=data.get("light"),
                noise=data.get("noise"),
                voc=data.get("voc"),
                air_quality=data.get("air_quality"),
                seating_capacity=data.get("seating_capacity", 0),
                has_projector=data.get("has_projector", False),
                computers=data.get("computers", 0),
                has_robots=data.get("has_robots", False),
            )
            self._rooms.append(room)
    
    def _score_room(self, room: RoomData) -> Dict[str, float]:
        """Calculate all sub-criterion scores for a room."""
        scores = {}
        
        # Comfort sub-criteria
        if room.temperature is not None:
            scores["Temperature"] = map_temperature(room.temperature)
        else:
            scores["Temperature"] = 0.5  # Neutral if no data
        
        if room.light is not None:
            scores["Lighting"] = map_light(room.light)
        else:
            scores["Lighting"] = 0.5
        
        if room.noise is not None:
            scores["Noise"] = map_noise(room.noise)
        else:
            scores["Noise"] = 0.5
        
        if room.humidity is not None:
            scores["Humidity"] = map_humidity(room.humidity)
        else:
            scores["Humidity"] = 0.5
        
        # Health sub-criteria
        if room.co2 is not None:
            scores["CO2"] = map_co2(room.co2)
        else:
            scores["CO2"] = 0.5
        
        if room.air_quality is not None:
            scores["AirQuality"] = map_air_quality(room.air_quality)
        else:
            scores["AirQuality"] = 0.5
        
        if room.voc is not None:
            scores["VOC"] = map_voc(room.voc)
        else:
            scores["VOC"] = 0.5
        
        # Usability sub-criteria
        scores["SeatingCapacity"] = map_seating_capacity(
            room.seating_capacity, 
            self._requirements.required_seats
        )
        
        scores["Equipment"] = map_equipment(
            room.computers > 0,
            room.computers,
            self._requirements.need_computers
        )
        
        scores["AVFacilities"] = map_av_facilities(
            room.has_projector,
            self._requirements.need_projector
        )
        
        return scores
    
    def evaluate_rooms(
        self,
        method: AggregationMethod = AggregationMethod.WEIGHTED_SUM
    ) -> AHPResult:
        """
        Evaluate all rooms and produce rankings.
        
        Args:
            method: Aggregation method to use
        
        Returns:
            AHPResult containing rankings and metadata
        """
        if not self._rooms:
            raise ValueError("No rooms loaded. Call load_room_data() first.")
        
        room_scores = []
        
        # Build hierarchy weights structure for aggregation
        hierarchy_weights = {
            "main": self._main_weights,
        }
        hierarchy_weights.update(self._sub_weights)
        
        for room in self._rooms:
            # Calculate sub-criterion scores
            leaf_scores = self._score_room(room)
            
            # Aggregate through hierarchy
            final_score, main_scores = aggregate_with_hierarchy(
                leaf_scores, hierarchy_weights, method
            )
            
            # Create result object
            room_score = RoomScore(
                room_id=room.room_id,
                room_name=room.room_name,
                final_score=final_score,
                comfort_score=main_scores.get("Comfort", 0),
                health_score=main_scores.get("Health", 0),
                usability_score=main_scores.get("Usability", 0),
            )
            
            # Add detailed criterion scores
            for crit_id, score in leaf_scores.items():
                room_score.criterion_scores.append(CriterionScore(
                    criterion_id=crit_id,
                    criterion_name=crit_id,
                    raw_value=getattr(room, crit_id.lower(), 0) or 0,
                    normalized_score=score,
                    weight=self._global_weights.get(crit_id, 0),
                ))
            
            room_scores.append(room_score)
        
        # Rank rooms
        ranked_rooms = rank_rooms(room_scores)
        
        return AHPResult(
            rankings=ranked_rooms,
            weights=self._global_weights,
            main_criteria_weights=self._main_weights,
            consistency_ratios=self._consistency_ratios,
            is_consistent=self._is_consistent,
        )
    
    def get_weights_summary(self) -> str:
        """Get a formatted summary of all weights."""
        lines = ["=" * 40, "AHP WEIGHTS SUMMARY", "=" * 40, ""]
        
        lines.append("MAIN CRITERIA:")
        for crit, weight in self._main_weights.items():
            lines.append(f"  {crit}: {weight:.4f} ({weight*100:.1f}%)")
        
        lines.append("\nSUB-CRITERIA:")
        for main_crit, sub_weights in self._sub_weights.items():
            lines.append(f"\n  {main_crit}:")
            for sub_crit, weight in sub_weights.items():
                global_w = self._global_weights.get(sub_crit, 0)
                lines.append(f"    {sub_crit}: {weight:.4f} (global: {global_w:.4f})")
        
        lines.append("\nCONSISTENCY RATIOS:")
        for name, cr in self._consistency_ratios.items():
            status = "✓" if cr < 0.1 else "✗"
            lines.append(f"  {name}: {cr:.4f} {status}")
        
        return "\n".join(lines)
