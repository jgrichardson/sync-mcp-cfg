"""Tests for Gemini CLI client handler."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from sync_mcp_cfg.clients.gemini_cli import GeminiCLIHandler
from sync_mcp_cfg.core.models import ClientConfig, ClientType, MCPServer, MCPServerType


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            'mcpServers': {
                'test-server': {
                    'command': 'python',
                    'args': ['-m', 'test_server'],
                    'env': {'TEST_VAR': 'test_value'},
                    'trust': True,
                    'cwd': './test-dir',
                    'timeout': 30000
                },
                'disabled-server': {
                    'command': 'node',
                    'args': ['server.js'],
                    'env': {},
                    'trust': False,
                    'timeout': 15000
                }
            },
            'theme': 'Default'
        }
        json.dump(config_data, f, indent=2)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def gemini_handler(temp_config_file):
    """Create a GeminiCLIHandler with temporary config."""
    config = ClientConfig(
        client_type=ClientType.GEMINI_CLI,
        config_path=temp_config_file,
        is_available=True
    )
    return GeminiCLIHandler(config)


def test_load_servers(gemini_handler):
    """Test loading servers from Gemini CLI configuration."""
    servers = gemini_handler.load_servers()
    
    assert len(servers) == 2
    
    test_server = next(s for s in servers if s.name == 'test-server')
    assert test_server.command == 'python'
    assert test_server.args == ['-m', 'test_server']
    assert test_server.env == {'TEST_VAR': 'test_value'}
    assert test_server.server_type == MCPServerType.STDIO
    assert test_server.enabled is True
    assert 'timeout: 30000ms, cwd: ./test-dir' in test_server.description
    
    disabled_server = next(s for s in servers if s.name == 'disabled-server')
    assert disabled_server.enabled is False


def test_save_servers(gemini_handler):
    """Test saving servers to Gemini CLI configuration."""
    new_server = MCPServer(
        name='new-server',
        command='python3',
        args=['-m', 'new_server'],
        env={'NEW_VAR': 'new_value'},
        server_type=MCPServerType.HTTP,
        url='http://localhost:8000',
        enabled=True,
        description='New test server'
    )
    
    gemini_handler.save_servers([new_server])
    
    # Reload and verify
    servers = gemini_handler.load_servers()
    assert len(servers) == 1
    
    saved_server = servers[0]
    assert saved_server.name == 'new-server'
    assert saved_server.command == 'python3'
    assert saved_server.server_type == MCPServerType.HTTP
    assert saved_server.url == 'http://localhost:8000'
    # Description should contain the URL since it's an HTTP server


def test_add_server(gemini_handler):
    """Test adding a single server."""
    new_server = MCPServer(
        name='added-server',
        command='node',
        args=['added.js'],
        env={},
        server_type=MCPServerType.STDIO,
        enabled=True
    )
    
    gemini_handler.add_server(new_server)
    
    servers = gemini_handler.load_servers()
    assert len(servers) == 3  # 2 original + 1 new
    
    added_server = next(s for s in servers if s.name == 'added-server')
    assert added_server.command == 'node'


def test_remove_server(gemini_handler):
    """Test removing a server."""
    result = gemini_handler.remove_server('test-server')
    assert result is True
    
    servers = gemini_handler.load_servers()
    assert len(servers) == 1
    assert all(s.name != 'test-server' for s in servers)
    
    # Try removing non-existent server
    result = gemini_handler.remove_server('non-existent')
    assert result is False


def test_get_server(gemini_handler):
    """Test getting a specific server."""
    server = gemini_handler.get_server('test-server')
    assert server is not None
    assert server.name == 'test-server'
    
    # Test non-existent server
    server = gemini_handler.get_server('non-existent')
    assert server is None


def test_validate_config(gemini_handler):
    """Test configuration validation."""
    assert gemini_handler.validate_config() is True
    
    # Test with invalid config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('invalid json')
        invalid_path = Path(f.name)
    
    invalid_config = ClientConfig(
        client_type=ClientType.GEMINI_CLI,
        config_path=invalid_path,
        is_available=True
    )
    invalid_handler = GeminiCLIHandler(invalid_config)
    
    assert invalid_handler.validate_config() is False
    
    # Cleanup
    invalid_path.unlink()


def test_backup_and_restore(gemini_handler):
    """Test backup and restore functionality."""
    # Create backup
    backup_path = gemini_handler.backup_config()
    assert backup_path.exists()
    
    # Modify original config
    new_server = MCPServer(
        name='backup-test',
        command='test',
        args=[],
        env={},
        server_type=MCPServerType.STDIO,
        enabled=True
    )
    gemini_handler.save_servers([new_server])
    
    # Verify modification
    servers = gemini_handler.load_servers()
    assert len(servers) == 1
    assert servers[0].name == 'backup-test'
    
    # Restore from backup
    gemini_handler.restore_config(backup_path)
    
    # Verify restore
    servers = gemini_handler.load_servers()
    assert len(servers) == 2  # Original servers restored
    
    # Cleanup
    backup_path.unlink()


def test_default_config_path():
    """Test default configuration path."""
    default_path = GeminiCLIHandler.get_default_config_path()
    expected_path = Path.home() / ".gemini" / "settings.json"
    assert default_path == expected_path


@patch('shutil.which')
def test_is_available(mock_which):
    """Test availability check."""
    # Test when gemini is available
    mock_which.return_value = '/usr/local/bin/gemini'
    assert GeminiCLIHandler.is_available() is True
    
    # Test when gemini is not available
    mock_which.return_value = None
    assert GeminiCLIHandler.is_available() is False


def test_empty_config():
    """Test handling of empty/non-existent config."""
    with tempfile.NamedTemporaryFile(delete=True) as f:
        config_path = Path(f.name)
    
    # Config file doesn't exist now
    config = ClientConfig(
        client_type=ClientType.GEMINI_CLI,
        config_path=config_path,
        is_available=True
    )
    handler = GeminiCLIHandler(config)
    
    # Should return empty list for non-existent config
    servers = handler.load_servers()
    assert servers == []
    
    # Should be able to save to non-existent config (creates it)
    new_server = MCPServer(
        name='first-server',
        command='python',
        args=[],
        env={},
        server_type=MCPServerType.STDIO,
        enabled=True
    )
    handler.save_servers([new_server])
    
    # Verify it was saved
    servers = handler.load_servers()
    assert len(servers) == 1
    assert servers[0].name == 'first-server'
    
    # Cleanup
    if config_path.exists():
        config_path.unlink()
