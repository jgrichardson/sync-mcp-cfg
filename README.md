# Sync MCP Config

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A powerful tool to manage and synchronize Model Context Protocol (MCP) server configurations across multiple AI clients.

## 🚀 Features

- **Multi-Client Support**: Manage MCP servers across Claude Code, Claude Desktop, Cursor, and VS Code
- **Easy Synchronization**: Sync server configurations between different clients with conflict resolution
- **Backup & Restore**: Automatic backups before changes with restore capability
- **Interactive CLI**: User-friendly command-line interface with rich output and progress indicators
- **Text-based UI**: Optional TUI for visual management
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Extensible**: Plugin-based architecture for easy addition of new clients
- **Safe Operations**: Built-in validation and dry-run capabilities

## 📦 Installation

### From Source (Current Method)

```bash
git clone https://github.com/jgrichardson/sync-mcp-cfg.git
cd sync-mcp-cfg
pip install -e .
```

> **Note**: This tool is actively developed and tested. PyPI package distribution is planned for the future.

### Requirements

- Python 3.9 or higher
- One or more supported MCP clients installed (Claude Code, Claude Desktop, Cursor, or VS Code)

### Development Installation

```bash
git clone https://github.com/jgrichardson/sync-mcp-cfg.git
cd sync-mcp-cfg
pip install -e ".[dev]"
```

## 🛠️ Supported Clients

| Client | Status | Configuration Location |
|--------|--------|------------------------|
| **Claude Code CLI** | ✅ | `~/.claude.json` |
| **Claude Desktop** | ✅ | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)<br>`%APPDATA%/Claude/claude_desktop_config.json` (Windows) |
| **Cursor** | ✅ | `~/.cursor/mcp.json` |
| **VS Code Copilot** | ✅ | `.vscode/mcp.json` |

## 🚀 Quick Start

### 1. Initialize Configuration

```bash
sync-mcp-cfg init
```

### 2. Check Client Status

```bash
sync-mcp-cfg status
```

### 3. Add an MCP Server

```bash
# Add a filesystem server
sync-mcp-cfg add filesystem npx \
  --args "-y" \
  --args "@modelcontextprotocol/server-filesystem" \
  --args "/path/to/directory" \
  --clients claude-code --clients cursor

# Add with environment variables
sync-mcp-cfg add weather-api node \
  --args "/path/to/weather-server.js" \
  --env "API_KEY=your-key-here" \
  --description "Weather information server"
```

### 4. List Configured Servers

```bash
# List all servers
sync-mcp-cfg list

# List servers for specific client
sync-mcp-cfg list --client claude-code

# Detailed view
sync-mcp-cfg list --detailed
```

### 5. Sync Between Clients

```bash
# Sync all servers from Claude Code to Cursor
sync-mcp-cfg sync --from claude-code --to cursor

# Sync specific servers
sync-mcp-cfg sync --from claude-desktop --to claude-code --to vscode \
  --servers filesystem --servers weather-api

# Dry run to see what would be synced
sync-mcp-cfg sync --from cursor --dry-run
```

### 6. Remove Servers

```bash
# Remove from specific clients
sync-mcp-cfg remove filesystem --clients claude-code

# Remove from all clients
sync-mcp-cfg remove weather-api --force
```

## 📋 Usage Examples

### Adding Popular MCP Servers

```bash
# Filesystem server
sync-mcp-cfg add filesystem npx \
  -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/Users/username/Documents"

# Sequential thinking server
sync-mcp-cfg add sequential-thinking npx \
  -a "-y" -a "@modelcontextprotocol/server-sequential-thinking"

# GitHub server
sync-mcp-cfg add github npx \
  -a "-y" -a "@modelcontextprotocol/server-github" \
  -e "GITHUB_PERSONAL_ACCESS_TOKEN=your-token"

# Brave search server
sync-mcp-cfg add brave-search npx \
  -a "-y" -a "@modelcontextprotocol/server-brave-search" \
  -e "BRAVE_API_KEY=your-key"
```

### Batch Operations

```bash
# Sync all servers from one client to multiple others
sync-mcp-cfg sync --from claude-desktop --to claude-code --to cursor --to vscode

# List servers in JSON format for scripting
sync-mcp-cfg list --format json > mcp-servers.json

# Add server to all available clients
sync-mcp-cfg add universal-server npx -a "-y" -a "some-mcp-server"
```

## 🎨 Text-based UI

Launch the interactive TUI for visual management:

```bash
sync-mcp-cfg tui
```

The TUI provides:
- Visual overview of all clients and servers
- Interactive server addition and removal
- Drag-and-drop style synchronization
- Real-time status updates

## 🔧 Configuration

### Global Configuration

The tool stores its configuration in:
- **Linux/macOS**: `~/.config/sync-mcp-cfg/config.json`
- **Windows**: `%APPDATA%/sync-mcp-cfg/config.json`

### Configuration Options

```json
{
  "auto_backup": true,
  "backup_retention_days": 30,
  "validate_servers": true,
  "default_sync_target": ["claude-code", "cursor"]
}
```

## 🛡️ Backup and Recovery

### Automatic Backups

Backups are created automatically before any destructive operation:

```bash
# View backup location
sync-mcp-cfg status --verbose

# Manual backup
sync-mcp-cfg backup --client claude-code

# Restore from backup
sync-mcp-cfg restore --client claude-code --backup /path/to/backup.json
```

### Backup Locations

- **Claude Code**: `~/.claude/backups/`
- **Claude Desktop**: `~/Library/Application Support/Claude/backups/` (macOS)
- **Cursor**: `~/.cursor/backups/`
- **VS Code**: `.vscode/backups/`

## 🔌 Extending Support

### Adding New Clients

The tool uses a plugin-based architecture. To add support for a new MCP client:

1. Create a new handler in `src/sync_mcp_cfg/clients/`
2. Extend the `BaseClientHandler` class
3. Implement the required methods
4. Register the handler in `__init__.py`

Example:

```python
from .base import BaseClientHandler
from ..core.models import MCPServer

class NewClientHandler(BaseClientHandler):
    def load_servers(self) -> List[MCPServer]:
        # Implementation for loading servers
        pass
    
    def save_servers(self, servers: List[MCPServer]) -> None:
        # Implementation for saving servers
        pass
```

## 🧪 Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff src/ tests/

# Type checking
mypy src/
```

### Building Documentation

```bash
mkdocs serve
```

## Why This Tool?

If you use multiple AI clients with MCP servers, this tool helps with:
- Keeping server configurations synchronized across clients
- Avoiding manual copy/paste errors when setting up servers
- Creating backups before making changes
- Managing servers from a single command-line interface

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/jgrichardson/sync-mcp-cfg.git
cd sync-mcp-cfg
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## 📚 Command Reference

### Global Options

- `--verbose, -v`: Enable verbose output
- `--no-color`: Disable colored output
- `--help`: Show help message

### Commands

- `init`: Initialize configuration
- `status`: Show client status
- `add`: Add MCP server
- `remove`: Remove MCP server
- `list`: List MCP servers
- `sync`: Sync servers between clients
- `tui`: Launch text-based UI

For detailed command help:
```bash
sync-mcp-cfg COMMAND --help
```

## 🐛 Troubleshooting

### Common Issues

1. **Client not detected**: Ensure the client is installed and configuration directory exists
2. **Permission errors**: Check file permissions on configuration directories
3. **Sync conflicts**: Use `--overwrite` flag or resolve conflicts manually
4. **Backup failures**: Ensure sufficient disk space and write permissions

### Debug Mode

```bash
sync-mcp-cfg --verbose COMMAND
```

### Log Files

Logs are written to:
- **Linux/macOS**: `~/.local/share/sync-mcp-cfg/logs/`
- **Windows**: `%LOCALAPPDATA%/sync-mcp-cfg/logs/`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - The standard this tool supports
- [Anthropic](https://anthropic.com/) - For Claude and the MCP specification
- [Rich](https://github.com/Textualize/rich) - For beautiful terminal output
- [Click](https://click.palletsprojects.com/) - For the CLI framework

## 📞 Support

- 🐛 [Report Bugs](https://github.com/jgrichardson/sync-mcp-cfg/issues)
- 💡 [Request Features](https://github.com/jgrichardson/sync-mcp-cfg/issues)
- 📖 [Documentation](https://github.com/jgrichardson/sync-mcp-cfg/wiki)
- 💬 [Discussions](https://github.com/jgrichardson/sync-mcp-cfg/discussions)

---

**Made with ❤️ for the AI development community**