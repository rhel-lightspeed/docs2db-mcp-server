"""RAG engine singleton wrapper."""

import logging
from typing import Optional

from docs2db_api.rag.engine import RAGConfig, UniversalRAGEngine

from docs2db_mcp.config import CONFIG

logger = logging.getLogger(__name__)

_engine: Optional[UniversalRAGEngine] = None


async def get_engine() -> UniversalRAGEngine:
    """Get or create the singleton RAG engine instance.

    Returns:
        Initialized UniversalRAGEngine instance

    Raises:
        Exception: If engine initialization fails
    """
    global _engine

    if _engine is None:
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
            logger.error(f"Failed to initialize RAG engine: {e}")
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
