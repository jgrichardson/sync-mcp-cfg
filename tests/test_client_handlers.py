"""Tests for client handlers."""

import json
from pathlib import Path

import pytest

from sync_mcp_cfg.clients.claude_code import ClaudeCodeHandler
from sync_mcp_cfg.clients.cursor import CursorHandler
from sync_mcp_cfg.clients.vscode import VSCodeHandler
from sync_mcp_cfg.core.models import ClientConfig, ClientType, MCPServerType


class TestClaudeCodeHandler:
    """Test Claude Code client handler."""

    def test_load_servers_empty_config(self, temp_dir):
        """Test loading servers from empty config."""
        config_path = temp_dir / "empty.json"
        config_path.write_text("{}")

        config = ClientConfig(
            client_type=ClientType.CLAUDE_CODE,
            config_path=config_path,
            is_available=True,
        )
        handler = ClaudeCodeHandler(config)

        servers = handler.load_servers()
        assert servers == []

    def test_load_servers_with_data(self, temp_dir, claude_code_config_data):
        """Test loading servers from config with data."""
        config_path = temp_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(claude_code_config_data, f)

        config = ClientConfig(
            client_type=ClientType.CLAUDE_CODE,
            config_path=config_path,
            is_available=True,
        )
        handler = ClaudeCodeHandler(config)

        servers = handler.load_servers()
        assert len(servers) == 2

        # Check filesystem server
        fs_server = next(s for s in servers if s.name == "filesystem")
        assert fs_server.command == "npx"
        assert fs_server.args == [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "/tmp",
        ]
        assert fs_server.server_type == MCPServerType.STDIO

        # Check weather server
        weather_server = next(s for s in servers if s.name == "weather")
        assert weather_server.command == "node"
        assert weather_server.env == {"API_KEY": "secret"}

    def test_save_servers(self, temp_dir, sample_servers):
        """Test saving servers to config."""
        config_path = temp_dir / "claude.json"

        config = ClientConfig(
            client_type=ClientType.CLAUDE_CODE,
            config_path=config_path,
            is_available=True,
        )
        handler = ClaudeCodeHandler(config)

        # Save only stdio servers (Claude Code format)
        stdio_servers = [
            s for s in sample_servers if s.server_type == MCPServerType.STDIO
        ]
        handler.save_servers(stdio_servers)

        # Verify file was created
        assert config_path.exists()

        # Load and verify content
        with open(config_path) as f:
            data = json.load(f)

        assert "mcpServers" in data
        assert len(data["mcpServers"]) == 2
        assert "filesystem" in data["mcpServers"]
        assert "weather" in data["mcpServers"]

    def test_add_server(self, temp_dir, sample_mcp_server):
        """Test adding a server."""
        config_path = temp_dir / "claude.json"
        config_path.write_text("{}")

        config = ClientConfig(
            client_type=ClientType.CLAUDE_CODE,
            config_path=config_path,
            is_available=True,
        )
        handler = ClaudeCodeHandler(config)

        handler.add_server(sample_mcp_server)

        servers = handler.load_servers()
        assert len(servers) == 1
        assert servers[0].name == "test-server"

    def test_remove_server(self, temp_dir, claude_code_config_data):
        """Test removing a server."""
        config_path = temp_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(claude_code_config_data, f)

        config = ClientConfig(
            client_type=ClientType.CLAUDE_CODE,
            config_path=config_path,
            is_available=True,
        )
        handler = ClaudeCodeHandler(config)

        # Remove existing server
        assert handler.remove_server("filesystem") is True

        servers = handler.load_servers()
        assert len(servers) == 1
        assert servers[0].name == "weather"

        # Try to remove non-existent server
        assert handler.remove_server("nonexistent") is False

    def test_validate_config(self, temp_dir):
        """Test config validation."""
        config = ClientConfig(
            client_type=ClientType.CLAUDE_CODE,
            config_path=temp_dir / "claude.json",
            is_available=True,
        )
        handler = ClaudeCodeHandler(config)

        # Non-existent file is valid
        assert handler.validate_config() is True

        # Valid config
        valid_config = {"mcpServers": {"test": {"command": "echo"}}}
        config.config_path.write_text(json.dumps(valid_config))
        assert handler.validate_config() is True

        # Invalid config
        invalid_config = {"mcpServers": {"test": {}}}  # Missing command
        config.config_path.write_text(json.dumps(invalid_config))
        assert handler.validate_config() is False


class TestCursorHandler:
    """Test Cursor client handler."""

    def test_load_servers_with_data(self, temp_dir, cursor_config_data):
        """Test loading servers from Cursor config."""
        config_path = temp_dir / "cursor.json"
        with open(config_path, 'w') as f:
            json.dump(cursor_config_data, f)

        config = ClientConfig(
            client_type=ClientType.CURSOR,
            config_path=config_path,
            is_available=True,
        )
        handler = CursorHandler(config)

        servers = handler.load_servers()
        assert len(servers) == 2

        # Check filesystem server
        fs_server = next(s for s in servers if s.name == "filesystem")
        assert fs_server.command == "npx"
        assert fs_server.args == [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "/tmp",
        ]

    def test_save_servers(self, temp_dir, sample_servers):
        """Test saving servers to Cursor config."""
        config_path = temp_dir / "cursor.json"

        config = ClientConfig(
            client_type=ClientType.CURSOR,
            config_path=config_path,
            is_available=True,
        )
        handler = CursorHandler(config)

        # Save only stdio servers
        stdio_servers = [
            s for s in sample_servers if s.server_type == MCPServerType.STDIO
        ]
        handler.save_servers(stdio_servers)

        # Verify file was created
        assert config_path.exists()

        # Load and verify content
        with open(config_path) as f:
            data = json.load(f)

        assert "servers" in data
        assert "version" in data
        assert len(data["servers"]) == 2


class TestVSCodeHandler:
    """Test VS Code client handler."""

    def test_load_servers_with_data(self, temp_dir, vscode_config_data):
        """Test loading servers from VS Code config."""
        config_path = temp_dir / "vscode.json"
        with open(config_path, 'w') as f:
            json.dump(vscode_config_data, f)

        config = ClientConfig(
            client_type=ClientType.VSCODE,
            config_path=config_path,
            is_available=True,
        )
        handler = VSCodeHandler(config)

        servers = handler.load_servers()
        assert len(servers) == 2

        # Check weather server with environment variable
        weather_server = next(s for s in servers if s.name == "weather")
        assert weather_server.env == {"API_KEY": "${input:api-key}"}

    def test_save_servers_preserves_inputs(
        self, temp_dir, vscode_config_data, sample_servers
    ):
        """Test that saving servers preserves inputs section."""
        config_path = temp_dir / "vscode.json"
        with open(config_path, 'w') as f:
            json.dump(vscode_config_data, f)

        config = ClientConfig(
            client_type=ClientType.VSCODE,
            config_path=config_path,
            is_available=True,
        )
        handler = VSCodeHandler(config)

        # Save servers
        stdio_servers = [
            s for s in sample_servers if s.server_type == MCPServerType.STDIO
        ]
        handler.save_servers(stdio_servers)

        # Load and verify inputs are preserved
        with open(config_path) as f:
            data = json.load(f)

        assert "inputs" in data
        assert len(data["inputs"]) == 1
        assert data["inputs"][0]["id"] == "api-key"

    def test_set_workspace_config_path(self, temp_dir):
        """Test setting workspace-specific config path."""
        original_path = temp_dir / "original.json"
        config = ClientConfig(
            client_type=ClientType.VSCODE,
            config_path=original_path,
            is_available=True,
        )
        handler = VSCodeHandler(config)

        workspace_path = temp_dir / "workspace"
        handler.set_workspace_config_path(workspace_path)

        expected_path = workspace_path / ".vscode" / "mcp.json"
        assert handler.config.config_path == expected_path
