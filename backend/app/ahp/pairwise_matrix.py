"""
Pairwise Comparison Matrix for AHP Algorithm.

This module implements the Saaty pairwise comparison matrix used in the
Analytic Hierarchy Process (AHP) for multi-criteria decision making.

The Saaty scale ranges from 1 to 9:
    1 - Equal importance
    3 - Moderate importance of one over another
    5 - Strong importance
    7 - Very strong importance
    9 - Absolute importance
    2, 4, 6, 8 - Intermediate values
"""

import numpy as np
from typing import Dict, List, Optional, Tuple

# Saaty scale constants
SAATY_SCALE = {
    1: "Equal importance",
    2: "Weak importance (intermediate)",
    3: "Moderate importance",
    4: "Moderate plus (intermediate)",
    5: "Strong importance",
    6: "Strong plus (intermediate)",
    7: "Very strong importance",
    8: "Very, very strong (intermediate)",
    9: "Absolute importance",
}


class PairwiseMatrix:
    """
    Represents a pairwise comparison matrix for AHP.
    
    The matrix is square and reciprocal: if a[i][j] = x, then a[j][i] = 1/x.
    Diagonal elements are always 1 (criterion compared to itself).
    
    Example:
        >>> pm = PairwiseMatrix(['Temperature', 'CO2', 'Humidity'])
        >>> pm.set_comparison('Temperature', 'CO2', 3)  # Temp is 3x more important than CO2
        >>> pm.set_comparison('Temperature', 'Humidity', 5)
        >>> pm.set_comparison('CO2', 'Humidity', 2)
        >>> matrix = pm.get_matrix()
    """
    
    def __init__(self, criteria: List[str]):
        """
        Initialize a pairwise comparison matrix.
        
        Args:
            criteria: List of criterion names (order matters for matrix indexing)
        """
        if len(criteria) < 2:
            raise ValueError("At least 2 criteria are required for pairwise comparison")
        
        self.criteria = list(criteria)
        self.n = len(criteria)
        self._index_map = {name: i for i, name in enumerate(criteria)}
        
        # Initialize with identity matrix (all equal importance = 1)
        self._matrix = np.ones((self.n, self.n), dtype=float)
    
    def set_comparison(self, criterion_a: str, criterion_b: str, value: float) -> None:
        """
        Set the pairwise comparison value between two criteria.
        
        Args:
            criterion_a: First criterion name
            criterion_b: Second criterion name  
            value: Saaty scale value (1-9). If criterion_a is `value` times 
                   more important than criterion_b. Use fractions (1/3, 1/5, etc.)
                   if criterion_a is less important.
        
        Raises:
            ValueError: If value is outside valid range or criteria not found
        """
        if criterion_a not in self._index_map:
            raise ValueError(f"Criterion '{criterion_a}' not found")
        if criterion_b not in self._index_map:
            raise ValueError(f"Criterion '{criterion_b}' not found")
        
        if not (1/9 <= value <= 9):
            raise ValueError(f"Value must be between 1/9 and 9, got {value}")
        
        i = self._index_map[criterion_a]
        j = self._index_map[criterion_b]
        
        self._matrix[i, j] = value
        self._matrix[j, i] = 1.0 / value  # Reciprocal property
    
    def set_comparison_by_index(self, i: int, j: int, value: float) -> None:
        """
        Set comparison by matrix indices (for bulk operations).
        
        Args:
            i: Row index
            j: Column index
            value: Saaty scale value
        """
        if not (0 <= i < self.n and 0 <= j < self.n):
            raise ValueError(f"Indices out of range: ({i}, {j})")
        if not (1/9 <= value <= 9):
            raise ValueError(f"Value must be between 1/9 and 9, got {value}")
        
        self._matrix[i, j] = value
        self._matrix[j, i] = 1.0 / value
    
    def get_matrix(self) -> np.ndarray:
        """Return a copy of the comparison matrix."""
        return self._matrix.copy()
    
    def get_comparison(self, criterion_a: str, criterion_b: str) -> float:
        """Get the comparison value between two criteria."""
        i = self._index_map[criterion_a]
        j = self._index_map[criterion_b]
        return self._matrix[i, j]
    
    def is_valid(self) -> Tuple[bool, Optional[str]]:
        """
        Validate the matrix properties.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check diagonal is all 1s
        if not np.allclose(np.diag(self._matrix), 1.0):
            return False, "Diagonal elements must be 1"
        
        # Check reciprocity
        for i in range(self.n):
            for j in range(i + 1, self.n):
                expected_reciprocal = 1.0 / self._matrix[i, j]
                if not np.isclose(self._matrix[j, i], expected_reciprocal, rtol=1e-5):
                    return False, f"Reciprocity violated at ({i},{j}): {self._matrix[i,j]} vs {self._matrix[j,i]}"
        
        # Check all values are positive
        if np.any(self._matrix <= 0):
            return False, "All values must be positive"
        
        return True, None
    
    def from_flat_upper_triangle(self, values: List[float]) -> None:
        """
        Populate matrix from upper triangle values (row by row).
        
        This is useful for UI input where user provides n(n-1)/2 comparisons.
        
        Args:
            values: List of comparison values for upper triangle,
                    ordered row by row from (0,1), (0,2), ..., (n-2, n-1)
        
        Expected length: n(n-1)/2
        """
        expected_len = self.n * (self.n - 1) // 2
        if len(values) != expected_len:
            raise ValueError(f"Expected {expected_len} values, got {len(values)}")
        
        idx = 0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                self.set_comparison_by_index(i, j, values[idx])
                idx += 1
    
    def __repr__(self) -> str:
        return f"PairwiseMatrix(criteria={self.criteria})"
    
    def __str__(self) -> str:
        """Pretty print the matrix with labels."""
        header = "        " + "  ".join(f"{c[:6]:>6}" for c in self.criteria)
        rows = []
        for i, criterion in enumerate(self.criteria):
            row_values = "  ".join(f"{v:6.3f}" for v in self._matrix[i])
            rows.append(f"{criterion[:6]:>6}  {row_values}")
        return header + "\n" + "\n".join(rows)


def create_default_criteria_matrix() -> PairwiseMatrix:
    """
    Create a default comparison matrix for main criteria.
    
    Default weights targeting:
    - Comfort: 40%
    - Health: 35%  
    - Usability: 25%
    
    These translate to approximate Saaty scale values.
    """
    criteria = ["Comfort", "Health", "Usability"]
    pm = PairwiseMatrix(criteria)
    
    # Comfort vs Health: roughly equal, slight preference for comfort
    pm.set_comparison("Comfort", "Health", 1.2)
    
    # Comfort vs Usability: comfort moderately more important
    pm.set_comparison("Comfort", "Usability", 2.0)
    
    # Health vs Usability: health slightly more important  
    pm.set_comparison("Health", "Usability", 1.5)
    
    return pm


def create_comfort_subcriteria_matrix() -> PairwiseMatrix:
    """Default matrix for Comfort sub-criteria."""
    criteria = ["Temperature", "Lighting", "Noise", "Humidity"]
    pm = PairwiseMatrix(criteria)
    
    # Temperature most important for comfort
    pm.set_comparison("Temperature", "Lighting", 2)
    pm.set_comparison("Temperature", "Noise", 2)
    pm.set_comparison("Temperature", "Humidity", 3)
    
    # Lighting and Noise roughly equal
    pm.set_comparison("Lighting", "Noise", 1)
    pm.set_comparison("Lighting", "Humidity", 2)
    
    pm.set_comparison("Noise", "Humidity", 2)
    
    return pm


def create_health_subcriteria_matrix() -> PairwiseMatrix:
    """Default matrix for Health sub-criteria."""
    criteria = ["CO2", "AirQuality", "VOC"]
    pm = PairwiseMatrix(criteria)
    
    # CO2 is most critical health indicator
    pm.set_comparison("CO2", "AirQuality", 2)
    pm.set_comparison("CO2", "VOC", 2)
    
    # Air quality slightly more important than VOC
    pm.set_comparison("AirQuality", "VOC", 1.5)
    
    return pm


def create_usability_subcriteria_matrix() -> PairwiseMatrix:
    """Default matrix for Usability sub-criteria."""
    criteria = ["SeatingCapacity", "Equipment", "AVFacilities"]
    pm = PairwiseMatrix(criteria)
    
    # Seating capacity usually most important for room selection
    pm.set_comparison("SeatingCapacity", "Equipment", 2)
    pm.set_comparison("SeatingCapacity", "AVFacilities", 3)
    
    # Computers more important than just projector
    pm.set_comparison("Equipment", "AVFacilities", 2)
    
    return pm
