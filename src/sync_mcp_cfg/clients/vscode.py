"""VS Code Copilot client handler."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..core.exceptions import ClientHandlerError, ConfigurationError
from ..core.models import ClientConfig, MCPServer, MCPServerType
from .base import BaseClientHandler


class VSCodeHandler(BaseClientHandler):
    """Handler for VS Code Copilot MCP server configurations."""

    def load_servers(self) -> List[MCPServer]:
        """Load MCP servers from VS Code settings.json configuration."""
        if not self.config_exists():
            return []

        try:
            with open(self.config.config_path, 'r') as f:
                config_data = json.load(f)

            servers = []

            # VS Code Copilot stores MCP servers in settings.json under "mcp.servers"
            mcp_config = config_data.get('mcp', {})
            server_configs = mcp_config.get('servers', {})

            for name, server_config in server_configs.items():
                # Extract server configuration
                command = server_config.get('command', '')
                args = server_config.get('args', [])
                env = server_config.get('env', {})
                server_type = server_config.get('type', 'stdio')
                url = server_config.get('url')

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
                    enabled=True,  # VS Code doesn't have explicit enable/disable in MCP config
                    description=server_config.get('description', f"VS Code MCP Server"),
                )
                servers.append(server)

            return servers

        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ClientHandlerError(f"Failed to load VS Code configuration: {e}")

    def save_servers(self, servers: List[MCPServer]) -> None:
        """Save MCP servers to VS Code settings.json configuration."""
        self.ensure_config_dir()

        # Load existing configuration to preserve other VS Code settings
        config_data = {}
        if self.config_exists():
            try:
                with open(self.config.config_path, 'r') as f:
                    config_data = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start fresh
                config_data = {}

        # Convert servers to VS Code format
        server_configs = {}
        for server in servers:
            server_config = {
                'command': server.command,
                'args': server.args,
            }

            # Add env if not empty
            if server.env:
                server_config['env'] = server.env

            # Add type if not stdio (default)
            if server.server_type != MCPServerType.STDIO:
                server_config['type'] = server.server_type.value

            # Add URL for SSE/HTTP servers
            if server.url:
                server_config['url'] = server.url

            server_configs[server.name] = server_config

        # Ensure mcp section exists
        if 'mcp' not in config_data:
            config_data['mcp'] = {}

        config_data['mcp']['servers'] = server_configs

        try:
            with open(self.config.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            raise ClientHandlerError(f"Failed to save VS Code configuration: {e}")

    def add_server(self, server: MCPServer) -> None:
        """Add a single MCP server to VS Code configuration."""
        servers = self.load_servers()

        # Remove existing server with same name
        servers = [s for s in servers if s.name != server.name]
        servers.append(server)

        self.save_servers(servers)

    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server from VS Code configuration."""
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
        """Validate VS Code settings.json format."""
        if not self.config_exists():
            return True  # Empty config is valid

        try:
            with open(self.config.config_path, 'r') as f:
                config_data = json.load(f)

            # Check if mcp section exists and is properly formatted
            mcp_config = config_data.get('mcp', {})
            if not isinstance(mcp_config, dict):
                return False

            servers = mcp_config.get('servers', {})
            if not isinstance(servers, dict):
                return False

            # Validate each server configuration
            for name, server_config in servers.items():
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

        except (json.JSONDecodeError, IOError):
            return False

    def backup_config(self, backup_path: Optional[Path] = None) -> Path:
        """Create a backup of the current VS Code configuration."""
        if not self.config_exists():
            raise ClientHandlerError("No configuration file exists to backup")

        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"vscode_mcp_backup_{timestamp}.json"
            backup_path = self.config.config_path.parent / "backups" / backup_filename

        backup_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(self.config.config_path, backup_path)
            return backup_path
        except IOError as e:
            raise ClientHandlerError(f"Failed to create backup: {e}")

    def restore_config(self, backup_path: Path) -> None:
        """Restore VS Code configuration from a backup."""
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

    def set_workspace_config_path(self, workspace_path: Path) -> None:
        """Set the configuration path for a specific VS Code workspace."""
        new_config_path = workspace_path / ".vscode" / "mcp.json"
        self.config.config_path = new_config_path
