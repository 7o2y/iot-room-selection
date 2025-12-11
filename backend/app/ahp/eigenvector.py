"""
Eigenvector Calculation and Consistency Ratio for AHP.

This module implements the priority weight calculation using the eigenvector
method and validates the consistency of pairwise comparison matrices.

Key concepts:
- Priority Vector: The principal eigenvector of the comparison matrix,
  normalized so weights sum to 1.
- Consistency Index (CI): Measures deviation from perfect consistency.
- Consistency Ratio (CR): CI / RI, where RI is the Random Index.
  CR < 0.1 is considered acceptable.
"""

import numpy as np
from typing import Tuple, Optional

# Random Index (RI) values for matrices of size n
# Derived from Saaty's original research (average CI of random matrices)
RANDOM_INDEX = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
    11: 1.51,
    12: 1.53,
    13: 1.56,
    14: 1.57,
    15: 1.59,
}


def calculate_priority_weights(matrix: np.ndarray, method: str = "eigenvector") -> np.ndarray:
    """
    Calculate priority weights from a pairwise comparison matrix.
    
    Args:
        matrix: Square numpy array representing the pairwise comparison matrix
        method: Calculation method:
            - "eigenvector": Principal eigenvector method (most accurate)
            - "geometric_mean": Row geometric mean method (faster approximation)
            - "normalized_sum": Column sum normalization (simplest)
    
    Returns:
        Normalized weight vector (sums to 1.0)
    
    Raises:
        ValueError: If matrix is not square or method is invalid
    """
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Matrix must be square")
    
    n = matrix.shape[0]
    
    if method == "eigenvector":
        return _eigenvector_method(matrix)
    elif method == "geometric_mean":
        return _geometric_mean_method(matrix)
    elif method == "normalized_sum":
        return _normalized_sum_method(matrix)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'eigenvector', 'geometric_mean', or 'normalized_sum'")


def _eigenvector_method(matrix: np.ndarray) -> np.ndarray:
    """
    Calculate weights using the principal eigenvector.
    
    This is the theoretically correct method for AHP.
    """
    # Calculate eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    
    # Find the principal (largest real) eigenvalue
    # For a consistent matrix, this equals n
    real_eigenvalues = np.real(eigenvalues)
    principal_index = np.argmax(real_eigenvalues)
    
    # Get the corresponding eigenvector
    principal_eigenvector = np.real(eigenvectors[:, principal_index])
    
    # Normalize to sum to 1
    weights = principal_eigenvector / np.sum(principal_eigenvector)
    
    # Ensure all weights are positive (flip sign if needed)
    if np.any(weights < 0):
        weights = -weights
    
    return weights


def _geometric_mean_method(matrix: np.ndarray) -> np.ndarray:
    """
    Calculate weights using row geometric means.
    
    This is a good approximation that's computationally simpler.
    """
    n = matrix.shape[0]
    
    # Calculate geometric mean of each row
    geometric_means = np.power(np.prod(matrix, axis=1), 1.0 / n)
    
    # Normalize
    weights = geometric_means / np.sum(geometric_means)
    
    return weights


def _normalized_sum_method(matrix: np.ndarray) -> np.ndarray:
    """
    Calculate weights by normalizing column sums then averaging rows.
    
    This is the simplest approximation method.
    """
    # Normalize each column to sum to 1
    col_sums = np.sum(matrix, axis=0)
    normalized = matrix / col_sums
    
    # Average across rows
    weights = np.mean(normalized, axis=1)
    
    return weights


def calculate_lambda_max(matrix: np.ndarray, weights: np.ndarray) -> float:
    """
    Calculate the maximum eigenvalue (λmax) from the matrix and its weights.
    
    For a perfectly consistent matrix, λmax = n.
    
    Args:
        matrix: Pairwise comparison matrix
        weights: Priority weight vector
    
    Returns:
        Maximum eigenvalue (λmax)
    """
    n = matrix.shape[0]
    
    # Aw = λmax * w
    # λmax = sum((Aw)_i / w_i) / n
    aw = matrix @ weights
    
    # Avoid division by zero for very small weights
    with np.errstate(divide='ignore', invalid='ignore'):
        ratios = np.where(weights > 1e-10, aw / weights, n)
    
    lambda_max = np.mean(ratios)
    
    return lambda_max


def calculate_consistency_index(matrix: np.ndarray, weights: Optional[np.ndarray] = None) -> float:
    """
    Calculate the Consistency Index (CI).
    
    CI = (λmax - n) / (n - 1)
    
    Args:
        matrix: Pairwise comparison matrix
        weights: Optional pre-calculated weights (will be computed if not provided)
    
    Returns:
        Consistency Index value
    """
    n = matrix.shape[0]
    
    if n == 1:
        return 0.0
    
    if weights is None:
        weights = calculate_priority_weights(matrix)
    
    lambda_max = calculate_lambda_max(matrix, weights)
    
    ci = (lambda_max - n) / (n - 1)
    
    return ci


def calculate_consistency_ratio(matrix: np.ndarray, weights: Optional[np.ndarray] = None) -> Tuple[float, bool]:
    """
    Calculate the Consistency Ratio (CR) and check if it's acceptable.
    
    CR = CI / RI
    
    A CR < 0.1 (10%) is generally considered acceptable, meaning the
    pairwise comparisons are sufficiently consistent.
    
    Args:
        matrix: Pairwise comparison matrix
        weights: Optional pre-calculated weights
    
    Returns:
        Tuple of (CR value, is_acceptable: bool)
    
    Raises:
        ValueError: If matrix size exceeds RI table (n > 15)
    """
    n = matrix.shape[0]
    
    if n > 15:
        raise ValueError(f"Matrix size {n} exceeds maximum supported size of 15")
    
    if n <= 2:
        # For 1x1 or 2x2 matrices, CR is always 0 (perfectly consistent)
        return 0.0, True
    
    ci = calculate_consistency_index(matrix, weights)
    ri = RANDOM_INDEX[n]
    
    if ri == 0:
        return 0.0, True
    
    cr = ci / ri
    is_acceptable = cr < 0.1
    
    return cr, is_acceptable


def validate_matrix_consistency(matrix: np.ndarray, threshold: float = 0.1) -> Tuple[bool, dict]:
    """
    Perform full consistency validation on a pairwise comparison matrix.
    
    Args:
        matrix: Pairwise comparison matrix
        threshold: CR threshold for acceptability (default 0.1)
    
    Returns:
        Tuple of (is_valid, details_dict)
        
        details_dict contains:
        - weights: Priority weight vector
        - lambda_max: Maximum eigenvalue
        - ci: Consistency Index
        - cr: Consistency Ratio
        - is_consistent: Whether CR < threshold
        - n: Matrix size
    """
    n = matrix.shape[0]
    
    weights = calculate_priority_weights(matrix)
    lambda_max = calculate_lambda_max(matrix, weights)
    ci = calculate_consistency_index(matrix, weights)
    cr, is_consistent = calculate_consistency_ratio(matrix, weights)
    
    details = {
        "weights": weights,
        "lambda_max": lambda_max,
        "ci": ci,
        "cr": cr,
        "is_consistent": is_consistent and cr < threshold,
        "n": n,
        "ri": RANDOM_INDEX.get(n, None),
    }
    
    return details["is_consistent"], details


def format_weights(weights: np.ndarray, criteria_names: list) -> str:
    """
    Format weights as a readable string with percentages.
    
    Args:
        weights: Weight vector
        criteria_names: List of criterion names
    
    Returns:
        Formatted string with criterion names and percentages
    """
    lines = []
    for name, weight in zip(criteria_names, weights):
        lines.append(f"  {name}: {weight:.4f} ({weight*100:.1f}%)")
    return "\n".join(lines)
