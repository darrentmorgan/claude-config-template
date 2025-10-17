"""Module node model for code graph.

Represents a module/package in the codebase (e.g., a Python module, JavaScript file with exports).
"""

from typing import Optional
from pydantic import BaseModel, Field


class ModuleNode(BaseModel):
    """Module node in the code graph.

    Represents a module or package containing multiple code elements.
    Examples: Python modules (__init__.py), JavaScript modules, Go packages.
    """

    id: str = Field(..., description="Unique identifier for the module")
    path: str = Field(..., description="File path to the module")
    name: str = Field(..., description="Module name (e.g., 'utils', 'core.services')")
    language: str = Field(..., description="Programming language (python, typescript, go, etc.)")
    content_hash: str = Field(..., description="Hash of module content for change detection")
    exports: list[str] = Field(default_factory=list, description="List of exported symbols")
    imports: list[str] = Field(default_factory=list, description="List of imported module names")
    docstring: Optional[str] = Field(None, description="Module-level documentation")

    class Config:
        """Pydantic config."""
        frozen = False
        extra = "forbid"
