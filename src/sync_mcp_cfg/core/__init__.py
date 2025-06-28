"""Core functionality for sync-mcp-cfg."""

from .exceptions import (
    BackupError,
    ClientHandlerError,
    ClientNotFoundError,
    ConfigurationError,
    ServerNotFoundError,
    SyncError,
    SyncMCPError,
    ValidationError,
)
from .models import (
    AppConfig,
    BackupInfo,
    ClientConfig,
    ClientType,
    MCPServer,
    MCPServerType,
    SyncConfig,
)
from .registry import ClientRegistry

__all__ = [
    # Exceptions
    "SyncMCPError",
    "ClientNotFoundError", 
    "ConfigurationError",
    "ValidationError",
    "BackupError",
    "SyncError",
    "ServerNotFoundError",
    "ClientHandlerError",
    # Models
    "MCPServer",
    "MCPServerType",
    "ClientConfig",
    "ClientType",
    "SyncConfig",
    "BackupInfo",
    "AppConfig",
    # Registry
    "ClientRegistry",
]