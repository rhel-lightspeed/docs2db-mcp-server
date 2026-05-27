"""Main entry point for docs2db MCP server."""

import logging
import os
import sys

import structlog


# Must read transport before importing modules that configure logging
transport = os.environ.get("DOCS2DB_MCP_TRANSPORT", "sse")

if transport == "sse":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
else:
    # stdout is reserved for MCP protocol, must redirect all logging to stderr
    os.environ.setdefault("DOCS2DB_LOG_LEVEL", "CRITICAL")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

# Import configuration (lightweight, doesn't trigger heavy imports)
from docs2db_mcp.config import CONFIG  # noqa: E402
from docs2db_mcp.server import mcp  # noqa: E402


logger = structlog.get_logger(__name__)


def main() -> None:
    """Run the MCP server."""
    logger.info(
        "Starting docs2db MCP server",
        host=CONFIG.host,
        port=CONFIG.port,
        transport=CONFIG.transport,
        database=f"{CONFIG.db_host}:{CONFIG.db_port}/{CONFIG.db_database}",
        rag_threshold=CONFIG.rag_similarity_threshold,
        rag_max_chunks=CONFIG.rag_max_chunks,
        rag_reranking=CONFIG.rag_enable_reranking,
    )

    try:
        mcp.run(transport=CONFIG.transport, **CONFIG.transport_kwargs)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error("Server error", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
