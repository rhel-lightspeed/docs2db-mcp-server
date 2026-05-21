# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- GitHub Actions CI workflow (lint + test jobs, no postgres service)
- OpenSSF Scorecard workflow
- Pre-commit hooks (ruff, pyright, gitleaks, check-toml, end-of-file-fixer, trailing-whitespace)
- CodeRabbit configuration (`.coderabbit.yaml`)
- `AGENTS.md` knowledge base for AI agents (supersedes `CLAUDE.md`)
- `Makefile` with `test`, `test-ci`, `lint`, `format`, `typecheck`, `clean`, `help` targets
- `SECURITY.md` vulnerability reporting policy
- `CONTRIBUTING.md` developer guide for the MCP server
- GitHub pull request template
- OpenSSF Scorecard workflow
- `renovate.json` dependency update configuration
- `.python-version` file pinned to `3.12`

### Changed

- CI workflow: extended ruff check and format to cover `src/`, `tests/`, and `demos/`
- Makefile: `lint` target now runs `ruff check --fix` (was `ruff check`)
- pytest: added `--cov=docs2db_mcp --cov-report=term-missing` to default options
- Type checker: mypy → pyright (`uv run pyright src/docs2db_mcp/`)
- Dev dependencies: moved from `[project.optional-dependencies]` to `[dependency-groups]`
- `requires-python` tightened from `>=3.12` to `>=3.12,<3.14`

### Removed

- `CLAUDE.md` (superseded by `AGENTS.md`)

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
