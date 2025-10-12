"""FunctionNode model representing a function, method, or procedure."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Parameter(BaseModel):
    """Function parameter."""

    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    is_optional: bool = False


class FunctionNode(BaseModel):
    """Represents a function, method, or procedure.

    Attributes:
        id: UUID or hash-based ID
        name: Function name
        qualified_name: Full dotted name (e.g., "auth.services.authenticate")
        line_start: Starting line number
        line_end: Ending line number
        docstring: Optional documentation string
        signature: Full function signature
        return_type: Optional return type annotation
        parameters: List of function parameters
        is_async: Whether function is async
        is_exported: Whether function is publicly exported
        decorators: List of decorators applied
        cyclomatic_complexity: Optional code complexity metric
    """

    id: str
    name: str
    qualified_name: str
    line_start: int = Field(..., ge=1)
    line_end: int = Field(..., ge=1)
    docstring: Optional[str] = None
    signature: str
    return_type: Optional[str] = None
    parameters: list[Parameter] = Field(default_factory=list)
    is_async: bool = False
    is_exported: bool = False
    decorators: list[str] = Field(default_factory=list)
    cyclomatic_complexity: Optional[int] = Field(default=None, ge=1)

    @field_validator("line_end")
    @classmethod
    def validate_line_range(cls, v: int, info) -> int:
        """Validate that line_end >= line_start."""
        if v < info.data.get("line_start", 1):
            raise ValueError("line_end must be >= line_start")
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "f7g8h9",
                "name": "authenticate",
                "qualified_name": "auth.services.authenticate",
                "line_start": 50,
                "line_end": 75,
                "docstring": "Authenticates user credentials",
                "signature": "def authenticate(username: str, password: str) -> Optional[User]",
                "return_type": "Optional[User]",
                "parameters": [
                    {"name": "username", "type_hint": "str", "is_optional": False},
                    {"name": "password", "type_hint": "str", "is_optional": False},
                ],
                "is_async": False,
                "is_exported": True,
                "decorators": [],
                "cyclomatic_complexity": 5,
            }
        }
