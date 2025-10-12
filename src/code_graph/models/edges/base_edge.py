"""Base edge model for all relationship types."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class EdgeType(str, Enum):
    """Types of relationships between code elements."""

    CONTAINS = "CONTAINS"
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    INHERITS = "INHERITS"
    READS_WRITES = "READS_WRITES"
    TESTS = "TESTS"


class ConfidenceLevel(str, Enum):
    """Confidence level for relationship."""

    HIGH = "high"  # 0.8-1.0
    MEDIUM = "medium"  # 0.5-0.79
    LOW = "low"  # 0.0-0.49


class BaseEdge(BaseModel):
    """Base class for all edge types.

    Attributes:
        type: Type of relationship
        confidence: Confidence score (0.0-1.0)
        metadata: Additional relationship-specific data
    """

    type: EdgeType
    confidence: float = Field(..., ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is in valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return v

    def get_confidence_level(self) -> ConfidenceLevel:
        """Get the confidence level category."""
        if self.confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def should_warn_user(self, threshold: float = 0.70) -> bool:
        """Check if confidence is below warning threshold."""
        return self.confidence <= threshold


class ContainsEdge(BaseEdge):
    """Represents containment relationship (file contains module, class contains function)."""

    type: EdgeType = EdgeType.CONTAINS


class ImportsEdge(BaseEdge):
    """Represents import/include/require relationships."""

    type: EdgeType = EdgeType.IMPORTS
    import_type: str = Field(..., pattern="^(absolute|relative|dynamic)$")
    imported_names: list[str] = Field(default_factory=list)
    is_resolved: bool = Field(..., description="Whether target file was found")


class CallsEdge(BaseEdge):
    """Represents function call relationships."""

    type: EdgeType = EdgeType.CALLS
    call_type: str = Field(..., pattern="^(direct|indirect|dynamic)$")
    is_recursive: bool = False


class InheritsEdge(BaseEdge):
    """Represents class inheritance or interface implementation."""

    type: EdgeType = EdgeType.INHERITS
    inheritance_type: str = Field(..., pattern="^(extends|implements|mixin)$")
    is_direct: bool = True


class ReadsWritesEdge(BaseEdge):
    """Represents data access relationships."""

    type: EdgeType = EdgeType.READS_WRITES
    access_type: str = Field(..., pattern="^(reads|writes|both)$")


class TestsEdge(BaseEdge):
    """Represents test coverage relationship."""

    type: EdgeType = EdgeType.TESTS
    coverage_type: str = Field(..., pattern="^(unit|integration|e2e)$")
    coverage_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
