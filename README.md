# Sync MCP Config

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A powerful tool to manage and synchronize Model Context Protocol (MCP) server configurations across multiple AI clients.

## 🚀 Features

- **Multi-Client Support**: Manage MCP servers across Claude Code, Claude Desktop, Cursor, VS Code, **Gemini CLI**, and **OpenCode**
- **Easy Synchronization**: Sync server configurations between different clients with conflict resolution
- **Backup & Restore**: Automatic backups before changes with restore capability
- **Interactive CLI**: User-friendly command-line interface with rich output and progress indicators
- **Text-based UI**: Optional TUI for visual management
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Extensible**: Plugin-based architecture for easy addition of new clients
- **Safe Operations**: Built-in validation and dry-run capabilities
- **Security Hardened**: Protected against accidental exposure of sensitive data
- **Auto-Detection**: Automatically discovers client configurations in standard locations

## 📦 Installation

### From Source (Current Method)

```bash
git clone https://github.com/gilberth/sync-mcp-cfg.git
cd sync-mcp-cfg
pip install -e .
```

> **Note**: This tool is actively developed and tested. PyPI package distribution is planned for the future.

### Requirements

- Python 3.9 or higher
- One or more supported MCP clients installed (Claude Code, Claude Desktop, Cursor, VS Code, Gemini CLI, or OpenCode)

### Development Installation

```bash
git clone https://github.com/gilberth/sync-mcp-cfg.git
cd sync-mcp-cfg
pip install -e ".[dev]"
```

## 🛠️ Supported Clients

| Client              | Status | Configuration Location                                                                                                                                                                        |
| ------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Claude Code CLI** | ✅     | `~/.claude.json`                                                                                                                                                                              |
| **Claude Desktop**  | ✅     | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)<br>`%APPDATA%/Claude/claude_desktop_config.json` (Windows)<br>`~/.config/Claude/claude_desktop_config.json` (Linux) |
| **Cursor**          | ✅     | `~/.cursor/mcp.json`                                                                                                                                                                          |
| **VS Code Copilot** | ✅     | `~/Library/Application Support/Code/User/settings.json` (macOS)<br>`%APPDATA%/Code/User/settings.json` (Windows)<br>`~/.config/Code/User/settings.json` (Linux)                               |
| **Gemini CLI**      | ✅     | `~/.gemini/settings.json` (global)<br>`.gemini/settings.json` (local)                                                                                                                         |
| **OpenCode**        | ✅     | `~/.config/opencode/config.json` (global)<br>`./opencode.json` (project)                                                                                                                      |

## 🌟 Gemini CLI Support

This tool now includes **complete support for Gemini CLI** with all its specific features:

### Key Features

- **Auto-detection**: Automatically finds Gemini CLI configuration in global (`~/.gemini/settings.json`) or local (`.gemini/settings.json`) locations
- **Trust control**: Supports the `trust` field for automatic tool execution approval
- **Working directory**: Supports `cwd` field for stdio servers
- **Timeout configuration**: Configurable timeout values (default: 600,000ms)
- **HTTP URLs**: Special support for `httpUrl` field for HTTP servers (different from SSE `url`)
- **Integrated settings**: Manages MCP servers as part of Gemini CLI's main settings.json

### Gemini CLI Specific Examples

```bash
# List only Gemini CLI servers
sync-mcp-cfg list --client gemini-cli

# Sync from Claude Desktop to Gemini CLI with backup
sync-mcp-cfg sync --from claude-desktop --to gemini-cli --backup

# Add server specifically for Gemini CLI
sync-mcp-cfg add gemini-fs npx \
  -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/tmp" \
  --clients gemini-cli \
  --description "Filesystem server for Gemini CLI"
```

For complete Gemini CLI documentation, see: [docs/gemini-cli-example.md](docs/gemini-cli-example.md)

## 🔥 OpenCode Support

This tool now includes **complete support for OpenCode** - the AI coding agent built for the terminal!

### Key Features

- **Auto-detection**: Automatically finds OpenCode configuration in global (`~/.config/opencode/config.json`) or project (`./opencode.json`) locations
- **Local & Remote servers**: Full support for both stdio local servers and remote SSE/HTTP servers
- **Native format**: Uses OpenCode's native configuration format with `type: "local"` and `type: "remote"`
- **Schema validation**: Maintains proper `$schema` reference to OpenCode's configuration schema
- **Environment variables**: Complete support for environment variable configuration in local servers
- **Bidirectional sync**: Seamlessly sync servers TO and FROM OpenCode with all other clients

### OpenCode Configuration Format

OpenCode uses a unique configuration format that distinguishes between local and remote servers:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "filesystem": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path"
      ],
      "environment": { "PATH_ROOT": "/workspace" },
      "enabled": true
    },
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.ai/v1",
      "enabled": true
    }
  }
}
```

### OpenCode Specific Examples

```bash
# List only OpenCode servers
sync-mcp-cfg list --client opencode

# Sync from VS Code to OpenCode
sync-mcp-cfg sync --from vscode --to opencode

# Add local server specifically for OpenCode
sync-mcp-cfg add opencode-fs npx \
  -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/tmp" \
  --clients opencode \
  --description "Filesystem server for OpenCode"

# Add remote SSE server to OpenCode
sync-mcp-cfg add context7 "" \
  --type sse --url "https://mcp.context7.ai/v1" \
  --clients opencode \
  --description "Context7 remote MCP server"

# Sync FROM OpenCode to other clients
sync-mcp-cfg sync --from opencode --to claude-desktop --to cursor
```

### OpenCode Server Types

| sync-mcp-cfg Type | OpenCode Format                       | Use Case               |
| ----------------- | ------------------------------------- | ---------------------- |
| `stdio`           | `{"type": "local", "command": [...]}` | Local NPX/Node servers |
| `sse`             | `{"type": "remote", "url": "..."}`    | Remote SSE endpoints   |
| `http`            | `{"type": "remote", "url": "..."}`    | Remote HTTP endpoints  |

**Note**: OpenCode doesn't distinguish between SSE and HTTP in configuration - both use `type: "remote"` with a URL. The protocol is determined by the endpoint.

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

# Add Gemini CLI specific server with trust and timeout
sync-mcp-cfg add gemini-server npx \
  --args "-y" \
  --args "@modelcontextprotocol/server-filesystem" \
  --args "/tmp" \
  --clients gemini-cli \
  --description "Filesystem server for Gemini CLI"
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

# Sync between multiple clients including Gemini CLI and OpenCode
sync-mcp-cfg sync --from claude-desktop --to gemini-cli --to opencode --backup

# Sync specific servers
sync-mcp-cfg sync --from claude-desktop --to claude-code --to vscode --to gemini-cli --to opencode \
  --servers filesystem --servers weather-api

# Dry run to see what would be synced
sync-mcp-cfg sync --from cursor --to opencode --dry-run
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

# Gemini CLI specific server with trust and timeout settings
sync-mcp-cfg add gemini-filesystem npx \
  -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/path/to/files" \
  --clients gemini-cli \
  --description "Trusted filesystem server for Gemini CLI"
```

### Batch Operations

```bash
# Sync all servers from one client to multiple others including Gemini CLI and OpenCode
sync-mcp-cfg sync --from claude-desktop --to claude-code --to cursor --to vscode --to gemini-cli --to opencode

# List servers in JSON format for scripting
sync-mcp-cfg list --format json > mcp-servers.json

# Add server to all available clients
sync-mcp-cfg add universal-server npx -a "-y" -a "some-mcp-server"

# Sync with backup and overwrite protection for OpenCode
sync-mcp-cfg sync --from vscode --to opencode --backup --overwrite
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
- **VS Code**: Global settings backup with the settings.json file
- **Gemini CLI**: `~/.gemini/backups/` (global) or `.gemini/backups/` (local)
- **OpenCode**: `~/.config/opencode/backups/` (global) or `./backups/` (project)

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
git clone https://github.com/gilberth/sync-mcp-cfg.git
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

## 🔒 Security & Privacy

This tool is designed with security in mind:

- **No sensitive data collection**: Personal credentials, API keys, and private paths are never included in the codebase
- **Sanitized examples**: All documentation uses generic, non-personal example data
- **Protected .gitignore**: Comprehensive exclusion patterns prevent accidental exposure of sensitive configuration files
- **Backup safety**: Automatic backups are stored locally and never transmitted

For complete security guidelines, see: [SECURITY.md](SECURITY.md)

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

- 🐛 [Report Bugs](https://github.com/gilberth/sync-mcp-cfg/issues)
- 💡 [Request Features](https://github.com/gilberth/sync-mcp-cfg/issues)
- 📖 [Documentation](https://github.com/gilberth/sync-mcp-cfg/wiki)
- 💬 [Discussions](https://github.com/gilberth/sync-mcp-cfg/discussions)

---

## 🆕 Recent Updates

### Latest Release - OpenCode & Gemini CLI Support

**🎉 Major Features Added:**

- ✅ **Complete OpenCode Support**: Full integration with local/remote server support, auto-detection, and native configuration format
- ✅ **Complete Gemini CLI Support**: Full integration with auto-detection, trust control, and timeout configuration
- ✅ **Enhanced VSCode Support**: Now uses global settings.json for proper MCP configuration
- ✅ **Security Hardening**: Protected against accidental exposure of sensitive data with comprehensive .gitignore
- ✅ **Cross-Client Synchronization**: Seamless MCP server sharing between all supported clients including OpenCode
- ✅ **Comprehensive Testing**: Full test coverage for all new features including OpenCode
- ✅ **Rich Documentation**: Detailed examples and usage guides for all clients

**🔧 Technical Improvements:**

- Plugin-based architecture with easy extensibility
- Automatic backup creation before all destructive operations
- Enhanced error handling and validation
- Improved client auto-detection across all platforms
- Support for client-specific configuration fields (trust, cwd, timeout, httpUrl, OpenCode's type/command structure)
- OpenCode's unique local/remote server format with environment variable support

**Made with ❤️ for the AI development community**
