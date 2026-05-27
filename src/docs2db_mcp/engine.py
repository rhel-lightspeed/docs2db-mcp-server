"""RAG engine singleton wrapper.

Heavy dependencies (torch, transformers, docs2db-api) are imported lazily
inside ``get_engine()`` so that importing this module is near-instant.
"""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from docs2db_mcp.config import CONFIG


if TYPE_CHECKING:
    from docs2db_api.rag.engine import UniversalRAGEngine


logger = logging.getLogger(__name__)

_engine: UniversalRAGEngine | None = None


async def get_engine() -> UniversalRAGEngine:
    """Get or create the singleton RAG engine instance.

    On first call this imports ``docs2db-api`` (which pulls in torch,
    transformers, etc.) and initialises the engine.  Subsequent calls
    return the cached instance.

    Returns:
        Initialized UniversalRAGEngine instance

    Raises:
        Exception: If engine initialization fails
    """
    global _engine

    if _engine is None:
        from docs2db_api.rag.engine import RAGConfig
        from docs2db_api.rag.engine import UniversalRAGEngine

        logger.info("Initializing UniversalRAGEngine")

        # Configure database connection (dict format)
        db_config = {
            "host": CONFIG.db_host,
            "port": str(CONFIG.db_port),
            "database": CONFIG.db_database,
            "user": CONFIG.db_user,
            "password": CONFIG.db_password,
        }

        # Configure RAG (no LLM config - refinement disabled)
        rag_config = RAGConfig()
        rag_config.similarity_threshold = CONFIG.rag_similarity_threshold
        rag_config.max_chunks = CONFIG.rag_max_chunks
        rag_config.enable_reranking = CONFIG.rag_enable_reranking
        rag_config.enable_question_refinement = False  # Disabled for tool calling

        # Create and initialize engine
        _engine = UniversalRAGEngine(
            config=rag_config,
            db_config=db_config,
        )

        try:
            await _engine.start()
            logger.info("UniversalRAGEngine initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize RAG engine: %s", e)
            _engine = None
            raise

    return _engine


async def shutdown_engine() -> None:
    """Shutdown the RAG engine and cleanup resources."""
    global _engine

    if _engine is not None:
        logger.info("Shutting down UniversalRAGEngine")
        # UniversalRAGEngine doesn't have a stop() method
        # Just set to None to allow garbage collection
        _engine = None


async def health_check() -> None:
    """Perform startup health check to verify database connectivity and functionality.

    Raises:
        Exception: If health check fails (database unreachable, query fails, etc.)
    """
    logger.info("Performing startup health check...")

    try:
        # Initialize engine and connect to database
        engine = await get_engine()
        logger.info("Database connection established")

        # Perform a simple test query to verify the system works
        test_query = "test"
        result = await engine.search_documents(
            query=test_query,
            max_chunks=1,
            similarity_threshold=0.0,
            enable_reranking=False,
        )

        # Verify we got a valid response
        if result is None:
            msg = "Health check query returned None"
            raise Exception(msg)

        logger.info("Test query successful (returned %d documents)", len(result.documents))
        logger.info("Health check passed - system is ready")

    except Exception as e:
        logger.error("Health check failed: %s", e, exc_info=True)
        raise Exception(f"Startup health check failed - cannot connect to database or perform queries: {e}") from e
