"""FastMCP server instance and initialization."""

import logging

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    "docs2db-rag",
    instructions=(
        "RAG search using docs2db for RHEL documentation. "
        "Use search_documents to find relevant information from "
        "RHEL documentation, knowledge base articles, and guides."
    ),
)

# Import tools to register them with the MCP server
# This must happen after mcp instance is created
from docs2db_mcp.tools import search_documents  # noqa: F401, E402

logger.info("MCP server 'docs2db-rag' initialized")
