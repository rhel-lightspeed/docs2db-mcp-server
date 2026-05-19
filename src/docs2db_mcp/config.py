"""Configuration management for docs2db MCP server."""

from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Config(BaseSettings):
    """Configuration for docs2db MCP server.

    All settings can be configured via environment variables with the
    DOCS2DB_MCP_ prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="DOCS2DB_MCP_",
        env_ignore_empty=True,
        extra="ignore",
    )

    # MCP Server Settings
    transport: Literal["stdio", "http", "sse", "streamable-http"] = Field(
        default="sse",
        description="Transport type (stdio, http, sse, streamable-http)",
    )
    host: str = Field(
        default="0.0.0.0",  # noqa: S104 — intentional: server binds to all interfaces
        description="Bind address for SSE transport",
    )
    port: int = Field(
        default=8002,
        description="Port number for SSE transport",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )

    # Database Settings
    db_host: str = Field(
        default="localhost",
        description="PostgreSQL host",
    )
    db_port: int = Field(
        default=5432,
        description="PostgreSQL port",
    )
    db_database: str = Field(
        default="ragdb",
        description="Database name",
    )
    db_user: str = Field(
        default="postgres",
        description="Database user",
    )
    db_password: str = Field(
        default="postgres",
        description="Database password",
    )

    # RAG Settings
    rag_similarity_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for search results",
        ge=0.0,
        le=1.0,
    )
    rag_max_chunks: int = Field(
        default=5,
        description="Maximum number of chunks to return",
        ge=1,
        le=100,
    )
    rag_enable_reranking: bool = Field(
        default=True,
        description="Enable cross-encoder reranking",
    )

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        return f"postgresql://{user}:{password}@{self.db_host}:{self.db_port}/{self.db_database}"


# Global config instance
CONFIG = Config()
