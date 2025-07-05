"""Tests for core models."""

import pytest
from pydantic import ValidationError

from sync_mcp_cfg.core.models import (
    ClientType,
    MCPServer,
    MCPServerType,
)


class TestMCPServer:
    """Test MCP server model."""

    def test_create_basic_server(self):
        """Test creating a basic MCP server."""
        server = MCPServer(
            name="test-server",
            command="echo",
            args=["hello", "world"],
            env={"TEST": "value"},
        )

        assert server.name == "test-server"
        assert server.command == "echo"
        assert server.args == ["hello", "world"]
        assert server.env == {"TEST": "value"}
        assert server.server_type == MCPServerType.STDIO
        assert server.enabled is True
        assert server.url is None

    def test_create_sse_server(self):
        """Test creating an SSE server."""
        server = MCPServer(
            name="sse-server",
            command="",
            server_type=MCPServerType.SSE,
            url="http://localhost:3000/sse",
        )

        assert server.server_type == MCPServerType.SSE
        assert server.url == "http://localhost:3000/sse"

    def test_server_name_validation(self):
        """Test server name validation."""
        # Valid names
        valid_names = ["server", "server-name", "server_name", "server123"]
        for name in valid_names:
            server = MCPServer(name=name, command="echo")
            assert server.name == name

        # Invalid names
        invalid_names = ["", "  ", "server name", "server@name", "server/name"]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                MCPServer(name=name, command="echo")

    def test_url_validation_for_sse_server(self):
        """Test URL validation for SSE servers."""
        # SSE server without URL should fail
        with pytest.raises(ValidationError):
            MCPServer(
                name="sse-server",
                command="",
                server_type=MCPServerType.SSE,
            )

        # SSE server with URL should succeed
        server = MCPServer(
            name="sse-server",
            command="",
            server_type=MCPServerType.SSE,
            url="http://localhost:3000",
        )
        assert server.url == "http://localhost:3000"

    def test_server_string_representation(self):
        """Test server string representation."""
        server = MCPServer(
            name="test-server",
            command="echo",
            server_type=MCPServerType.STDIO,
        )
        assert str(server) == "test-server (stdio)"


class TestClientType:
    """Test client type enum."""

    def test_client_types(self):
        """Test all client types are available."""
        expected_types = {
            "claude-code",
            "claude-desktop",
            "cursor",
            "vscode",
            "gemini-cli",
            "opencode",
        }

        actual_types = {ct.value for ct in ClientType}
        assert actual_types == expected_types

    def test_client_type_from_string(self):
        """Test creating client type from string."""
        assert ClientType("claude-code") == ClientType.CLAUDE_CODE
        assert ClientType("cursor") == ClientType.CURSOR

        with pytest.raises(ValueError):
            ClientType("invalid-client")


class TestMCPServerType:
    """Test MCP server type enum."""

    def test_server_types(self):
        """Test all server types are available."""
        expected_types = {"stdio", "sse", "http"}
        actual_types = {st.value for st in MCPServerType}
        assert actual_types == expected_types

    def test_default_server_type(self):
        """Test default server type is stdio."""
        server = MCPServer(name="test", command="echo")
        assert server.server_type == MCPServerType.STDIO
