"""
Score Mapping Functions for AHP Algorithm.

This module provides functions to map raw sensor data values to normalized
scores (0-1), based on EU standards (EN 16798-1, EN 12464-1) and comfort
research.

Score interpretation:
    1.0 = Perfect/Optimal
    0.5 = Acceptable
    0.0 = Unacceptable

Each mapping function uses piecewise linear interpolation based on
established thresholds from European standards.
"""

from dataclasses import dataclass
from typing import Callable, Dict, Optional
import numpy as np


@dataclass
class MappingConfig:
    """Configuration for a single sensor mapping function."""
    name: str
    unit: str
    optimal_min: float
    optimal_max: float
    acceptable_min: float
    acceptable_max: float
    description: str


# ============================================================================
# MAPPING CONFIGURATIONS (Based on EN 16798-1 Category II)
# ============================================================================

TEMPERATURE_CONFIG = MappingConfig(
    name="Temperature",
    unit="°C",
    optimal_min=20.0,
    optimal_max=24.0,
    acceptable_min=18.0,
    acceptable_max=26.0,
    description="Based on EN 16798-1, Category II for office spaces"
)

CO2_CONFIG = MappingConfig(
    name="CO2",
    unit="ppm",
    optimal_min=0.0,
    optimal_max=600.0,
    acceptable_min=0.0,
    acceptable_max=1000.0,
    description="Based on EN 16798-1, Category II (800 ppm above outdoor ~400)"
)

HUMIDITY_CONFIG = MappingConfig(
    name="Humidity",
    unit="%RH",
    optimal_min=40.0,
    optimal_max=60.0,
    acceptable_min=30.0,
    acceptable_max=70.0,
    description="Based on EN 16798-1 and health research"
)

LIGHT_CONFIG = MappingConfig(
    name="Light Intensity",
    unit="lux",
    optimal_min=300.0,
    optimal_max=500.0,
    acceptable_min=200.0,
    acceptable_max=750.0,
    description="Based on EN 12464-1 for office/classroom lighting"
)

NOISE_CONFIG = MappingConfig(
    name="Noise",
    unit="dBA",
    optimal_min=0.0,
    optimal_max=35.0,
    acceptable_min=0.0,
    acceptable_max=45.0,
    description="Based on WHO guidelines and EN 16798-1"
)

VOC_CONFIG = MappingConfig(
    name="VOC",
    unit="ppb",
    optimal_min=0.0,
    optimal_max=200.0,
    acceptable_min=0.0,
    acceptable_max=400.0,
    description="Based on WELL Building Standard"
)

AIR_QUALITY_CONFIG = MappingConfig(
    name="Air Quality Index",
    unit="AQI",
    optimal_min=0.0,
    optimal_max=50.0,
    acceptable_min=0.0,
    acceptable_max=100.0,
    description="US EPA AQI scale adapted for indoor use"
)


# ============================================================================
# MAPPING FUNCTIONS
# ============================================================================

def map_temperature(value: float, config: MappingConfig = TEMPERATURE_CONFIG) -> float:
    """
    Map temperature to a comfort score.
    
    Score distribution:
        - 1.0: Within optimal range (20-24°C)
        - 0.5-1.0: Between acceptable and optimal bounds
        - 0.0-0.5: Outside acceptable range (rapidly decreasing)
    
    Args:
        value: Temperature in °C
        config: Mapping configuration
    
    Returns:
        Normalized score between 0 and 1
    """
    return _map_range_centered(
        value,
        config.optimal_min, config.optimal_max,
        config.acceptable_min, config.acceptable_max
    )


def map_co2(value: float, config: MappingConfig = CO2_CONFIG) -> float:
    """
    Map CO2 concentration to a health score.
    
    Lower is better - score decreases as CO2 increases.
    
    Args:
        value: CO2 concentration in ppm
        config: Mapping configuration
    
    Returns:
        Normalized score between 0 and 1
    """
    return _map_lower_is_better(
        value,
        config.optimal_max,
        config.acceptable_max
    )


def map_humidity(value: float, config: MappingConfig = HUMIDITY_CONFIG) -> float:
    """
    Map relative humidity to a comfort score.
    
    Both too low and too high humidity are undesirable.
    
    Args:
        value: Relative humidity in %
        config: Mapping configuration
    
    Returns:
        Normalized score between 0 and 1
    """
    return _map_range_centered(
        value,
        config.optimal_min, config.optimal_max,
        config.acceptable_min, config.acceptable_max
    )


def map_light(value: float, config: MappingConfig = LIGHT_CONFIG) -> float:
    """
    Map light intensity to a comfort score.
    
    Both too dim and too bright are undesirable for work.
    
    Args:
        value: Light intensity in lux
        config: Mapping configuration
    
    Returns:
        Normalized score between 0 and 1
    """
    return _map_range_centered(
        value,
        config.optimal_min, config.optimal_max,
        config.acceptable_min, config.acceptable_max
    )


def map_noise(value: float, config: MappingConfig = NOISE_CONFIG) -> float:
    """
    Map noise level to a comfort score.
    
    Lower is better - quiet rooms score higher.
    
    Args:
        value: Noise level in dBA
        config: Mapping configuration
    
    Returns:
        Normalized score between 0 and 1
    """
    return _map_lower_is_better(
        value,
        config.optimal_max,
        config.acceptable_max
    )


def map_voc(value: float, config: MappingConfig = VOC_CONFIG) -> float:
    """
    Map VOC concentration to a health score.
    
    Lower is better.
    
    Args:
        value: VOC concentration in ppb
        config: Mapping configuration
    
    Returns:
        Normalized score between 0 and 1
    """
    return _map_lower_is_better(
        value,
        config.optimal_max,
        config.acceptable_max
    )


def map_air_quality(value: float, config: MappingConfig = AIR_QUALITY_CONFIG) -> float:
    """
    Map Air Quality Index to a health score.
    
    Lower AQI is better.
    
    Args:
        value: Air Quality Index (0-500 scale)
        config: Mapping configuration
    
    Returns:
        Normalized score between 0 and 1
    """
    return _map_lower_is_better(
        value,
        config.optimal_max,
        config.acceptable_max
    )


# ============================================================================
# FACILITY MAPPING FUNCTIONS
# ============================================================================

def map_seating_capacity(value: int, required: int) -> float:
    """
    Map seating capacity relative to required seats.
    
    Score:
        - 1.0: Capacity matches requirement within 20%
        - 0.5-1.0: Capacity is 50-80% or 120-200% of requirement
        - 0.0: Capacity is < 50% of requirement
    
    Args:
        value: Available seats
        required: Required number of seats
    
    Returns:
        Normalized score between 0 and 1
    """
    if required <= 0:
        return 1.0 if value > 0 else 0.5
    
    ratio = value / required
    
    if 0.8 <= ratio <= 1.5:
        return 1.0
    elif ratio < 0.8:
        # Not enough seats
        return max(0, ratio / 0.8 * 0.5 + 0.5 * (ratio / 0.8))
    else:
        # Too many seats (less efficient, but acceptable)
        return max(0.5, 1.0 - (ratio - 1.5) * 0.1)


def map_equipment(has_computers: bool, computer_count: int = 0, required: int = 0) -> float:
    """
    Map equipment availability to a usability score.
    
    Args:
        has_computers: Whether the room has computers
        computer_count: Number of computers available
        required: Required number of computers (0 = not required)
    
    Returns:
        Normalized score between 0 and 1
    """
    if required == 0:
        # No computers required - bonus if available
        return 1.0 if not has_computers else 1.0
    
    if not has_computers or computer_count == 0:
        return 0.0
    
    ratio = computer_count / required
    if ratio >= 1.0:
        return 1.0
    return ratio


def map_av_facilities(has_projector: bool, required: bool = False) -> float:
    """
    Map A/V facilities availability.
    
    Args:
        has_projector: Whether room has video projector
        required: Whether a projector is required
    
    Returns:
        Normalized score between 0 and 1
    """
    if required and not has_projector:
        return 0.0
    if not required and has_projector:
        return 1.0  # Bonus
    if required and has_projector:
        return 1.0
    return 0.8  # Neither required nor present


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _map_range_centered(
    value: float,
    optimal_min: float,
    optimal_max: float,
    acceptable_min: float,
    acceptable_max: float
) -> float:
    """
    Map a value to score where optimal range is in the middle.
    
    Returns 1.0 if within optimal range, decreasing toward 0 outside acceptable.
    """
    # Within optimal range
    if optimal_min <= value <= optimal_max:
        return 1.0
    
    # Below optimal but above acceptable minimum
    if acceptable_min <= value < optimal_min:
        range_size = optimal_min - acceptable_min
        if range_size == 0:
            return 0.5
        return 0.5 + 0.5 * (value - acceptable_min) / range_size
    
    # Above optimal but below acceptable maximum
    if optimal_max < value <= acceptable_max:
        range_size = acceptable_max - optimal_max
        if range_size == 0:
            return 0.5
        return 1.0 - 0.5 * (value - optimal_max) / range_size
    
    # Outside acceptable range
    if value < acceptable_min:
        # Decay score below acceptable
        distance = acceptable_min - value
        decay = min(1.0, distance / (acceptable_max - acceptable_min))
        return max(0, 0.5 * (1 - decay))
    
    if value > acceptable_max:
        # Decay score above acceptable
        distance = value - acceptable_max
        decay = min(1.0, distance / (acceptable_max - acceptable_min))
        return max(0, 0.5 * (1 - decay))
    
    return 0.0


def _map_lower_is_better(
    value: float,
    optimal_max: float,
    acceptable_max: float
) -> float:
    """
    Map a value where lower is better (0 is optimal).
    """
    if value <= 0:
        return 1.0
    
    if value <= optimal_max:
        return 1.0
    
    if value <= acceptable_max:
        range_size = acceptable_max - optimal_max
        if range_size == 0:
            return 0.5
        return 1.0 - 0.5 * (value - optimal_max) / range_size
    
    # Above acceptable
    distance = value - acceptable_max
    decay = min(1.0, distance / acceptable_max)
    return max(0, 0.5 * (1 - decay))


# ============================================================================
# MAPPING REGISTRY
# ============================================================================

SENSOR_MAPPING_FUNCTIONS: Dict[str, Callable[[float], float]] = {
    "temperature": map_temperature,
    "co2": map_co2,
    "humidity": map_humidity,
    "light": map_light,
    "noise": map_noise,
    "voc": map_voc,
    "air_quality": map_air_quality,
}


def get_mapping_function(sensor_type: str) -> Callable[[float], float]:
    """
    Get the appropriate mapping function for a sensor type.
    
    Args:
        sensor_type: One of 'temperature', 'co2', 'humidity', 'light', 
                     'noise', 'voc', 'air_quality'
    
    Returns:
        Mapping function
    
    Raises:
        ValueError: If sensor type is not recognized
    """
    key = sensor_type.lower().replace(" ", "_").replace("-", "_")
    
    if key not in SENSOR_MAPPING_FUNCTIONS:
        raise ValueError(
            f"Unknown sensor type: {sensor_type}. "
            f"Available: {list(SENSOR_MAPPING_FUNCTIONS.keys())}"
        )
    
    return SENSOR_MAPPING_FUNCTIONS[key]
