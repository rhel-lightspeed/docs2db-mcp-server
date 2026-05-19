"""Pytest fixtures and configuration for docs2db-mcp-server tests."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

# Import server first to ensure proper tool registration order
# (resolves the circular import between server.py and tools/search_documents.py)
from docs2db_mcp.server import mcp  # noqa: F401


@pytest.fixture
def sample_documents():
    return [
        {
            "text": "RHEL 9 introduces new security features including enhanced SELinux policies.",
            "document_path": "rhel9/security-guide.md",
            "similarity_score": 0.92,
            "metadata": {"version": "9.0", "section": "security"},
            "chunk_index": 0,
            "vector_similarity": 0.91,
            "rerank_score": 0.95,
        },
        {
            "text": "Package management with dnf in RHEL 9 provides improved dependency resolution.",
            "document_path": "rhel9/package-management.md",
            "similarity_score": 0.85,
            "metadata": {"version": "9.0", "section": "packages"},
            "chunk_index": 2,
            "vector_similarity": 0.84,
            "rerank_score": 0.88,
        },
    ]


@pytest.fixture
def mock_rag_result(sample_documents):
    result = MagicMock(spec_set=["documents"])
    result.documents = sample_documents
    return result


@pytest.fixture
def mock_engine(mock_rag_result):
    engine = MagicMock(spec_set=["search_documents"])
    engine.search_documents = AsyncMock(return_value=mock_rag_result)
    return engine
