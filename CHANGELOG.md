# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-16

### Added
- Initial implementation of MCP server for docs2db-api
- `search_documents` tool with hybrid search (vector + BM25)
- SSE (Server-Sent Events) transport for MCP protocol
- Environment-based configuration via pydantic-settings
- Cross-encoder reranking support for improved relevance
- Docker/Podman containerization with health checks
- Comprehensive README with usage examples
- Support for llama-stack, Goose, and Claude Desktop
- Non-root container user for security
- Configurable similarity thresholds and result limits

### Changed
- Improved `search_documents` tool description to emphasize RHEL-specific use cases
- Tool description now highlights when to use this tool (RHEL version-specific features, release notes, etc.)

### Fixed
- Containerfile installation order (copy source before pip install to avoid module not found errors)

### Dependencies
- fastmcp >=2.14.4, <3
- mcp >=1.9.3
- docs2db-api
- pydantic >=2.12.5
- pydantic-settings >=2.12.0

[Unreleased]: https://github.com/rhel-lightspeed/docs2db-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/rhel-lightspeed/docs2db-mcp-server/releases/tag/v0.1.0
