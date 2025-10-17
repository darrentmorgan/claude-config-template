"""Test node model for code graph.

Represents a test function or test class in the codebase.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TestNode(BaseModel):
    """Test node in the code graph.

    Represents unit tests, integration tests, or test suites.
    Used for targeted test selection (User Story 5).
    """

    id: str = Field(..., description="Unique identifier for the test")
    name: str = Field(..., description="Test name (function or class name)")
    file_path: str = Field(..., description="Test file path")
    test_type: str = Field(..., description="Type: unit, integration, e2e")
    language: str = Field(..., description="Programming language")
    line_start: int = Field(..., description="Starting line number")
    line_end: int = Field(..., description="Ending line number")

    # Test characteristics
    framework: str = Field(..., description="Test framework (pytest, jest, go test, etc.)")
    test_suite: Optional[str] = Field(None, description="Test suite/class this test belongs to")

    # Coverage tracking
    covered_functions: list[str] = Field(
        default_factory=list,
        description="Function IDs that this test covers"
    )
    covered_classes: list[str] = Field(
        default_factory=list,
        description="Class IDs that this test covers"
    )

    # Metadata
    docstring: Optional[str] = Field(None, description="Test description")
    tags: list[str] = Field(default_factory=list, description="Test tags/markers")

    class Config:
        """Pydantic config."""
        frozen = False
        extra = "forbid"
