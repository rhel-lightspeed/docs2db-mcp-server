"""RAG engine singleton wrapper.

Heavy dependencies (torch, transformers, docs2db-api) are imported lazily
inside ``get_engine()`` so that importing this module is near-instant.
"""

from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING

import structlog

from docs2db_mcp.config import CONFIG


if TYPE_CHECKING:
    from docs2db_api.rag.engine import UniversalRAGEngine


logger = structlog.get_logger(__name__)

_engine: UniversalRAGEngine | None = None
_engine_lock = asyncio.Lock()


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

    async with _engine_lock:
        if _engine is None:
            from docs2db_api.rag.engine import RAGConfig
            from docs2db_api.rag.engine import UniversalRAGEngine

            logger.info("Initializing UniversalRAGEngine")

            db_config = {
                "host": CONFIG.db_host,
                "port": str(CONFIG.db_port),
                "database": CONFIG.db_database,
                "user": CONFIG.db_user,
                "password": CONFIG.db_password,
            }

            rag_config = RAGConfig()
            rag_config.similarity_threshold = CONFIG.rag_similarity_threshold
            rag_config.max_chunks = CONFIG.rag_max_chunks
            rag_config.enable_reranking = CONFIG.rag_enable_reranking
            rag_config.enable_question_refinement = False

            _engine = UniversalRAGEngine(
                config=rag_config,
                db_config=db_config,
            )

            try:
                await _engine.start()
                logger.info("UniversalRAGEngine initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize RAG engine", error=str(e))
                _engine = None
                raise

    return _engine


async def shutdown_engine() -> None:
    """Shutdown the RAG engine and cleanup resources."""
    global _engine

    async with _engine_lock:
        if _engine is not None:
            logger.info("Shutting down UniversalRAGEngine")
            try:
                await _engine.close()
            finally:
                _engine = None


async def health_check() -> None:
    """Perform startup health check to verify database connectivity and functionality.

    Raises:
        Exception: If health check fails (database unreachable, query fails, etc.)
    """
    logger.info("Performing startup health check...")

    try:
        engine = await get_engine()
        logger.info("Database connection established")

        result = await engine.search_documents(
            query="test",
            max_chunks=1,
            similarity_threshold=0.0,
            enable_reranking=False,
        )

        if result is None:
            msg = "Health check query returned None"
            raise Exception(msg)

        logger.info("Test query successful", document_count=len(result.documents))
        logger.info("Health check passed - system is ready")

    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        raise Exception(f"Startup health check failed - cannot connect to database or perform queries: {e}") from e
