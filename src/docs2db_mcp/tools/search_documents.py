"""search_documents tool implementation."""

import logging
from typing import Any

from mcp.types import ToolAnnotations

from docs2db_mcp.engine import get_engine
from docs2db_mcp.server import mcp

logger = logging.getLogger(__name__)


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
    query: str,
    max_chunks: int = 5,
    similarity_threshold: float = 0.7,
    enable_reranking: bool = True,
) -> dict[str, Any]:
    """Search RHEL documentation using docs2db RAG engine.

    Args:
        query: Search query string
        max_chunks: Maximum number of chunks to return (1-100)
        similarity_threshold: Minimum similarity score (0.0-1.0)
        enable_reranking: Enable cross-encoder reranking

    Returns:
        Dictionary containing:
        - chunks: List of matching document chunks with metadata
        - query_used: The original query (refinement disabled)
        - num_results: Number of results returned
    """
    logger.info(f"Searching for: {query!r} (max_chunks={max_chunks})")

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

        logger.info(f"Found {len(chunks)} results")

        return {
            "chunks": chunks,
            "query_used": query,  # No refinement, return original query
            "num_results": len(chunks),
        }

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        return {
            "chunks": [],
            "query_used": query,
            "num_results": 0,
            "error": str(e),
        }
