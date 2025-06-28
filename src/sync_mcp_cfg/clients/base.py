"""Abstract base class for MCP client handlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from ..core.models import ClientConfig, MCPServer


class BaseClientHandler(ABC):
    """Abstract base class for MCP client handlers."""
    
    def __init__(self, config: ClientConfig):
        self.config = config
    
    @abstractmethod
    def load_servers(self) -> List[MCPServer]:
        """Load MCP servers from the client's configuration."""
        pass
    
    @abstractmethod
    def save_servers(self, servers: List[MCPServer]) -> None:
        """Save MCP servers to the client's configuration."""
        pass
    
    @abstractmethod
    def add_server(self, server: MCPServer) -> None:
        """Add a single MCP server to the client's configuration."""
        pass
    
    @abstractmethod
    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server from the client's configuration."""
        pass
    
    @abstractmethod
    def get_server(self, server_name: str) -> Optional[MCPServer]:
        """Get a specific MCP server by name."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the client's configuration format."""
        pass
    
    @abstractmethod
    def backup_config(self, backup_path: Optional[Path] = None) -> Path:
        """Create a backup of the current configuration."""
        pass
    
    @abstractmethod
    def restore_config(self, backup_path: Path) -> None:
        """Restore configuration from a backup."""
        pass
    
    def ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self.config.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def config_exists(self) -> bool:
        """Check if the configuration file exists."""
        return self.config.config_path.exists()
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.config.client_type.value})"