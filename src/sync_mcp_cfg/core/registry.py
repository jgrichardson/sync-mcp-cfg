"""Client registry and discovery system."""

import platform
from pathlib import Path
from typing import Dict, List, Optional

from ..core.exceptions import ClientNotFoundError
from ..core.models import ClientConfig, ClientType


class ClientRegistry:
    """Registry for discovering and managing MCP clients."""
    
    def __init__(self):
        self._clients: Dict[ClientType, ClientConfig] = {}
        self._discover_clients()
    
    def _discover_clients(self) -> None:
        """Discover available MCP clients on the system."""
        self._clients.clear()
        
        # Discover each client type
        for client_type in ClientType:
            config = self._discover_client(client_type)
            if config:
                self._clients[client_type] = config
    
    def _discover_client(self, client_type: ClientType) -> Optional[ClientConfig]:
        """Discover a specific client type."""
        system = platform.system().lower()
        
        if client_type == ClientType.CLAUDE_CODE:
            return self._discover_claude_code()
        elif client_type == ClientType.CLAUDE_DESKTOP:
            return self._discover_claude_desktop(system)
        elif client_type == ClientType.CURSOR:
            return self._discover_cursor(system)
        elif client_type == ClientType.VSCODE:
            return self._discover_vscode()
        elif client_type == ClientType.GEMINI_CLI:
            return self._discover_gemini_cli()
        
        return None
    
    def _discover_claude_code(self) -> Optional[ClientConfig]:
        """Discover Claude Code CLI configuration."""
        # Check for global config file
        config_path = Path.home() / ".claude.json"
        
        # Also check for local settings
        local_settings = Path.home() / ".claude" / "settings.json"
        
        # Use the primary config file if it exists, otherwise the settings file
        if config_path.exists():
            return ClientConfig(
                client_type=ClientType.CLAUDE_CODE,
                config_path=config_path,
                is_available=True
            )
        elif local_settings.exists() or local_settings.parent.exists():
            # Create the main config file path even if it doesn't exist yet
            return ClientConfig(
                client_type=ClientType.CLAUDE_CODE,
                config_path=config_path,
                is_available=True
            )
        
        return None
    
    def _discover_claude_desktop(self, system: str) -> Optional[ClientConfig]:
        """Discover Claude Desktop configuration."""
        if system == "darwin":  # macOS
            config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        elif system == "windows":
            config_path = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
        else:  # Linux
            config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
        
        # Check if Claude Desktop is likely installed
        if system == "darwin":
            app_path = Path("/Applications/Claude.app")
            is_available = app_path.exists() or config_path.exists() or config_path.parent.exists()
        elif system == "windows":
            # Check common Windows installation paths
            app_paths = [
                Path.home() / "AppData" / "Local" / "Claude" / "Claude.exe",
                Path("C:/Program Files/Claude/Claude.exe"),
                Path("C:/Program Files (x86)/Claude/Claude.exe"),
            ]
            is_available = any(p.exists() for p in app_paths) or config_path.exists() or config_path.parent.exists()
        else:
            # For Linux, just check if config directory exists or can be created
            is_available = config_path.exists() or config_path.parent.exists()
        
        if is_available:
            return ClientConfig(
                client_type=ClientType.CLAUDE_DESKTOP,
                config_path=config_path,
                is_available=True
            )
        
        return None
    
    def _discover_cursor(self, system: str) -> Optional[ClientConfig]:
        """Discover Cursor configuration."""
        # Check for global config
        global_config = Path.home() / ".cursor" / "mcp.json"
        
        # Check if Cursor is installed
        if system == "darwin":
            app_path = Path("/Applications/Cursor.app")
            is_available = app_path.exists() or global_config.exists() or global_config.parent.exists()
        elif system == "windows":
            app_paths = [
                Path.home() / "AppData" / "Local" / "Programs" / "cursor" / "Cursor.exe",
                Path("C:/Program Files/Cursor/Cursor.exe"),
            ]
            is_available = any(p.exists() for p in app_paths) or global_config.exists() or global_config.parent.exists()
        else:
            # Linux installation paths
            app_paths = [
                Path.home() / ".local" / "share" / "cursor",
                Path("/usr/local/bin/cursor"),
                Path("/usr/bin/cursor"),
            ]
            is_available = any(p.exists() for p in app_paths) or global_config.exists() or global_config.parent.exists()
        
        if is_available:
            return ClientConfig(
                client_type=ClientType.CURSOR,
                config_path=global_config,
                is_available=True
            )
        
        return None
    
    def _discover_vscode(self) -> Optional[ClientConfig]:
        """Discover VS Code configuration."""
        system = platform.system().lower()
        
        # VS Code Copilot uses the global settings.json file for MCP configuration
        if system == "darwin":  # macOS
            config_path = Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        elif system == "windows":
            config_path = Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json"
        else:  # Linux
            config_path = Path.home() / ".config" / "Code" / "User" / "settings.json"
        
        # Check if VS Code is available by looking for the command or config file
        import shutil
        vscode_available = (
            shutil.which("code") is not None or
            shutil.which("code-insiders") is not None or
            config_path.exists() or
            Path("/Applications/Visual Studio Code.app").exists()  # macOS check
        )
        
        if vscode_available:
            return ClientConfig(
                client_type=ClientType.VSCODE,
                config_path=config_path,
                is_available=True
            )
        
        return None
    
    def _discover_gemini_cli(self) -> Optional[ClientConfig]:
        """Discover Gemini CLI configuration."""
        # Check both global and local settings paths as per official docs
        global_config = Path.home() / ".gemini" / "settings.json"
        local_config = Path.cwd() / ".gemini" / "settings.json"
        
        # Prefer local over global if both exist
        config_path = local_config if local_config.exists() else global_config
        
        # Check if gemini-cli is available by looking for the command
        import shutil
        gemini_available = (
            shutil.which("gemini") is not None or
            config_path.exists() or
            config_path.parent.exists()
        )
        
        if gemini_available:
            return ClientConfig(
                client_type=ClientType.GEMINI_CLI,
                config_path=config_path,
                is_available=True
            )
        
        return None
    
    def get_client(self, client_type: ClientType) -> ClientConfig:
        """Get a client configuration by type."""
        if client_type not in self._clients:
            raise ClientNotFoundError(f"Client {client_type.value} not found or not available")
        return self._clients[client_type]
    
    def get_available_clients(self) -> List[ClientConfig]:
        """Get all available client configurations."""
        return list(self._clients.values())
    
    def is_client_available(self, client_type: ClientType) -> bool:
        """Check if a client is available."""
        return client_type in self._clients
    
    def refresh(self) -> None:
        """Refresh the client discovery."""
        self._discover_clients()
    
    def add_custom_client(self, config: ClientConfig) -> None:
        """Add a custom client configuration."""
        self._clients[config.client_type] = config
    
    def __str__(self) -> str:
        available = [client.client_type.value for client in self._clients.values()]
        return f"Available clients: {', '.join(available) if available else 'none'}"