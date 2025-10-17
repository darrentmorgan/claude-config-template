"""Configuration management for code graph indexer.

Loads and validates configuration from .code-graph/config.yaml
"""

import os
from pathlib import Path
from typing import Any, Optional
import yaml
from pydantic import BaseModel, Field


class IndexerConfig(BaseModel):
    """Main configuration for code graph indexer."""

    # Memgraph connection
    memgraph_host: str = Field(default="localhost", description="Memgraph host")
    memgraph_port: int = Field(default=7687, description="Memgraph Bolt port")
    memgraph_user: str = Field(default="", description="Memgraph username")
    memgraph_password: str = Field(default="", description="Memgraph password")

    # Indexing settings
    max_file_size_mb: int = Field(default=10, description="Skip files larger than this")
    supported_languages: list[str] = Field(
        default_factory=lambda: ["python", "typescript", "javascript", "go", "java"],
        description="Languages to index"
    )
    exclude_patterns: list[str] = Field(
        default_factory=lambda: ["node_modules", ".venv", "__pycache__", ".git"],
        description="Directories to exclude"
    )

    # Performance
    max_workers: int = Field(default=4, description="Parallel processing workers")
    embedding_batch_size: int = Field(default=32, description="Batch size for embeddings")

    # Hybrid scoring weights
    embedding_weight: float = Field(default=0.4, description="Semantic similarity weight")
    graph_weight: float = Field(default=0.4, description="Graph proximity weight")
    signal_weight: float = Field(default=0.2, description="Execution signal weight")

    # Query settings
    default_top_n: int = Field(default=10, description="Default number of results")
    max_top_n: int = Field(default=50, description="Maximum results to return")
    default_neighbor_hops: int = Field(default=2, description="Default neighbor expansion hops")
    max_neighbor_hops: int = Field(default=5, description="Maximum neighbor hops")

    # Confidence thresholds
    confidence_warning_threshold: float = Field(
        default=0.70,
        description="Warn when confidence <= this"
    )

    # Storage
    wal_enabled: bool = Field(default=True, description="Enable Write-Ahead Logging")
    snapshot_enabled: bool = Field(default=True, description="Enable snapshots")
    snapshot_interval_hours: int = Field(default=24, description="Auto-snapshot interval")

    class Config:
        """Pydantic config."""
        extra = "forbid"


def load_config(config_path: Optional[str] = None) -> IndexerConfig:
    """Load configuration from file or use defaults.

    Args:
        config_path: Path to config.yaml file. If None, looks for .code-graph/config.yaml

    Returns:
        IndexerConfig instance

    Raises:
        FileNotFoundError: If specified config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    if config_path is None:
        # Look for config in standard locations
        possible_paths = [
            Path.cwd() / ".code-graph" / "config.yaml",
            Path.home() / ".code-graph" / "config.yaml",
        ]
        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break

    if config_path is None:
        # No config file found, use defaults
        return IndexerConfig()

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f) or {}

    # Override with environment variables if set
    env_overrides = {}
    if os.getenv("MEMGRAPH_HOST"):
        env_overrides["memgraph_host"] = os.getenv("MEMGRAPH_HOST")
    if os.getenv("MEMGRAPH_PORT"):
        env_overrides["memgraph_port"] = int(os.getenv("MEMGRAPH_PORT"))

    config_data.update(env_overrides)

    return IndexerConfig(**config_data)


def save_config(config: IndexerConfig, config_path: str) -> None:
    """Save configuration to file.

    Args:
        config: Configuration to save
        config_path: Path to save config file
    """
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False)
