"""Index snapshot model for reproducible builds.

Provides point-in-time captures of the code graph state.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class IndexSnapshot(BaseModel):
    """Point-in-time snapshot of the code graph.

    Used for reproducible builds and rollback (FR-014).
    """

    id: str = Field(..., description="Unique snapshot identifier")
    timestamp: datetime = Field(..., description="When snapshot was created")
    commit_hash: Optional[str] = Field(None, description="Git commit hash if available")

    # Snapshot metadata
    total_nodes: int = Field(..., description="Total nodes in graph at snapshot time")
    total_edges: int = Field(..., description="Total edges in graph at snapshot time")
    indexed_files: int = Field(..., description="Number of files successfully indexed")
    failed_files: int = Field(default=0, description="Number of files that failed to index")

    # Storage
    storage_path: str = Field(..., description="Path to snapshot data file")
    compressed: bool = Field(default=True, description="Whether snapshot is compressed")
    size_bytes: int = Field(..., description="Snapshot file size in bytes")

    # Validation
    checksum: str = Field(..., description="SHA-256 checksum of snapshot data")

    # Tags for organization
    tags: list[str] = Field(default_factory=list, description="User-defined tags")
    description: Optional[str] = Field(None, description="Snapshot description")

    class Config:
        """Pydantic config."""
        frozen = False
        extra = "forbid"
