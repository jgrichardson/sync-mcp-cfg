# AGENTS.md

Development guidelines for agentic coding agents working on sync-mcp-cfg.

## Build/Test Commands
- Install: `pip install -e .` or `make install`
- Dev setup: `pip install -e ".[dev]"` or `make install-dev`
- Run tests: `pytest` or `make test`
- Run single test: `pytest tests/test_models.py::TestMCPServer::test_create_basic_server`
- Test with coverage: `pytest --cov=src/sync_mcp_cfg` or `make test-cov`
- Lint: `ruff check src/ tests/` or `make lint`
- Format: `black src/ tests/` or `make format`
- Type check: `mypy src/` or `make type-check`
- All quality checks: `make quality`

## Code Style
- Python 3.9+ with full type hints (`typing` imports)
- Black formatting (88-char line length, skip string normalization)
- Ruff linting (E, W, F, I, B, C4, UP rules)
- Pydantic models for validation with descriptive Field() descriptions
- Rich for terminal output, Click for CLI
- Import order: stdlib, third-party, local (`from ...core` relative imports)
- Docstrings: Triple quotes with brief description
- Error handling: Custom exceptions in `core.exceptions`, user-friendly Rich messages
- Naming: snake_case for functions/vars, PascalCase for classes, UPPER_CASE for constants