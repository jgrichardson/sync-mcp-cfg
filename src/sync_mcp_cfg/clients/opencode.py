"""OpenCode client handler."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..core.exceptions import ClientHandlerError, ConfigurationError
from ..core.models import ClientConfig, MCPServer, MCPServerType
from .base import BaseClientHandler


class OpenCodeHandler(BaseClientHandler):
    """Handler for OpenCode MCP server configurations."""

    def load_servers(self) -> List[MCPServer]:
        """Load MCP servers from OpenCode configuration."""
        if not self.config_exists():
            return []

        try:
            with open(self.config.config_path, "r") as f:
                config_data = json.load(f)

            servers = []
            mcp_config = config_data.get("mcp", {})

            for server_id, server_config in mcp_config.items():
                if not isinstance(server_config, dict):
                    continue

                server_type = server_config.get("type", "local")
                enabled = server_config.get("enabled", True)

                if server_type == "local":
                    # Local server configuration
                    command_list = server_config.get("command", [])
                    if not command_list:
                        continue

                    command = command_list[0] if command_list else ""
                    args = command_list[1:] if len(command_list) > 1 else []
                    env = server_config.get("environment", {})

                    server = MCPServer(
                        name=server_id,
                        command=command,
                        args=args,
                        env=env,
                        server_type=MCPServerType.STDIO,
                        enabled=enabled,
                    )

                elif server_type == "remote":
                    # Remote server configuration
                    url = server_config.get("url", "")
                    if not url:
                        continue

                    # OpenCode remote servers can be SSE or HTTP
                    # Default to SSE but detect HTTP from URL
                    if url.startswith("http://") and not "sse" in url:
                        mcp_type = MCPServerType.HTTP
                    else:
                        mcp_type = MCPServerType.SSE  # Default for remote

                    server = MCPServer(
                        name=server_id,
                        command="",  # Remote servers don't have commands
                        args=[],
                        env={},
                        server_type=mcp_type,
                        url=url,
                        enabled=enabled,
                    )
                else:
                    continue

                servers.append(server)

            return servers

        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ClientHandlerError(f"Failed to load OpenCode configuration: {e}")

    def save_servers(self, servers: List[MCPServer]) -> None:
        """Save MCP servers to OpenCode configuration."""
        self.ensure_config_dir()

        # Load existing configuration to preserve other settings
        config_data = {}
        if self.config_exists():
            try:
                with open(self.config.config_path, "r") as f:
                    config_data = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start fresh
                config_data = {}

        # Ensure schema is set
        if "$schema" not in config_data:
            config_data["$schema"] = "https://opencode.ai/config.json"

        # Convert servers to OpenCode format
        mcp_config = {}
        for server in servers:
            if server.server_type == MCPServerType.STDIO and server.command:
                # Local server
                command_list = [server.command] + server.args
                server_config = {
                    "type": "local",
                    "command": command_list,
                    "enabled": server.enabled,
                }

                if server.env:
                    server_config["environment"] = server.env

            elif (
                server.server_type in (MCPServerType.SSE, MCPServerType.HTTP)
                and server.url
            ):
                # Remote server
                server_config = {
                    "type": "remote",
                    "url": server.url,
                    "enabled": server.enabled,
                }
            else:
                # Skip invalid configurations
                continue

            mcp_config[server.name] = server_config

        config_data["mcp"] = mcp_config

        try:
            with open(self.config.config_path, "w") as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            raise ClientHandlerError(f"Failed to save OpenCode configuration: {e}")

    def add_server(self, server: MCPServer) -> None:
        """Add a single MCP server to OpenCode configuration."""
        servers = self.load_servers()

        # Remove existing server with same name
        servers = [s for s in servers if s.name != server.name]
        servers.append(server)

        self.save_servers(servers)

    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server from OpenCode configuration."""
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
        """Validate OpenCode configuration format."""
        if not self.config_exists():
            return True  # Empty config is valid

        try:
            with open(self.config.config_path, "r") as f:
                config_data = json.load(f)

            # Check if mcp section exists and is properly formatted
            mcp_config = config_data.get("mcp", {})
            if not isinstance(mcp_config, dict):
                return False

            # Validate each server configuration
            for server_id, server_config in mcp_config.items():
                if not isinstance(server_config, dict):
                    return False

                server_type = server_config.get("type")
                if server_type not in ("local", "remote"):
                    return False

                if server_type == "local":
                    # Validate local server
                    command = server_config.get("command")
                    if not isinstance(command, list) or not command:
                        return False

                    environment = server_config.get("environment")
                    if environment is not None and not isinstance(environment, dict):
                        return False

                elif server_type == "remote":
                    # Validate remote server
                    url = server_config.get("url")
                    if not isinstance(url, str) or not url:
                        return False

                # Validate enabled field
                enabled = server_config.get("enabled", True)
                if not isinstance(enabled, bool):
                    return False

            return True

        except (json.JSONDecodeError, IOError):
            return False

    def backup_config(self, backup_path: Optional[Path] = None) -> Path:
        """Create a backup of the current OpenCode configuration."""
        if not self.config_exists():
            raise ClientHandlerError("No configuration file exists to backup")

        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"opencode_config_backup_{timestamp}.json"
            backup_path = self.config.config_path.parent / "backups" / backup_filename

        backup_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(self.config.config_path, backup_path)
            return backup_path
        except IOError as e:
            raise ClientHandlerError(f"Failed to create backup: {e}")

    def restore_config(self, backup_path: Path) -> None:
        """Restore OpenCode configuration from a backup."""
        if not backup_path.exists():
            raise ClientHandlerError(f"Backup file not found: {backup_path}")

        # Validate backup file before restoring
        try:
            with open(backup_path, "r") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid backup file format: {e}")

        self.ensure_config_dir()

        try:
            shutil.copy2(backup_path, self.config.config_path)
        except IOError as e:
            raise ClientHandlerError(f"Failed to restore configuration: {e}")
