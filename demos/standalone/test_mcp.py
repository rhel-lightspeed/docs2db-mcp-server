#!/usr/bin/env python3
"""Standalone test script for docs2db MCP server.

This script tests the MCP server by directly invoking the search_documents tool function.
Requires a running PostgreSQL database with docs2db RAG data.
"""

import asyncio
import os
import sys


# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

# Import the engine directly instead of the decorated tool
from docs2db_mcp.engine import get_engine


async def main() -> None:
    """Run test queries against the MCP server."""
    print("=" * 80)
    print("docs2db MCP Server - Standalone Test")
    print("=" * 80)

    # Configure database connection
    os.environ.setdefault("DOCS2DB_MCP_DB_HOST", "localhost")
    os.environ.setdefault("DOCS2DB_MCP_DB_PORT", "5432")
    os.environ.setdefault("DOCS2DB_MCP_DB_DATABASE", "ragdb")
    os.environ.setdefault("DOCS2DB_MCP_DB_USER", "postgres")
    os.environ.setdefault("DOCS2DB_MCP_DB_PASSWORD", "postgres")

    # Test queries
    queries = [
        "How do I configure SELinux on RHEL?",
        "What is systemd?",
        "How to install packages with dnf?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Query: {query!r}")
        print("-" * 80)

        try:
            # Get the RAG engine and search directly
            engine = await get_engine()
            rag_result = await engine.search_documents(
                query=query,
                max_chunks=3,
                similarity_threshold=0.7,
                enable_reranking=True,
            )

            num_results = len(rag_result.documents)
            print(f"✅ Found {num_results} results\n")

            for j, doc in enumerate(rag_result.documents, 1):
                print(f"  Result {j}:")
                print(f"    Similarity: {doc['similarity_score']:.3f}")
                print(f"    Source: {doc['document_path']}")
                print(f"    Text: {doc['text'][:200]}...")
                if doc.get("metadata", {}).get("headings"):
                    print(f"    Headings: {', '.join(doc['metadata']['headings'])}")
                print()

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()

    print("=" * 80)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
