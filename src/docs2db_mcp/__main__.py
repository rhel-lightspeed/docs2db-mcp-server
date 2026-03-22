"""Main entry point for docs2db MCP server."""

import asyncio
import logging
import sys

from docs2db_mcp.config import CONFIG
from docs2db_mcp.engine import health_check, shutdown_engine
from docs2db_mcp.server import mcp

# Configure logging
logging.basicConfig(
    level=getattr(logging, CONFIG.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)


async def cleanup() -> None:
    """Cleanup resources on shutdown."""
    logger.info("Shutting down docs2db MCP server")
    await shutdown_engine()


def main() -> None:
    """Run the MCP server."""
    logger.info(f"Starting docs2db MCP server on {CONFIG.host}:{CONFIG.port}")
    logger.info(f"Transport: {CONFIG.transport}")
    logger.info(f"Database: {CONFIG.db_host}:{CONFIG.db_port}/{CONFIG.db_database}")
    logger.info(f"RAG settings: threshold={CONFIG.rag_similarity_threshold}, "
                f"max_chunks={CONFIG.rag_max_chunks}, "
                f"reranking={CONFIG.rag_enable_reranking}")

    # Perform startup health check
    try:
        asyncio.run(health_check())
    except Exception as e:
        logger.error(f"Startup health check failed: {e}")
        logger.error("Server will not start - please check database connection and configuration")
        sys.exit(1)

    try:
        # Run the MCP server
        mcp.run(transport=CONFIG.transport, **CONFIG.transport_kwargs)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        asyncio.run(cleanup())


if __name__ == "__main__":
    main()
