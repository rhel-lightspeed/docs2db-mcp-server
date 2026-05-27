"""Main entry point for docs2db MCP server."""

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
from docs2db_mcp.server import mcp  # noqa: E402


logger = logging.getLogger(__name__)


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

    try:
        mcp.run(transport=CONFIG.transport, **CONFIG.transport_kwargs)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error("Server error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
