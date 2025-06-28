"""Cursor client handler with dual format support."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..core.exceptions import ClientHandlerError, ConfigurationError
from ..core.models import ClientConfig, MCPServer, MCPServerType
from .base import BaseClientHandler


class CursorHandler(BaseClientHandler):
    """Handler for Cursor MCP server configurations.
    
    Supports both Cursor native format and Claude-compatible format:
    - Native: {"servers": [...]}
    - Claude-compatible: {"mcpServers": {...}}
    """
    
    def _detect_config_format(self, config_data: dict) -> str:
        """Detect which MCP format the config uses.
        
        Returns:
            'claude' if using mcpServers format
            'cursor' if using servers format
            'both' if both formats exist (problematic)
            'none' if no MCP config found
        """
        has_mcp_servers = 'mcpServers' in config_data and config_data['mcpServers']
        has_servers = 'servers' in config_data and config_data['servers']
        
        if has_mcp_servers and has_servers:
            return 'both'
        elif has_mcp_servers:
            return 'claude'
        elif has_servers:
            return 'cursor'
        else:
            return 'none'
    
    def load_servers(self) -> List[MCPServer]:
        """Load MCP servers from Cursor configuration."""
        if not self.config_exists():
            return []
        
        try:
            with open(self.config.config_path, 'r') as f:
                config_data = json.load(f)
            
            servers = []
            config_format = self._detect_config_format(config_data)
            
            if config_format == 'both':
                # Load from both formats but warn about the conflict
                servers.extend(self._load_claude_format(config_data))
                servers.extend(self._load_cursor_format(config_data))
            elif config_format == 'claude':
                servers = self._load_claude_format(config_data)
            elif config_format == 'cursor':
                servers = self._load_cursor_format(config_data)
            # 'none' returns empty list
            
            return servers
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ClientHandlerError(f"Failed to load Cursor configuration: {e}")
    
    def _load_claude_format(self, config_data: dict) -> List[MCPServer]:
        """Load servers from Claude-compatible mcpServers format."""
        servers = []
        mcp_servers = config_data.get('mcpServers', {})
        
        for name, server_config in mcp_servers.items():
            command = server_config.get('command', '')
            args = server_config.get('args', [])
            env = server_config.get('env', {})
            server_type = server_config.get('type', 'stdio')
            url = server_config.get('url')
            # Claude format doesn't have explicit enabled field
            enabled = not server_config.get('disabled', False)
            
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
                enabled=enabled
            )
            servers.append(server)
        
        return servers
    
    def _load_cursor_format(self, config_data: dict) -> List[MCPServer]:
        """Load servers from Cursor native servers format."""
        servers = []
        server_list = config_data.get('servers', [])
        
        for server_config in server_list:
            name = server_config.get('name', '')
            server_type = server_config.get('type', 'command')
            command = server_config.get('command', '')
            enabled = server_config.get('enabled', True)
            
            # Cursor format combines command and args in single string
            if command:
                command_parts = command.split()
                if command_parts:
                    actual_command = command_parts[0]
                    args = command_parts[1:] if len(command_parts) > 1 else []
                else:
                    actual_command = command
                    args = []
            else:
                actual_command = ''
                args = []
            
            # Map server type (Cursor uses 'command' for stdio)
            if server_type == 'command':
                mcp_type = MCPServerType.STDIO
            elif server_type == 'sse':
                mcp_type = MCPServerType.SSE
            elif server_type == 'http':
                mcp_type = MCPServerType.HTTP
            else:
                mcp_type = MCPServerType.STDIO
            
            server = MCPServer(
                name=name,
                command=actual_command,
                args=args,
                env={},  # Cursor native format doesn't expose env vars
                server_type=mcp_type,
                enabled=enabled
            )
            servers.append(server)
        
        return servers
    
    def save_servers(self, servers: List[MCPServer]) -> None:
        """Save MCP servers to Cursor configuration."""
        self.ensure_config_dir()
        
        # Load existing configuration
        config_data = {"version": "1.0"}
        existing_format = 'cursor'  # Default to cursor format for new configs
        
        if self.config_exists():
            try:
                with open(self.config.config_path, 'r') as f:
                    config_data = json.load(f)
                existing_format = self._detect_config_format(config_data)
            except json.JSONDecodeError:
                config_data = {"version": "1.0"}
                existing_format = 'cursor'
        
        # Handle format conflicts
        if existing_format == 'both':
            # If both formats exist, preserve the mcpServers format and remove servers
            # This prioritizes the Claude-compatible format
            existing_format = 'claude'
            if 'servers' in config_data:
                del config_data['servers']
        
        # Save in the detected/preferred format
        if existing_format == 'claude':
            self._save_claude_format(config_data, servers)
        else:
            self._save_cursor_format(config_data, servers)
        
        try:
            with open(self.config.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            raise ClientHandlerError(f"Failed to save Cursor configuration: {e}")
    
    def _save_claude_format(self, config_data: dict, servers: List[MCPServer]) -> None:
        """Save servers in Claude-compatible mcpServers format."""
        mcp_servers = {}
        for server in servers:
            server_config = {
                'command': server.command,
                'args': server.args,
                'env': server.env,
            }
            
            # Add type if not stdio (default)
            if server.server_type != MCPServerType.STDIO:
                server_config['type'] = server.server_type.value
            
            # Add URL for SSE/HTTP servers
            if server.url:
                server_config['url'] = server.url
            
            # Add disabled flag if not enabled
            if not server.enabled:
                server_config['disabled'] = True
            
            mcp_servers[server.name] = server_config
        
        config_data['mcpServers'] = mcp_servers
    
    def _save_cursor_format(self, config_data: dict, servers: List[MCPServer]) -> None:
        """Save servers in Cursor native servers format."""
        server_list = []
        for server in servers:
            # Combine command and args for Cursor format
            if server.args:
                command_str = f"{server.command} {' '.join(server.args)}"
            else:
                command_str = server.command
            
            # Map server type
            if server.server_type == MCPServerType.STDIO:
                cursor_type = 'command'
            elif server.server_type == MCPServerType.SSE:
                cursor_type = 'sse'
            elif server.server_type == MCPServerType.HTTP:
                cursor_type = 'http'
            else:
                cursor_type = 'command'
            
            server_config = {
                'name': server.name,
                'type': cursor_type,
                'command': command_str,
                'enabled': server.enabled
            }
            
            server_list.append(server_config)
        
        config_data['servers'] = server_list
    
    def add_server(self, server: MCPServer) -> None:
        """Add a single MCP server to Cursor configuration."""
        servers = self.load_servers()
        
        # Remove existing server with same name
        servers = [s for s in servers if s.name != server.name]
        servers.append(server)
        
        self.save_servers(servers)
    
    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server from Cursor configuration."""
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
        """Validate Cursor configuration format."""
        if not self.config_exists():
            return True  # Empty config is valid
        
        try:
            with open(self.config.config_path, 'r') as f:
                config_data = json.load(f)
            
            config_format = self._detect_config_format(config_data)
            
            if config_format == 'claude':
                return self._validate_claude_format(config_data)
            elif config_format == 'cursor':
                return self._validate_cursor_format(config_data)
            elif config_format == 'both':
                # Both formats present - validate both
                return (self._validate_claude_format(config_data) and 
                       self._validate_cursor_format(config_data))
            else:
                return True  # No MCP config is valid
                
        except (json.JSONDecodeError, IOError):
            return False
    
    def _validate_claude_format(self, config_data: dict) -> bool:
        """Validate Claude-compatible mcpServers format."""
        mcp_servers = config_data.get('mcpServers', {})
        if not isinstance(mcp_servers, dict):
            return False
        
        for name, server_config in mcp_servers.items():
            if not isinstance(server_config, dict):
                return False
            
            # Check required fields
            if 'command' not in server_config:
                return False
            
            # Validate optional fields
            args = server_config.get('args')
            if args is not None and not isinstance(args, list):
                return False
            
            env = server_config.get('env')
            if env is not None and not isinstance(env, dict):
                return False
        
        return True
    
    def _validate_cursor_format(self, config_data: dict) -> bool:
        """Validate Cursor native servers format."""
        servers = config_data.get('servers', [])
        if not isinstance(servers, list):
            return False
        
        for server_config in servers:
            if not isinstance(server_config, dict):
                return False
            
            # Check required fields
            if 'name' not in server_config or 'command' not in server_config:
                return False
            
            # Validate optional fields
            server_type = server_config.get('type')
            if server_type is not None and server_type not in ['command', 'sse', 'http']:
                return False
            
            enabled = server_config.get('enabled')
            if enabled is not None and not isinstance(enabled, bool):
                return False
        
        return True
    
    def backup_config(self, backup_path: Optional[Path] = None) -> Path:
        """Create a backup of the current Cursor configuration."""
        if not self.config_exists():
            raise ClientHandlerError("No configuration file exists to backup")
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"cursor_mcp_backup_{timestamp}.json"
            backup_path = self.config.config_path.parent / "backups" / backup_filename
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(self.config.config_path, backup_path)
            return backup_path
        except IOError as e:
            raise ClientHandlerError(f"Failed to create backup: {e}")
    
    def restore_config(self, backup_path: Path) -> None:
        """Restore Cursor configuration from a backup."""
        if not backup_path.exists():
            raise ClientHandlerError(f"Backup file not found: {backup_path}")
        
        # Validate backup file before restoring
        try:
            with open(backup_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid backup file format: {e}")
        
        self.ensure_config_dir()
        
        try:
            shutil.copy2(backup_path, self.config.config_path)
        except IOError as e:
            raise ClientHandlerError(f"Failed to restore configuration: {e}")
    
    def get_config_format(self) -> str:
        """Get the current configuration format being used.
        
        Returns:
            'claude', 'cursor', 'both', or 'none'
        """
        if not self.config_exists():
            return 'none'
        
        try:
            with open(self.config.config_path, 'r') as f:
                config_data = json.load(f)
            return self._detect_config_format(config_data)
        except (json.JSONDecodeError, IOError):
            return 'none'