"""search_documents tool implementation."""

from typing import Annotated
from typing import Any

import structlog

from mcp.types import ToolAnnotations
from pydantic import Field

from docs2db_mcp.config import CONFIG
from docs2db_mcp.engine import get_engine
from docs2db_mcp.server import mcp


logger = structlog.get_logger(__name__)

_MAX_QUERY_LENGTH = 2000


@mcp.tool(
    description=(
        "Search official RHEL product documentation and release notes. "
        "This is the PRIMARY source for RHEL-specific information. "
        "Use this for:\n"
        "- RHEL version-specific features (RHEL 9, RHEL 10, etc.)\n"
        "- New features and changes in RHEL releases\n"
        "- Official product documentation and configuration guides\n"
        "- Release notes, package updates, and technical procedures\n"
        "Returns official documentation with exact version information."
    ),
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def search_documents(
    query: Annotated[
        str,
        Field(min_length=1, max_length=_MAX_QUERY_LENGTH, description="Search query string"),
    ],
    max_chunks: Annotated[
        int,
        Field(ge=1, le=CONFIG.rag_max_chunks, description="Maximum number of chunks to return"),
    ] = 5,
    similarity_threshold: Annotated[
        float,
        Field(ge=0.0, le=1.0, description="Minimum similarity score (0.0-1.0)"),
    ] = 0.7,
    enable_reranking: bool = True,
) -> dict[str, Any]:
    """Search RHEL documentation using docs2db RAG engine.

    Args:
        query: Search query string (1-2000 characters)
        max_chunks: Maximum number of chunks to return (1-CONFIG.rag_max_chunks)
        similarity_threshold: Minimum similarity score (0.0-1.0)
        enable_reranking: Enable cross-encoder reranking

    Returns:
        Dictionary containing:
        - chunks: List of matching document chunks with metadata
        - query_used: The original query (refinement disabled)
        - num_results: Number of results returned
    """
    # Runtime input validation — returns the documented error dictionary so
    # callers always receive a consistent response shape.  The Annotated/Field
    # constraints above serve as a first line of defence at the MCP-protocol
    # level (FastMCP rejects invalid values before the function body runs),
    # while this block guards direct invocations and keeps the contract
    # identical for both code paths.
    if not query or len(query) > _MAX_QUERY_LENGTH:
        return {
            "chunks": [],
            "query_used": query,
            "num_results": 0,
            "error": f"query length must be between 1 and {_MAX_QUERY_LENGTH}",
        }
    if not (1 <= max_chunks <= CONFIG.rag_max_chunks):
        return {
            "chunks": [],
            "query_used": query,
            "num_results": 0,
            "error": f"max_chunks must be between 1 and {CONFIG.rag_max_chunks}",
        }
    if not (0.0 <= similarity_threshold <= 1.0):
        return {
            "chunks": [],
            "query_used": query,
            "num_results": 0,
            "error": "similarity_threshold must be between 0.0 and 1.0",
        }

    logger.info("Searching", query_length=len(query), max_chunks=max_chunks)

    try:
        engine = await get_engine()

        # Search using docs2db-api's UniversalRAGEngine
        result = await engine.search_documents(
            query=query,
            max_chunks=max_chunks,
            similarity_threshold=similarity_threshold,
            enable_reranking=enable_reranking,
        )

        # Format results for MCP response
        chunks = [
            {
                "text": doc["text"],
                "similarity": float(doc.get("similarity_score", 0.0)),
                "source": doc.get("document_path", "unknown"),
                "metadata": doc.get("metadata", {}),
                "chunk_index": doc.get("chunk_index"),
                "vector_similarity": doc.get("vector_similarity"),
                "rerank_score": doc.get("rerank_score"),
            }
            for doc in result.documents
        ]

        logger.info("Search complete", num_results=len(chunks))

        return {
            "chunks": chunks,
            "query_used": query,  # No refinement, return original query
            "num_results": len(chunks),
        }

    except Exception as e:
        logger.error("Search failed", error=str(e), exc_info=True)
        return {
            "chunks": [],
            "query_used": query,
            "num_results": 0,
            "error": "internal search error",
        }
