"""Gemini CLI client handler."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..core.exceptions import ClientHandlerError, ConfigurationError
from ..core.models import ClientConfig, MCPServer, MCPServerType
from .base import BaseClientHandler


class GeminiCLIHandler(BaseClientHandler):
    """Handler for Gemini CLI MCP server configurations."""
    
    def load_servers(self) -> List[MCPServer]:
        """Load MCP servers from Gemini CLI configuration."""
        if not self.config_exists():
            return []
        
        try:
            with open(self.config.config_path, 'r') as f:
                config_data = json.load(f)
            
            servers = []
            
            # Gemini CLI typically stores MCP servers in a similar format to Claude
            # Adapt based on actual Gemini CLI configuration structure
            mcp_servers = config_data.get('mcpServers', {})
            
            for name, server_config in mcp_servers.items():
                # Extract server configuration
                command = server_config.get('command', '')
                args = server_config.get('args', [])
                env = server_config.get('env', {})
                server_type = server_config.get('type', 'stdio')
                url = server_config.get('url') or server_config.get('httpUrl')
                trust = server_config.get('trust', True)
                cwd = server_config.get('cwd')
                timeout = server_config.get('timeout')
                
                # Map server type
                if server_type == 'stdio':
                    mcp_type = MCPServerType.STDIO
                elif server_type == 'sse':
                    mcp_type = MCPServerType.SSE
                elif server_type == 'http':
                    mcp_type = MCPServerType.HTTP
                else:
                    mcp_type = MCPServerType.STDIO
                
                server = MCPServer(
                    name=name,
                    command=command,
                    args=args,
                    env=env,
                    server_type=mcp_type,
                    url=url,
                    enabled=trust,  # Use trust field as enabled
                    description=server_config.get('description', f"Gemini CLI MCP Server (timeout: {timeout}ms, cwd: {cwd})" if timeout or cwd else None)
                )
                servers.append(server)
            
            return servers
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ClientHandlerError(f"Failed to load Gemini CLI configuration: {e}")
    
    def save_servers(self, servers: List[MCPServer]) -> None:
        """Save MCP servers to Gemini CLI configuration."""
        self.ensure_config_dir()
        
        # Load existing configuration to preserve other settings
        config_data = {}
        if self.config_exists():
            try:
                with open(self.config.config_path, 'r') as f:
                    config_data = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start fresh
                config_data = {}
        
        # Convert servers to Gemini CLI format
        mcp_servers = {}
        for server in servers:
            server_config = {
                'command': server.command,
                'args': server.args,
                'env': server.env,
                'trust': server.enabled,  # Use enabled as trust
            }
            
            # Add type if not stdio (default)
            if server.server_type != MCPServerType.STDIO:
                server_config['type'] = server.server_type.value
            
            # Add URL for SSE/HTTP servers with correct field name
            if server.url:
                if server.server_type == MCPServerType.HTTP:
                    server_config['httpUrl'] = server.url
                else:
                    server_config['url'] = server.url
            
            mcp_servers[server.name] = server_config
        
        config_data['mcpServers'] = mcp_servers
        
        try:
            with open(self.config.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except OSError as e:
            raise ClientHandlerError(f"Failed to save Gemini CLI configuration: {e}")
    
    def add_server(self, server: MCPServer) -> None:
        """Add a single MCP server to Gemini CLI configuration."""
        servers = self.load_servers()
        
        # Remove existing server with same name
        servers = [s for s in servers if s.name != server.name]
        servers.append(server)
        
        self.save_servers(servers)
    
    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server from Gemini CLI configuration."""
        servers = self.load_servers()
        original_count = len(servers)
        
        servers = [s for s in servers if s.name != server_name]
        
        if len(servers) < original_count:
            self.save_servers(servers)
            return True
        return False
    
    def get_server(self, server_name: str) -> Optional[MCPServer]:
        """Get a specific MCP server by name."""
        servers = self.load_servers()
        for server in servers:
            if server.name == server_name:
                return server
        return None
    
    def validate_config(self) -> bool:
        """Validate Gemini CLI configuration format."""
        if not self.config_exists():
            return True  # Non-existent config is valid (will be created)
        
        try:
            with open(self.config.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Basic validation - should be a dict with optional mcpServers
            if not isinstance(config_data, dict):
                return False
            
            mcp_servers = config_data.get('mcpServers', {})
            if not isinstance(mcp_servers, dict):
                return False
            
            # Validate each server configuration
            for name, server_config in mcp_servers.items():
                if not isinstance(server_config, dict):
                    return False
                
                # Check required fields
                if 'command' not in server_config:
                    return False
                
                # Validate args if present
                if 'args' in server_config and not isinstance(server_config['args'], list):
                    return False
                
                # Validate env if present
                if 'env' in server_config and not isinstance(server_config['env'], dict):
                    return False
            
            return True
            
        except (json.JSONDecodeError, OSError):
            return False
    
    def backup_config(self, backup_path: Optional[Path] = None) -> Path:
        """Create a backup of the current Gemini CLI configuration."""
        if not self.config_exists():
            raise ClientHandlerError("Cannot backup non-existent configuration")
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.config.config_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / f"gemini_cli_config_{timestamp}.json"
        
        try:
            shutil.copy2(self.config.config_path, backup_path)
            return backup_path
        except OSError as e:
            raise ClientHandlerError(f"Failed to create backup: {e}")
    
    def restore_config(self, backup_path: Path) -> None:
        """Restore Gemini CLI configuration from a backup."""
        if not backup_path.exists():
            raise ClientHandlerError(f"Backup file not found: {backup_path}")
        
        # Validate backup before restoring
        try:
            with open(backup_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            raise ClientHandlerError(f"Invalid backup file format: {e}")
        
        try:
            self.ensure_config_dir()
            shutil.copy2(backup_path, self.config.config_path)
        except OSError as e:
            raise ClientHandlerError(f"Failed to restore configuration: {e}")
    
    @staticmethod
    def get_default_config_path() -> Path:
        """Get the default configuration path for Gemini CLI.
        
        Returns the global settings path as per official documentation.
        Local project settings would be at .gemini/settings.json.
        """
        return Path.home() / ".gemini" / "settings.json"
    
    @staticmethod
    def is_available() -> bool:
        """Check if Gemini CLI is available on the system."""
        try:
            import shutil
            return shutil.which("gemini") is not None
        except Exception:
            return False
