"""Core data models for MCP servers and client configurations."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class MCPServerType(str, Enum):
    """MCP server transport types."""
    
    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"


class MCPServer(BaseModel):
    """Represents an MCP server configuration."""
    
    name: str = Field(..., description="Unique name for the MCP server")
    command: str = Field(..., description="Command to execute the server")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    server_type: MCPServerType = Field(default=MCPServerType.STDIO, description="Server transport type")
    url: Optional[str] = Field(None, description="URL for SSE/HTTP servers")
    enabled: bool = Field(default=True, description="Whether the server is enabled")
    description: Optional[str] = Field(None, description="Human-readable description")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate server name contains only allowed characters."""
        if not v or not v.strip():
            raise ValueError("Server name cannot be empty")
        
        # Allow alphanumeric, hyphens, underscores
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        if not all(c in allowed_chars for c in v):
            raise ValueError("Server name can only contain letters, numbers, hyphens, and underscores")
        
        return v.strip()
    
    @validator('url')
    def validate_url(cls, v, values):
        """Validate URL is provided for SSE/HTTP servers."""
        server_type = values.get('server_type')
        if server_type in (MCPServerType.SSE, MCPServerType.HTTP) and not v:
            raise ValueError(f"URL is required for {server_type} servers")
        return v
    
    def __str__(self) -> str:
        return f"{self.name} ({self.server_type})"


class ClientType(str, Enum):
    """Supported MCP client types."""
    
    CLAUDE_CODE = "claude-code"
    CLAUDE_DESKTOP = "claude-desktop"
    CURSOR = "cursor"
    VSCODE = "vscode"


class ClientConfig(BaseModel):
    """Configuration for a specific MCP client."""
    
    client_type: ClientType
    config_path: Path
    is_available: bool = Field(default=False, description="Whether the client is installed/available")
    servers: List[MCPServer] = Field(default_factory=list, description="Servers configured for this client")
    
    class Config:
        arbitrary_types_allowed = True
    
    @validator('config_path', pre=True)
    def validate_path(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v).expanduser().resolve()
        return v
    
    def add_server(self, server: MCPServer) -> None:
        """Add a server to this client configuration."""
        # Remove existing server with same name
        self.servers = [s for s in self.servers if s.name != server.name]
        self.servers.append(server)
    
    def remove_server(self, server_name: str) -> bool:
        """Remove a server from this client configuration."""
        original_count = len(self.servers)
        self.servers = [s for s in self.servers if s.name != server_name]
        return len(self.servers) < original_count
    
    def get_server(self, server_name: str) -> Optional[MCPServer]:
        """Get a server by name."""
        for server in self.servers:
            if server.name == server_name:
                return server
        return None
    
    def __str__(self) -> str:
        status = "✓" if self.is_available else "✗"
        return f"{status} {self.client_type.value} ({len(self.servers)} servers)"


class SyncConfig(BaseModel):
    """Configuration for syncing servers between clients."""
    
    source_client: ClientType
    target_clients: List[ClientType]
    servers: List[str] = Field(default_factory=list, description="Specific servers to sync (empty = all)")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing servers")
    backup: bool = Field(default=True, description="Whether to create backup before sync")
    
    def __str__(self) -> str:
        targets = ", ".join(client.value for client in self.target_clients)
        server_count = len(self.servers) if self.servers else "all"
        return f"Sync {server_count} servers from {self.source_client.value} to {targets}"


class BackupInfo(BaseModel):
    """Information about a configuration backup."""
    
    timestamp: str
    client_type: ClientType
    backup_path: Path
    original_path: Path
    server_count: int
    
    class Config:
        arbitrary_types_allowed = True
    
    @validator('backup_path', 'original_path', pre=True)
    def validate_paths(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v
    
    def __str__(self) -> str:
        return f"{self.client_type.value} backup from {self.timestamp} ({self.server_count} servers)"


class AppConfig(BaseModel):
    """Global application configuration."""
    
    auto_backup: bool = Field(default=True, description="Automatically backup before changes")
    backup_retention_days: int = Field(default=30, description="Days to keep backups")
    default_sync_target: Optional[List[ClientType]] = Field(None, description="Default sync targets")
    validate_servers: bool = Field(default=True, description="Validate server configurations")
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> AppConfig:
        """Load configuration from file."""
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        return cls()
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.dict(), f, indent=2, default=str)