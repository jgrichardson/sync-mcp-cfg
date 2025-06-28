# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of sync-mcp-cfg
- Support for Claude Code CLI, Claude Desktop, Cursor, and VS Code Copilot
- CLI commands: add, remove, list, sync, status, init
- Interactive command modes
- Automatic backup and restore functionality
- Cross-platform support (Windows, macOS, Linux)
- Rich terminal output with colors and tables
- Plugin-based architecture for easy extension
- Comprehensive test suite
- GitHub Actions CI/CD pipeline
- Pre-commit hooks for code quality

### Features
- **Client Support**: Manage MCP servers across 4 major AI clients
- **Synchronization**: Sync server configurations between clients
- **Backup & Restore**: Automatic backups before destructive operations
- **Validation**: Configuration format validation for all clients
- **Discovery**: Automatic detection of installed MCP clients
- **Multiple Formats**: JSON, YAML, and table output formats
- **Interactive Mode**: User-friendly prompts and confirmations
- **Dry Run**: Preview changes before applying them

### Technical Details
- Python 3.9+ support
- Type hints throughout codebase
- Pydantic models for data validation
- Click-based CLI with Rich output
- Comprehensive error handling
- Cross-platform file path handling
- Extensible plugin architecture

## [0.1.0] - 2025-01-XX

### Added
- Initial MVP release
- Core functionality for MCP server management
- Support for 4 major MCP clients
- CLI interface with essential commands
- Documentation and examples

---

**Note**: This project follows [Semantic Versioning](https://semver.org/). 
- **MAJOR** version increments for incompatible API changes
- **MINOR** version increments for backwards-compatible functionality additions  
- **PATCH** version increments for backwards-compatible bug fixes