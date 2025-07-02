# OpenCode Integration Example

This document demonstrates the new OpenCode support in sync-mcp-cfg.

## Quick Demo

```bash
# Check OpenCode status
sync-mcp-cfg status

# Add a local server to OpenCode
sync-mcp-cfg add filesystem npx \
  -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/tmp" \
  --clients opencode \
  --description "Filesystem server for OpenCode"

# Add a remote server to OpenCode  
sync-mcp-cfg add context7 "" \
  --type sse --url "https://mcp.context7.ai/v1" \
  --clients opencode \
  --description "Context7 remote MCP server"

# Sync from VS Code to OpenCode
sync-mcp-cfg sync --from vscode --to opencode --servers github

# Sync FROM OpenCode to other clients
sync-mcp-cfg sync --from opencode --to cursor --servers filesystem

# List OpenCode servers
sync-mcp-cfg list --client opencode
```

## OpenCode Configuration Example

The generated OpenCode configuration follows the official format:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "filesystem": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
      "enabled": true
    },
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.ai/v1", 
      "enabled": true
    },
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@smithery/cli@latest", "run", "@smithery-ai/github"],
      "environment": {
        "GITHUB_TOKEN": "your-token"
      },
      "enabled": true
    }
  }
}
```

## Bidirectional Sync

OpenCode can both receive servers from other clients and share its servers:

```bash
# Receive servers from Claude Desktop
sync-mcp-cfg sync --from claude-desktop --to opencode

# Share OpenCode servers with all other clients  
sync-mcp-cfg sync --from opencode --to claude-code --to cursor --to vscode
```

## Configuration Paths

- **Global**: `~/.config/opencode/config.json`
- **Project**: `./opencode.json` (takes precedence)
- **Backups**: `~/.config/opencode/backups/`

This integration makes OpenCode a first-class citizen in the MCP ecosystem!