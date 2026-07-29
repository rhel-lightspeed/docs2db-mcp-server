from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

from docs2db_mcp.config import CONFIG
from docs2db_mcp.tools.search_documents import _MAX_QUERY_LENGTH


class TestSearchDocumentsInputValidation:
    """Tests for per-request parameter bounds validation (RSPEED-3383).

    Validates that the tool returns the documented JSON error dictionary
    for out-of-bounds max_chunks, similarity_threshold, and query length
    without dispatching to the RAG engine (CWE-770, CWE-20).
    """

    # -- max_chunks rejection ---------------------------------------------------

    async def test_max_chunks_above_config_limit_returns_error(self):
        from docs2db_mcp.tools.search_documents import search_documents

        result = await search_documents(query="test", max_chunks=CONFIG.rag_max_chunks + 1)
        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "max_chunks" in result["error"]

    async def test_max_chunks_zero_returns_error(self):
        from docs2db_mcp.tools.search_documents import search_documents

        result = await search_documents(query="test", max_chunks=0)
        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "max_chunks" in result["error"]

    async def test_max_chunks_negative_returns_error(self):
        from docs2db_mcp.tools.search_documents import search_documents

        result = await search_documents(query="test", max_chunks=-5)
        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "max_chunks" in result["error"]

    # -- similarity_threshold rejection -----------------------------------------

    async def test_similarity_threshold_above_one_returns_error(self):
        from docs2db_mcp.tools.search_documents import search_documents

        result = await search_documents(query="test", similarity_threshold=1.5)
        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "similarity_threshold" in result["error"]

    async def test_similarity_threshold_negative_returns_error(self):
        from docs2db_mcp.tools.search_documents import search_documents

        result = await search_documents(query="test", similarity_threshold=-0.1)
        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "similarity_threshold" in result["error"]

    # -- query length rejection -------------------------------------------------

    async def test_empty_query_returns_error(self):
        from docs2db_mcp.tools.search_documents import search_documents

        result = await search_documents(query="")
        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "query" in result["error"]

    async def test_query_exceeding_max_length_returns_error(self):
        from docs2db_mcp.tools.search_documents import search_documents

        result = await search_documents(query="x" * (_MAX_QUERY_LENGTH + 1))
        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "query" in result["error"]

    # -- accepted boundary values -----------------------------------------------

    async def test_valid_boundary_max_chunks_upper(self, mock_engine):
        """max_chunks == CONFIG.rag_max_chunks (upper bound) must reach the engine."""
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="RHEL 9", max_chunks=CONFIG.rag_max_chunks)
        assert "error" not in result
        mock_engine.search_documents.assert_awaited_once()

    async def test_valid_boundary_max_chunks_lower(self, mock_engine):
        """max_chunks == 1 (lower bound) must reach the engine."""
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="RHEL 9", max_chunks=1)
        assert "error" not in result
        mock_engine.search_documents.assert_awaited_once()

    async def test_valid_boundary_threshold_zero(self, mock_engine):
        """similarity_threshold == 0.0 (lower bound) must reach the engine."""
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="RHEL 9", similarity_threshold=0.0)
        assert "error" not in result
        mock_engine.search_documents.assert_awaited_once()

    async def test_valid_boundary_threshold_one(self, mock_engine):
        """similarity_threshold == 1.0 (upper bound) must reach the engine."""
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="RHEL 9", similarity_threshold=1.0)
        assert "error" not in result
        mock_engine.search_documents.assert_awaited_once()

    async def test_valid_boundary_query_min_length(self, mock_engine):
        """Single-character query (lower bound) must reach the engine."""
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="x")
        assert "error" not in result
        mock_engine.search_documents.assert_awaited_once()

    async def test_valid_boundary_query_max_length(self, mock_engine):
        """Query at exactly _MAX_QUERY_LENGTH (upper bound) must reach the engine."""
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="x" * _MAX_QUERY_LENGTH)
        assert "error" not in result
        mock_engine.search_documents.assert_awaited_once()


class TestSearchDocumentsSuccess:
    async def test_valid_query_returns_chunks(self, mock_engine, sample_documents):
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="RHEL 9 security features")

        assert "chunks" in result
        assert "query_used" in result
        assert "num_results" in result
        assert result["query_used"] == "RHEL 9 security features"
        assert result["num_results"] == len(sample_documents)
        assert len(result["chunks"]) == len(sample_documents)

    async def test_chunk_structure(self, mock_engine):
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="RHEL packages")

        assert result["num_results"] > 0
        chunk = result["chunks"][0]
        assert "text" in chunk
        assert "similarity" in chunk
        assert "source" in chunk
        assert "metadata" in chunk
        assert isinstance(chunk["similarity"], float)

    async def test_chunk_data_maps_correctly(self, mock_engine, sample_documents):
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="RHEL security")

        first_chunk = result["chunks"][0]
        first_doc = sample_documents[0]
        assert first_chunk["text"] == first_doc["text"]
        assert first_chunk["source"] == first_doc["document_path"]
        assert first_chunk["similarity"] == float(first_doc["similarity_score"])

    async def test_engine_called_with_correct_params(self, mock_engine):
        from docs2db_mcp.tools.search_documents import search_documents

        mock_get_engine = AsyncMock(return_value=mock_engine)
        with patch("docs2db_mcp.tools.search_documents.get_engine", new=mock_get_engine):
            await search_documents(
                query="test query",
                max_chunks=3,
                similarity_threshold=0.8,
                enable_reranking=False,
            )

        mock_engine.search_documents.assert_called_once_with(
            query="test query",
            max_chunks=3,
            similarity_threshold=0.8,
            enable_reranking=False,
        )

    async def test_default_params_forwarded(self, mock_engine):
        from docs2db_mcp.tools.search_documents import search_documents

        mock_get_engine = AsyncMock(return_value=mock_engine)
        with patch("docs2db_mcp.tools.search_documents.get_engine", new=mock_get_engine):
            await search_documents(query="test")

        mock_engine.search_documents.assert_called_once_with(
            query="test",
            max_chunks=5,
            similarity_threshold=0.7,
            enable_reranking=True,
        )

    async def test_query_used_is_original_query(self, mock_engine):
        from docs2db_mcp.tools.search_documents import search_documents

        original_query = "How to configure firewalld in RHEL?"
        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query=original_query)

        assert result["query_used"] == original_query

    async def test_multiple_chunks_order_preserved(self, mock_engine, sample_documents):
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="RHEL documentation")

        assert result["num_results"] == len(sample_documents)
        for chunk, doc in zip(result["chunks"], sample_documents, strict=True):
            assert chunk["text"] == doc["text"]


class TestSearchDocumentsEmptyResults:
    async def test_empty_results_returns_zero_chunks(self):
        from docs2db_mcp.tools.search_documents import search_documents

        empty_result = MagicMock()
        empty_result.documents = []
        mock_engine = MagicMock()
        mock_engine.search_documents = AsyncMock(return_value=empty_result)

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="nonexistent topic")

        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "error" not in result

    async def test_empty_results_preserves_query(self):
        from docs2db_mcp.tools.search_documents import search_documents

        empty_result = MagicMock()
        empty_result.documents = []
        mock_engine = MagicMock()
        mock_engine.search_documents = AsyncMock(return_value=empty_result)

        query = "obscure topic that returns nothing"
        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query=query)

        assert result["query_used"] == query


class TestSearchDocumentsErrorHandling:
    async def test_connection_error_returns_error_dict(self):
        from docs2db_mcp.tools.search_documents import search_documents

        mock_get_engine = AsyncMock(side_effect=ConnectionError("Database unreachable"))
        with patch("docs2db_mcp.tools.search_documents.get_engine", new=mock_get_engine):
            result = await search_documents(query="test query")

        assert "error" in result
        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "Database unreachable" in result["error"]

    async def test_search_error_returns_error_dict(self, mock_engine):
        from docs2db_mcp.tools.search_documents import search_documents

        mock_engine.search_documents = AsyncMock(side_effect=RuntimeError("Search failed"))
        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="test query")

        assert "error" in result
        assert result["chunks"] == []
        assert result["num_results"] == 0
        assert "Search failed" in result["error"]

    async def test_error_preserves_original_query(self):
        from docs2db_mcp.tools.search_documents import search_documents

        mock_get_engine = AsyncMock(side_effect=Exception("Unexpected error"))
        original_query = "RHEL 10 features"
        with patch("docs2db_mcp.tools.search_documents.get_engine", new=mock_get_engine):
            result = await search_documents(query=original_query)

        assert result["query_used"] == original_query

    async def test_timeout_error_handled_gracefully(self):
        from docs2db_mcp.tools.search_documents import search_documents

        mock_get_engine = AsyncMock(side_effect=TimeoutError())
        with patch("docs2db_mcp.tools.search_documents.get_engine", new=mock_get_engine):
            result = await search_documents(query="slow query")

        assert "error" in result
        assert result["chunks"] == []
        assert result["num_results"] == 0

    async def test_generic_exception_handled_gracefully(self):
        from docs2db_mcp.tools.search_documents import search_documents

        mock_get_engine = AsyncMock(side_effect=Exception("Something went wrong"))
        with patch("docs2db_mcp.tools.search_documents.get_engine", new=mock_get_engine):
            result = await search_documents(query="test")

        assert "error" in result
        assert "Something went wrong" in result["error"]


class TestSearchDocumentsFieldMapping:
    async def test_optional_fields_default_to_none(self):
        from docs2db_mcp.tools.search_documents import search_documents

        minimal_doc = {
            "text": "Minimal document chunk",
            "similarity_score": 0.75,
            "document_path": "minimal.md",
        }
        mock_result = MagicMock()
        mock_result.documents = [minimal_doc]
        mock_engine = MagicMock()
        mock_engine.search_documents = AsyncMock(return_value=mock_result)

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="minimal test")

        chunk = result["chunks"][0]
        assert chunk["text"] == "Minimal document chunk"
        assert chunk["chunk_index"] is None
        assert chunk["vector_similarity"] is None
        assert chunk["rerank_score"] is None
        assert chunk["metadata"] == {}

    async def test_similarity_is_float(self, mock_engine):
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="test")

        for chunk in result["chunks"]:
            assert isinstance(chunk["similarity"], float)

    async def test_rerank_score_preserved(self, mock_engine, sample_documents):
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="test")

        assert result["chunks"][0]["rerank_score"] == sample_documents[0]["rerank_score"]

    async def test_vector_similarity_preserved(self, mock_engine, sample_documents):
        from docs2db_mcp.tools.search_documents import search_documents

        with patch("docs2db_mcp.tools.search_documents.get_engine", new=AsyncMock(return_value=mock_engine)):
            result = await search_documents(query="test")

        assert result["chunks"][0]["vector_similarity"] == sample_documents[0]["vector_similarity"]
