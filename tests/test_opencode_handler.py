"""Tests for OpenCode client handler."""

import json
import tempfile
from pathlib import Path

import pytest

from sync_mcp_cfg.clients.opencode import OpenCodeHandler
from sync_mcp_cfg.core.models import ClientConfig, ClientType, MCPServer, MCPServerType


class TestOpenCodeHandler:
    """Test OpenCode client handler."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "config.json"
        self.client_config = ClientConfig(
            client_type=ClientType.OPENCODE,
            config_path=self.config_path,
            is_available=True,
        )
        self.handler = OpenCodeHandler(self.client_config)

    def test_load_servers_empty_config(self):
        """Test loading servers from empty config."""
        servers = self.handler.load_servers()
        assert servers == []

    def test_load_servers_local_server(self):
        """Test loading local MCP servers."""
        config_data = {
            "$schema": "https://opencode.ai/config.json",
            "mcp": {
                "filesystem": {
                    "type": "local",
                    "command": ["node", "/path/to/server.js"],
                    "environment": {"PATH_ROOT": "/workspace"},
                    "enabled": True,
                }
            },
        }

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        servers = self.handler.load_servers()
        assert len(servers) == 1

        server = servers[0]
        assert server.name == "filesystem"
        assert server.command == "node"
        assert server.args == ["/path/to/server.js"]
        assert server.env == {"PATH_ROOT": "/workspace"}
        assert server.server_type == MCPServerType.STDIO
        assert server.enabled is True

    def test_load_servers_remote_server(self):
        """Test loading remote MCP servers."""
        config_data = {
            "$schema": "https://opencode.ai/config.json",
            "mcp": {
                "context7": {
                    "type": "remote",
                    "url": "https://mcp.context7.ai/v1",
                    "enabled": True,
                }
            },
        }

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        servers = self.handler.load_servers()
        assert len(servers) == 1

        server = servers[0]
        assert server.name == "context7"
        assert server.command == ""
        assert server.args == []
        assert server.env == {}
        assert server.server_type == MCPServerType.SSE
        assert server.url == "https://mcp.context7.ai/v1"
        assert server.enabled is True

    def test_save_servers_local(self):
        """Test saving local MCP servers."""
        server = MCPServer(
            name="test-server",
            command="python",
            args=["-m", "test_server"],
            env={"API_KEY": "test123"},
            server_type=MCPServerType.STDIO,
            enabled=True,
        )

        self.handler.save_servers([server])

        # Read back and verify
        with open(self.config_path, "r") as f:
            config_data = json.load(f)

        assert "$schema" in config_data
        assert "mcp" in config_data

        mcp_config = config_data["mcp"]
        assert "test-server" in mcp_config

        server_config = mcp_config["test-server"]
        assert server_config["type"] == "local"
        assert server_config["command"] == ["python", "-m", "test_server"]
        assert server_config["environment"] == {"API_KEY": "test123"}
        assert server_config["enabled"] is True

    def test_save_servers_remote(self):
        """Test saving remote MCP servers."""
        server = MCPServer(
            name="remote-server",
            command="",
            args=[],
            env={},
            server_type=MCPServerType.SSE,
            url="https://example.com/mcp",
            enabled=True,
        )

        self.handler.save_servers([server])

        # Read back and verify
        with open(self.config_path, "r") as f:
            config_data = json.load(f)

        mcp_config = config_data["mcp"]
        assert "remote-server" in mcp_config

        server_config = mcp_config["remote-server"]
        assert server_config["type"] == "remote"
        assert server_config["url"] == "https://example.com/mcp"
        assert server_config["enabled"] is True

    def test_add_server(self):
        """Test adding a single server."""
        server = MCPServer(
            name="new-server",
            command="echo",
            args=["hello"],
            server_type=MCPServerType.STDIO,
        )

        self.handler.add_server(server)
        servers = self.handler.load_servers()

        assert len(servers) == 1
        assert servers[0].name == "new-server"
        assert servers[0].command == "echo"
        assert servers[0].args == ["hello"]

    def test_remove_server(self):
        """Test removing a server."""
        # First add a server
        server = MCPServer(
            name="to-remove", command="test", server_type=MCPServerType.STDIO
        )
        self.handler.add_server(server)

        # Verify it exists
        servers = self.handler.load_servers()
        assert len(servers) == 1

        # Remove it
        removed = self.handler.remove_server("to-remove")
        assert removed is True

        # Verify it's gone
        servers = self.handler.load_servers()
        assert len(servers) == 0

    def test_remove_nonexistent_server(self):
        """Test removing a server that doesn't exist."""
        removed = self.handler.remove_server("nonexistent")
        assert removed is False

    def test_get_server(self):
        """Test getting a specific server."""
        server = MCPServer(
            name="get-test", command="test", server_type=MCPServerType.STDIO
        )
        self.handler.add_server(server)

        # Get existing server
        found_server = self.handler.get_server("get-test")
        assert found_server is not None
        assert found_server.name == "get-test"
        assert found_server.command == "test"

        # Get nonexistent server
        not_found = self.handler.get_server("nonexistent")
        assert not_found is None

    def test_validate_config_empty(self):
        """Test validating empty config."""
        assert self.handler.validate_config() is True

    def test_validate_config_valid(self):
        """Test validating valid config."""
        config_data = {
            "$schema": "https://opencode.ai/config.json",
            "mcp": {
                "test": {
                    "type": "local",
                    "command": ["node", "server.js"],
                    "enabled": True,
                },
                "remote": {
                    "type": "remote",
                    "url": "https://example.com",
                    "enabled": False,
                },
            },
        }

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        assert self.handler.validate_config() is True

    def test_validate_config_invalid(self):
        """Test validating invalid config."""
        config_data = {
            "mcp": {"invalid": {"type": "invalid_type", "command": "not_a_list"}}
        }

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        assert self.handler.validate_config() is False

    def test_backup_config(self):
        """Test backing up config."""
        # Create initial config
        config_data = {"mcp": {"test": {"type": "local", "command": ["test"]}}}
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        # Backup
        backup_path = self.handler.backup_config()

        # Verify backup exists and has same content
        assert backup_path.exists()
        with open(backup_path, "r") as f:
            backup_data = json.load(f)
        assert backup_data == config_data

    def test_restore_config(self):
        """Test restoring config from backup."""
        # Create original config
        original_data = {"mcp": {"original": {"type": "local", "command": ["orig"]}}}
        with open(self.config_path, "w") as f:
            json.dump(original_data, f)

        # Create backup
        backup_path = self.handler.backup_config()

        # Modify original
        modified_data = {"mcp": {"modified": {"type": "local", "command": ["mod"]}}}
        with open(self.config_path, "w") as f:
            json.dump(modified_data, f)

        # Restore from backup
        self.handler.restore_config(backup_path)

        # Verify restoration
        with open(self.config_path, "r") as f:
            restored_data = json.load(f)
        assert restored_data == original_data

    def test_preserve_other_config_settings(self):
        """Test that saving servers preserves other config settings."""
        # Create config with other settings
        config_data = {
            "$schema": "https://opencode.ai/config.json",
            "theme": "dark",
            "model": "anthropic/claude-3",
            "mcp": {
                "existing": {"type": "local", "command": ["existing"], "enabled": True}
            },
        }

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        # Add a new server
        new_server = MCPServer(
            name="new", command="new_command", server_type=MCPServerType.STDIO
        )

        # This should preserve existing settings
        existing_servers = self.handler.load_servers()
        all_servers = existing_servers + [new_server]
        self.handler.save_servers(all_servers)

        # Verify other settings are preserved
        with open(self.config_path, "r") as f:
            updated_config = json.load(f)

        assert updated_config["theme"] == "dark"
        assert updated_config["model"] == "anthropic/claude-3"
        assert len(updated_config["mcp"]) == 2
        assert "existing" in updated_config["mcp"]
        assert "new" in updated_config["mcp"]
