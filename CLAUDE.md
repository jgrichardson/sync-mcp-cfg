# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sync MCP Config is a Python CLI tool for managing and synchronizing Model Context Protocol (MCP) server configurations across multiple AI clients (Claude Code, Claude Desktop, Cursor, VS Code Copilot).

## Build/Run/Test Commands

- Install dependencies: `pip install -e .`
- Install dev dependencies: `pip install -e ".[dev]"`
- Run CLI: `sync-mcp-cfg --help` or `python -m sync_mcp_cfg.cli.main`
- Run tests: `pytest`
- Run tests with coverage: `pytest --cov=src/sync_mcp_cfg`
- Format code: `black src/ tests/`
- Lint code: `ruff src/ tests/`
- Type check: `mypy src/`
- Run all checks: `pre-commit run --all-files`

## Code Architecture

### Core Architecture
- **Plugin-based design**: Each MCP client has its own handler that implements `BaseClientHandler`
- **Data models**: Pydantic models for type safety and validation (`core/models.py`)
- **Client registry**: Automatic discovery of available MCP clients (`core/registry.py`)
- **Layered CLI**: Click-based CLI with rich output and interactive prompts

### Key Directories
- `src/sync_mcp_cfg/core/`: Core models, exceptions, and client registry
- `src/sync_mcp_cfg/clients/`: Client-specific handlers for each MCP client
- `src/sync_mcp_cfg/cli/`: Command-line interface and commands
- `src/sync_mcp_cfg/tui/`: Text-based user interface (Textual)
- `src/sync_mcp_cfg/utils/`: Utility functions for config, backup, validation

### Client Handler Pattern
Each client handler must implement:
- `load_servers()`: Load MCP servers from client config
- `save_servers()`: Save MCP servers to client config  
- `add_server()`, `remove_server()`, `get_server()`: Server management
- `validate_config()`: Validate configuration format
- `backup_config()`, `restore_config()`: Backup/restore functionality

### Configuration Formats
- **Claude Code/Desktop**: JSON with `mcpServers` object
- **Cursor**: JSON with `servers` array and `version` field
- **VS Code**: JSON with `servers` object and optional `inputs` array

## Development Guidelines

### Code Style
- Python 3.9+ with type hints
- Black for formatting (88 char line length)
- Ruff for linting
- Pydantic for data validation
- Rich for terminal output
- Click for CLI framework

### Error Handling
- Custom exception hierarchy in `core/exceptions.py`
- Graceful degradation when clients aren't available
- User-friendly error messages with Rich formatting
- Automatic backups before destructive operations

### Testing Strategy  
- Unit tests for core models and client handlers
- Integration tests for CLI commands
- Mock client configurations for testing
- Parametrized tests for multiple client types

### CLI Design Principles
- Consistent command structure: `sync-mcp-cfg VERB NOUN`
- Rich help text and error messages
- Interactive prompts with sensible defaults
- Dry-run support for destructive operations
- Verbose mode for debugging

## Client-Specific Notes

### Claude Code CLI
- Config: `~/.claude.json` (primary), `~/.claude/settings.json` (fallback)
- Format: Standard MCP format with `mcpServers` object
- Auto-discovery: Check for config files or `.claude` directory

### Claude Desktop  
- Config locations vary by platform (macOS: `~/Library/Application Support/Claude/`)
- Same format as Claude Code CLI
- Discovery: Check app installation paths and config existence

### Cursor
- Config: `~/.cursor/mcp.json` (global), `.cursor/mcp.json` (project)
- Format: Custom format with `servers` array and `version` field
- Special handling: Commands include arguments as single string

### VS Code Copilot
- Config: `.vscode/mcp.json` (workspace-specific)
- Format: Advanced format with `inputs` for secure prompts
- Discovery: Check for VS Code installation via `code` command

## Common Patterns

### Adding New Client Support
1. Create handler class extending `BaseClientHandler`
2. Implement required abstract methods
3. Add client type to `ClientType` enum
4. Register handler in `clients/__init__.py`
5. Add discovery logic to `ClientRegistry`

### Configuration Validation
- Validate JSON structure before parsing
- Check required fields for each client format
- Graceful error handling for malformed configs
- Schema validation using Pydantic models

### Backup Strategy
- Automatic backups before any configuration changes
- Timestamped backup files in client-specific directories
- Configurable retention period (default 30 days)
- Validation of backup files before restore

## Dependencies

### Core Dependencies
- `click`: CLI framework
- `rich`: Terminal output formatting
- `pydantic`: Data validation and models
- `platformdirs`: Cross-platform directory paths
- `textual`: Text-based UI framework

### Development Dependencies
- `pytest`: Testing framework
- `black`: Code formatting
- `ruff`: Fast Python linter
- `mypy`: Static type checking
- `pre-commit`: Git hooks for code quality

## Important Implementation Details

### Error Recovery
- Validate operations before execution
- Create backups before destructive changes
- Rollback capability on partial failures
- Clear error messages with suggested fixes

### Cross-Platform Support
- Use `pathlib.Path` for all file operations
- Platform-specific config discovery
- Handle permission differences across systems
- Respect platform-specific config conventions

### Performance Considerations
- Lazy loading of client configurations
- Minimal file I/O operations
- Efficient server discovery and validation
- Concurrent operations where possible