"""
Score Aggregation for AHP Algorithm.

This module implements the final aggregation step of AHP, combining
sub-criteria scores with their calculated weights to produce final
room rankings.

Aggregation methods:
- Weighted Sum Model (WSM): Simple weighted average
- Weighted Product Model (WPM): Geometric weighted average
- Combined (Default): Hybrid approach for robustness
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class AggregationMethod(Enum):
    """Supported aggregation methods."""
    WEIGHTED_SUM = "weighted_sum"
    WEIGHTED_PRODUCT = "weighted_product"
    COMBINED = "combined"


@dataclass
class CriterionScore:
    """Score for a single criterion."""
    criterion_id: str
    criterion_name: str
    raw_value: float  # Original sensor value
    normalized_score: float  # 0-1 mapped score
    weight: float  # Final weight from AHP hierarchy


@dataclass  
class RoomScore:
    """Complete scoring result for a room."""
    room_id: str
    room_name: str
    final_score: float
    rank: int = 0
    criterion_scores: List[CriterionScore] = field(default_factory=list)
    
    # Breakdown by main criteria (for UI display)
    comfort_score: float = 0.0
    health_score: float = 0.0
    usability_score: float = 0.0


def aggregate_weighted_sum(
    scores: Dict[str, float],
    weights: Dict[str, float]
) -> float:
    """
    Calculate weighted sum aggregation.
    
    Formula: S = Σ(w_i * s_i)
    
    Args:
        scores: Dict mapping criterion ID to normalized score (0-1)
        weights: Dict mapping criterion ID to weight (should sum to 1)
    
    Returns:
        Aggregated score between 0 and 1
    """
    if not scores or not weights:
        return 0.0
    
    total = 0.0
    weight_sum = 0.0
    
    for criterion_id, score in scores.items():
        weight = weights.get(criterion_id, 0.0)
        total += weight * score
        weight_sum += weight
    
    # Normalize if weights don't sum to 1
    if weight_sum > 0 and not np.isclose(weight_sum, 1.0):
        total /= weight_sum
    
    return total


def aggregate_weighted_product(
    scores: Dict[str, float],
    weights: Dict[str, float],
    epsilon: float = 0.001
) -> float:
    """
    Calculate weighted product aggregation.
    
    Formula: S = Π(s_i ^ w_i)
    
    This method is scale-independent and handles varying score ranges better.
    
    Args:
        scores: Dict mapping criterion ID to normalized score (0-1)
        weights: Dict mapping criterion ID to weight
        epsilon: Small value to replace zeros (avoids 0^w = 0)
    
    Returns:
        Aggregated score between 0 and 1
    """
    if not scores or not weights:
        return 0.0
    
    product = 1.0
    weight_sum = 0.0
    
    for criterion_id, score in scores.items():
        weight = weights.get(criterion_id, 0.0)
        if weight == 0:
            continue
            
        # Replace zero scores with epsilon to avoid total zeroing
        safe_score = max(epsilon, score)
        product *= safe_score ** weight
        weight_sum += weight
    
    # Normalize the product
    if weight_sum > 0 and not np.isclose(weight_sum, 1.0):
        product = product ** (1.0 / weight_sum)
    
    return product


def aggregate_combined(
    scores: Dict[str, float],
    weights: Dict[str, float],
    wsm_weight: float = 0.7
) -> float:
    """
    Combined aggregation using both WSM and WPM.
    
    This provides a balanced result that captures both:
    - WSM: Good for compensatory scenarios (high values can compensate low ones)
    - WPM: Good for non-compensatory (zeros heavily penalize)
    
    Args:
        scores: Dict mapping criterion ID to normalized score
        weights: Dict mapping criterion ID to weight
        wsm_weight: Weight given to WSM (1 - wsm_weight for WPM)
    
    Returns:
        Combined aggregated score
    """
    wsm_score = aggregate_weighted_sum(scores, weights)
    wpm_score = aggregate_weighted_product(scores, weights)
    
    return wsm_weight * wsm_score + (1 - wsm_weight) * wpm_score


def aggregate_with_hierarchy(
    leaf_scores: Dict[str, float],
    hierarchy_weights: Dict[str, Dict[str, float]],
    method: AggregationMethod = AggregationMethod.WEIGHTED_SUM
) -> Tuple[float, Dict[str, float]]:
    """
    Aggregate scores respecting the AHP hierarchy structure.
    
    This performs bottom-up aggregation:
    1. Aggregate sub-criteria into main criteria scores
    2. Aggregate main criteria into final score
    
    Args:
        leaf_scores: Dict mapping leaf criterion ID to score
        hierarchy_weights: Nested dict structure:
            {
                "main": {"Comfort": 0.4, "Health": 0.35, "Usability": 0.25},
                "Comfort": {"Temperature": 0.4, "Lighting": 0.25, ...},
                "Health": {"CO2": 0.5, "AirQuality": 0.3, "VOC": 0.2},
                "Usability": {"SeatingCapacity": 0.5, ...}
            }
        method: Aggregation method to use
    
    Returns:
        Tuple of (final_score, main_criteria_scores)
    """
    aggregator = _get_aggregator(method)
    
    main_criteria_scores = {}
    
    # Aggregate each main criterion from its sub-criteria
    for main_criterion in ["Comfort", "Health", "Usability"]:
        if main_criterion not in hierarchy_weights:
            continue
        
        sub_weights = hierarchy_weights[main_criterion]
        sub_scores = {k: leaf_scores.get(k, 0.0) for k in sub_weights.keys()}
        
        main_criteria_scores[main_criterion] = aggregator(sub_scores, sub_weights)
    
    # Aggregate main criteria into final score
    main_weights = hierarchy_weights.get("main", {})
    final_score = aggregator(main_criteria_scores, main_weights)
    
    return final_score, main_criteria_scores


def rank_rooms(room_scores: List[RoomScore]) -> List[RoomScore]:
    """
    Sort rooms by score and assign ranks.
    
    Args:
        room_scores: List of RoomScore objects
    
    Returns:
        Sorted list with rank field populated
    """
    # Sort descending by score
    sorted_rooms = sorted(room_scores, key=lambda r: r.final_score, reverse=True)
    
    # Assign ranks (handle ties)
    current_rank = 1
    for i, room in enumerate(sorted_rooms):
        if i > 0 and not np.isclose(room.final_score, sorted_rooms[i-1].final_score):
            current_rank = i + 1
        room.rank = current_rank
    
    return sorted_rooms


def format_ranking(room_scores: List[RoomScore], detailed: bool = False) -> str:
    """
    Format room rankings as a readable string.
    
    Args:
        room_scores: Sorted list of RoomScore objects
        detailed: If True, include criterion breakdown
    
    Returns:
        Formatted ranking string
    """
    lines = ["=" * 50, "ROOM RANKING RESULTS", "=" * 50, ""]
    
    for room in room_scores:
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(room.rank, "  ")
        lines.append(f"{medal} Rank {room.rank}: {room.room_name}")
        lines.append(f"   Final Score: {room.final_score:.4f} ({room.final_score*100:.1f}%)")
        
        if detailed or room.rank <= 3:
            lines.append(f"   ├─ Comfort:   {room.comfort_score:.3f}")
            lines.append(f"   ├─ Health:    {room.health_score:.3f}")
            lines.append(f"   └─ Usability: {room.usability_score:.3f}")
        
        lines.append("")
    
    return "\n".join(lines)


def _get_aggregator(method: AggregationMethod):
    """Get the aggregation function for the specified method."""
    if method == AggregationMethod.WEIGHTED_SUM:
        return aggregate_weighted_sum
    elif method == AggregationMethod.WEIGHTED_PRODUCT:
        return aggregate_weighted_product
    elif method == AggregationMethod.COMBINED:
        return aggregate_combined
    else:
        raise ValueError(f"Unknown aggregation method: {method}")
