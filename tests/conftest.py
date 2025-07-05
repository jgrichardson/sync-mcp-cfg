"""Pytest configuration and fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock

import pytest

from sync_mcp_cfg.core.models import ClientConfig, ClientType, MCPServer, MCPServerType


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_mcp_server():
    """Create a sample MCP server for testing."""
    return MCPServer(
        name="test-server",
        command="echo",
        args=["hello", "world"],
        env={"TEST_VAR": "test_value"},
        server_type=MCPServerType.STDIO,
        enabled=True,
        description="A test server",
    )


@pytest.fixture
def sample_servers():
    """Create multiple sample MCP servers."""
    return [
        MCPServer(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            server_type=MCPServerType.STDIO,
        ),
        MCPServer(
            name="weather",
            command="node",
            args=["/path/to/weather.js"],
            env={"API_KEY": "secret"},
            server_type=MCPServerType.STDIO,
        ),
        MCPServer(
            name="sse-server",
            command="",
            server_type=MCPServerType.SSE,
            url="http://localhost:3000/sse",
        ),
    ]


@pytest.fixture
def claude_code_config_data():
    """Sample Claude Code configuration data."""
    return {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                "env": {},
            },
            "weather": {
                "command": "node",
                "args": ["/path/to/weather.js"],
                "env": {"API_KEY": "secret"},
            },
        }
    }


@pytest.fixture
def claude_desktop_config_data():
    """Sample Claude Desktop configuration data."""
    return {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                "env": {},
            },
        }
    }


@pytest.fixture
def cursor_config_data():
    """Sample Cursor configuration data."""
    return {
        "version": "1.0",
        "servers": [
            {
                "name": "filesystem",
                "type": "command",
                "command": "npx -y @modelcontextprotocol/server-filesystem /tmp",
                "enabled": True,
            },
            {
                "name": "weather",
                "type": "command",
                "command": "node /path/to/weather.js",
                "enabled": True,
            },
        ],
    }


@pytest.fixture
def vscode_config_data():
    """Sample VS Code configuration data."""
    return {
        "inputs": [
            {
                "type": "promptString",
                "id": "api-key",
                "description": "API Key",
                "password": True,
            }
        ],
        "servers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                "env": {},
            },
            "weather": {
                "command": "node",
                "args": ["/path/to/weather.js"],
                "env": {"API_KEY": "${input:api-key}"},
            },
        },
    }


@pytest.fixture
def mock_client_config(temp_dir):
    """Create a mock client configuration."""
    config_path = temp_dir / "test_config.json"
    return ClientConfig(
        client_type=ClientType.CLAUDE_CODE,
        config_path=config_path,
        is_available=True,
    )


@pytest.fixture
def claude_code_config_file(temp_dir, claude_code_config_data):
    """Create a Claude Code configuration file."""
    config_path = temp_dir / "claude_config.json"
    with open(config_path, 'w') as f:
        json.dump(claude_code_config_data, f, indent=2)
    return config_path


@pytest.fixture
def cursor_config_file(temp_dir, cursor_config_data):
    """Create a Cursor configuration file."""
    config_path = temp_dir / "cursor_config.json"
    with open(config_path, 'w') as f:
        json.dump(cursor_config_data, f, indent=2)
    return config_path


@pytest.fixture
def vscode_config_file(temp_dir, vscode_config_data):
    """Create a VS Code configuration file."""
    config_path = temp_dir / "vscode_config.json"
    with open(config_path, 'w') as f:
        json.dump(vscode_config_data, f, indent=2)
    return config_path


@pytest.fixture
def mock_registry():
    """Create a mock client registry."""
    registry = Mock()
    registry.get_available_clients.return_value = [
        ClientConfig(
            client_type=ClientType.CLAUDE_CODE,
            config_path=Path("/mock/claude.json"),
            is_available=True,
        ),
        ClientConfig(
            client_type=ClientType.CURSOR,
            config_path=Path("/mock/cursor.json"),
            is_available=True,
        ),
    ]
    return registry
