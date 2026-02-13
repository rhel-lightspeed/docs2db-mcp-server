# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of MCP server for docs2db-api
- `search_documents` tool with hybrid search support
- SSE (Server-Sent Events) transport for MCP protocol
- Environment-based configuration
- Cross-encoder reranking support
- Docker/Podman containerization
- Comprehensive README with usage examples
- Support for llama-stack, Goose, and Claude Desktop
- Health check endpoint

### Dependencies
- fastmcp >=2.14.4, <3
- mcp >=1.9.3
- docs2db-api
- pydantic >=2.12.5
- pydantic-settings >=2.12.0

## [0.1.0] - YYYY-MM-DD

### Added
- First public release
- MCP protocol support via FastMCP
- Integration with docs2db-api's UniversalRAGEngine
- Configurable similarity thresholds and result limits
- Production-ready containerization
- Non-root container user for security
- Comprehensive documentation

[Unreleased]: https://github.com/rhel-lightspeed/docs2db-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/rhel-lightspeed/docs2db-mcp-server/releases/tag/v0.1.0
