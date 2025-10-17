"""Confidence scoring utilities for code graph relationships.

Calculates and interprets confidence scores for graph relationships.
"""

from enum import Enum
from typing import Optional


class ConfidenceLevel(str, Enum):
    """Confidence level categories."""
    HIGH = "high"      # >= 0.90
    MEDIUM = "medium"  # >= 0.70
    LOW = "low"        # < 0.70


def calculate_parse_confidence(
    error_count: int,
    total_nodes: int,
    has_syntax_errors: bool
) -> float:
    """Calculate confidence score based on parsing results.

    Args:
        error_count: Number of ERROR nodes in AST
        total_nodes: Total nodes in AST
        has_syntax_errors: Whether file has syntax errors

    Returns:
        Confidence score between 0.0 and 1.0
    """
    if total_nodes == 0:
        return 0.0

    # Base confidence
    confidence = 1.0

    # Reduce based on syntax errors
    if has_syntax_errors:
        confidence *= 0.7  # Syntax errors reduce confidence to 70%

    # Reduce based on ERROR node proportion
    if error_count > 0:
        error_ratio = error_count / total_nodes
        confidence *= (1.0 - error_ratio * 0.5)  # Each error reduces confidence

    return max(0.0, min(1.0, confidence))


def calculate_relationship_confidence(
    source_confidence: float,
    target_exists: bool,
    import_resolved: bool
) -> float:
    """Calculate confidence for a relationship between nodes.

    Args:
        source_confidence: Confidence of source node
        target_exists: Whether target node exists in graph
        import_resolved: Whether import path resolves to actual file

    Returns:
        Confidence score between 0.0 and 1.0
    """
    # Start with source confidence
    confidence = source_confidence

    # Penalize unresolved targets
    if not target_exists:
        confidence *= 0.5  # Missing target = 50% confidence

    # Bonus for resolved imports
    if target_exists and import_resolved:
        confidence = min(1.0, confidence * 1.1)  # Slight bonus

    return max(0.0, min(1.0, confidence))


def get_confidence_level(score: float) -> ConfidenceLevel:
    """Convert confidence score to categorical level.

    Args:
        score: Confidence score between 0.0 and 1.0

    Returns:
        ConfidenceLevel enum value
    """
    if score >= 0.90:
        return ConfidenceLevel.HIGH
    elif score >= 0.70:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW


def should_warn(score: float, threshold: float = 0.70) -> bool:
    """Check if confidence score should trigger a warning.

    Args:
        score: Confidence score
        threshold: Warning threshold (default 0.70 per FR-003)

    Returns:
        True if warning should be shown
    """
    return score <= threshold


def format_confidence_message(
    score: float,
    reason: Optional[str] = None
) -> str:
    """Format a human-readable confidence message.

    Args:
        score: Confidence score
        reason: Optional reason for low confidence

    Returns:
        Formatted message string
    """
    level = get_confidence_level(score)
    percentage = int(score * 100)

    base_msg = f"Confidence: {percentage}% ({level.value})"

    if reason and should_warn(score):
        return f"⚠️  {base_msg} - {reason}"

    return base_msg
