"""FileNode model representing a source code file in the repository."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ParseStatus(str, Enum):
    """Parse status for a file."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class FileNode(BaseModel):
    """Represents a source code file in the repository.

    Attributes:
        id: UUID or hash-based ID
        path: Relative path from repository root
        language: Programming language (python, typescript, go, java)
        content_hash: SHA-256 hash of file contents
        size_bytes: File size in bytes
        parse_status: Status of parsing (success, partial, failed)
        error_count: Number of parse errors encountered
        last_indexed: Timestamp when file was last indexed
        embedding: Optional cached semantic embedding (768-dimensional vector)
    """

    id: str = Field(..., description="UUID or hash-based ID")
    path: str = Field(..., description="Relative path from repository root")
    language: str = Field(..., description="Programming language")
    content_hash: str = Field(..., description="SHA-256 hash of file contents")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    parse_status: ParseStatus = Field(..., description="Parse status")
    error_count: int = Field(default=0, ge=0, description="Number of parse errors")
    last_indexed: datetime = Field(..., description="Last index timestamp")
    embedding: Optional[list[float]] = Field(
        default=None,
        description="Cached semantic embedding (768-dim)",
        max_length=768,
    )

    @field_validator("content_hash")
    @classmethod
    def validate_content_hash(cls, v: str) -> str:
        """Validate that content_hash is a valid SHA-256 hash."""
        if len(v) != 64:
            raise ValueError("content_hash must be 64 hex characters (SHA-256)")
        if not all(c in "0123456789abcdef" for c in v.lower()):
            raise ValueError("content_hash must contain only hex characters")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate that language is supported."""
        supported = {"python", "typescript", "javascript", "go", "java"}
        if v.lower() not in supported:
            raise ValueError(f"Unsupported language: {v}. Must be one of {supported}")
        return v.lower()

    @field_validator("parse_status")
    @classmethod
    def validate_parse_status_consistency(cls, v: ParseStatus, info) -> ParseStatus:
        """Validate that parse_status is consistent with error_count."""
        if v == ParseStatus.SUCCESS and info.data.get("error_count", 0) > 0:
            raise ValueError("parse_status cannot be SUCCESS if error_count > 0")
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "f1a2b3c4",
                "path": "src/auth/login.py",
                "language": "python",
                "content_hash": "a7b8c9" + "0" * 58,
                "size_bytes": 4523,
                "parse_status": "success",
                "error_count": 0,
                "last_indexed": "2025-10-12T10:30:00Z",
                "embedding": [0.12, -0.34] + [0.0] * 766,
            }
        }
