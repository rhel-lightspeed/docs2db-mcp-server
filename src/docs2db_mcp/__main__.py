"""Main entry point for docs2db MCP server."""

import asyncio
import logging
import os
import sys


# Must read transport before importing modules that configure logging
transport = os.environ.get("DOCS2DB_MCP_TRANSPORT", "sse")

if transport == "sse":
    # stdout not used by MCP protocol, logging can go there
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
else:
    # stdout is reserved for MCP protocol, must redirect all logging to stderr
    # set CRITICAL level before importing docs2db-api to minimize startup logs
    os.environ.setdefault("DOCS2DB_LOG_LEVEL", "CRITICAL")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

# Import configuration (lightweight, doesn't trigger heavy imports)
from docs2db_mcp.config import CONFIG  # noqa: E402


logger = logging.getLogger(__name__)


def _configure_structlog_for_stdio() -> None:
    """Override docs2db-api's structlog configuration to redirect stdout to stderr.

    docs2db-api configures structlog at import time to write to stdout, but stdio transport
    requires stdout to be reserved exclusively for MCP protocol messages.
    """
    import structlog

    # Reconfigure structlog to output to stderr instead of stdout
    # Keep existing processors, just redirect the output stream
    structlog.configure(
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=False,
    )


# Import server and engine modules
# Must happen after reading transport to configure structlog before they import docs2db-api
from docs2db_mcp.engine import health_check  # noqa: E402
from docs2db_mcp.engine import shutdown_engine  # noqa: E402
from docs2db_mcp.server import mcp  # noqa: E402


# docs2db-api has already configured structlog, now override for stdio transport
if transport != "sse":
    _configure_structlog_for_stdio()


async def cleanup() -> None:
    """Cleanup resources on shutdown."""
    logger.info("Shutting down docs2db MCP server")
    await shutdown_engine()


def main() -> None:
    """Run the MCP server."""
    logger.info("Starting docs2db MCP server on %s:%s", CONFIG.host, CONFIG.port)
    logger.info("Transport: %s", CONFIG.transport)
    logger.info("Database: %s:%s/%s", CONFIG.db_host, CONFIG.db_port, CONFIG.db_database)
    logger.info(
        "RAG settings: threshold=%s, max_chunks=%s, reranking=%s",
        CONFIG.rag_similarity_threshold,
        CONFIG.rag_max_chunks,
        CONFIG.rag_enable_reranking,
    )

    # Perform startup health check
    try:
        asyncio.run(health_check())
    except Exception as e:
        logger.error("Startup health check failed: %s", e)
        logger.error("Server will not start - please check database connection and configuration")
        sys.exit(1)

    try:
        # Run the MCP server
        mcp.run(transport=CONFIG.transport, **CONFIG.transport_kwargs)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error("Server error: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        asyncio.run(cleanup())


if __name__ == "__main__":
    main()
