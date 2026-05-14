import asyncio


class TestImports:
    def test_docs2db_mcp_package(self):
        import docs2db_mcp

        assert docs2db_mcp is not None

    def test_version_defined(self):
        import docs2db_mcp

        assert docs2db_mcp.__version__ == "0.1.0"

    def test_server_module(self):
        from docs2db_mcp import server

        assert server is not None

    def test_mcp_instance_exists(self):
        from docs2db_mcp.server import mcp

        assert mcp is not None

    def test_config_module(self):
        from docs2db_mcp.config import CONFIG
        from docs2db_mcp.config import Config

        assert Config is not None
        assert CONFIG is not None

    def test_engine_module(self):
        from docs2db_mcp import engine

        assert engine is not None

    def test_get_engine_is_async(self):
        from docs2db_mcp.engine import get_engine

        assert asyncio.iscoroutinefunction(get_engine)

    def test_shutdown_engine_is_async(self):
        from docs2db_mcp.engine import shutdown_engine

        assert asyncio.iscoroutinefunction(shutdown_engine)

    def test_search_documents_tool_exists(self):
        from fastmcp.tools.tool import FunctionTool

        from docs2db_mcp.tools import search_documents

        assert isinstance(search_documents, FunctionTool)
        assert search_documents.name == "search_documents"

    def test_search_documents_fn_is_async(self):
        from docs2db_mcp.tools import search_documents

        assert asyncio.iscoroutinefunction(search_documents.fn)


class TestConfigDefaults:
    def test_transport_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.transport == "sse"

    def test_host_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.host == "0.0.0.0"

    def test_port_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.port == 8002

    def test_db_host_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.db_host == "localhost"

    def test_db_port_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.db_port == 5432

    def test_db_database_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.db_database == "ragdb"

    def test_db_user_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.db_user == "postgres"

    def test_rag_similarity_threshold_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.rag_similarity_threshold == 0.7

    def test_rag_max_chunks_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.rag_max_chunks == 5

    def test_rag_enable_reranking_default(self):
        from docs2db_mcp.config import CONFIG

        assert CONFIG.rag_enable_reranking is True

    def test_database_url_format(self):
        from docs2db_mcp.config import CONFIG

        url = CONFIG.database_url
        assert url.startswith("postgresql://")
        assert CONFIG.db_host in url
        assert CONFIG.db_database in url

    def test_config_reads_env_vars(self, monkeypatch):
        monkeypatch.setenv("DOCS2DB_MCP_DB_HOST", "test-host")
        monkeypatch.setenv("DOCS2DB_MCP_DB_PORT", "5433")

        from docs2db_mcp.config import Config

        config = Config()
        assert config.db_host == "test-host"
        assert config.db_port == 5433

    def test_config_env_prefix(self, monkeypatch):
        monkeypatch.setenv("DOCS2DB_MCP_RAG_MAX_CHUNKS", "20")

        from docs2db_mcp.config import Config

        config = Config()
        assert config.rag_max_chunks == 20


class TestMCPServer:
    def test_mcp_server_is_configured(self):
        from docs2db_mcp.server import mcp

        assert mcp is not None

    def test_search_documents_registered(self):
        from fastmcp.tools.tool import FunctionTool

        from docs2db_mcp.tools import search_documents

        assert isinstance(search_documents, FunctionTool)
        assert search_documents.name == "search_documents"
        assert search_documents.enabled
