"""Class node model for code graph.

Represents a class, struct, or interface definition in the codebase.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ClassNode(BaseModel):
    """Class/struct/interface node in the code graph.

    Represents object-oriented structures like classes (Python, Java),
    structs (Go), or interfaces (TypeScript, Go).
    """

    id: str = Field(..., description="Unique identifier for the class")
    name: str = Field(..., description="Class name")
    file_path: str = Field(..., description="File containing this class")
    language: str = Field(..., description="Programming language")
    line_start: int = Field(..., description="Starting line number")
    line_end: int = Field(..., description="Ending line number")

    # Class characteristics
    is_abstract: bool = Field(default=False, description="Whether class is abstract")
    is_interface: bool = Field(default=False, description="Whether this is an interface")
    base_classes: list[str] = Field(default_factory=list, description="Parent classes/interfaces")

    # Members
    methods: list[str] = Field(default_factory=list, description="Method names in this class")
    properties: list[str] = Field(default_factory=list, description="Property/field names")

    # Documentation
    docstring: Optional[str] = Field(None, description="Class-level documentation")
    decorators: list[str] = Field(default_factory=list, description="Decorators applied to class")

    class Config:
        """Pydantic config."""
        frozen = False
        extra = "forbid"
