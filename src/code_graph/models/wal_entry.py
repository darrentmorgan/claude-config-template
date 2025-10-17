"""Write-Ahead Log entry model for durability.

Provides transaction logging for graph operations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class WALOperationType(str, Enum):
    """Type of WAL operation."""
    CREATE_NODE = "CREATE_NODE"
    UPDATE_NODE = "UPDATE_NODE"
    DELETE_NODE = "DELETE_NODE"
    CREATE_EDGE = "CREATE_EDGE"
    DELETE_EDGE = "DELETE_EDGE"
    BEGIN_TRANSACTION = "BEGIN_TRANSACTION"
    COMMIT_TRANSACTION = "COMMIT_TRANSACTION"
    ROLLBACK_TRANSACTION = "ROLLBACK_TRANSACTION"


class WALEntry(BaseModel):
    """Write-Ahead Log entry for graph operations.

    Implements WAL for durability (FR-014).
    Operations are logged before being applied to the graph.
    """

    id: str = Field(..., description="Unique WAL entry identifier")
    sequence_number: int = Field(..., description="Sequential number for ordering")
    timestamp: datetime = Field(..., description="When operation was logged")

    # Operation details
    operation: WALOperationType = Field(..., description="Type of operation")
    entity_type: str = Field(..., description="Type of entity (node/edge type)")
    entity_id: str = Field(..., description="ID of entity being operated on")

    # Operation data
    data: dict[str, Any] = Field(..., description="Operation payload (new values, etc.)")
    previous_data: Optional[dict[str, Any]] = Field(
        None,
        description="Previous state for rollback"
    )

    # Transaction context
    transaction_id: Optional[str] = Field(None, description="Transaction ID if part of transaction")

    # Status
    applied: bool = Field(default=False, description="Whether operation has been applied")
    checksum: str = Field(..., description="Checksum for entry validation")

    class Config:
        """Pydantic config."""
        frozen = False
        extra = "forbid"
