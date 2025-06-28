"""List command for viewing MCP servers."""

from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from ...clients import get_client_handler
from ...core.exceptions import ClientNotFoundError
from ...core.models import ClientType

console = Console()


@click.command()
@click.option('--client', '-c', type=click.Choice([ct.value for ct in ClientType]),
              help='Show servers for specific client only')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'yaml']),
              default='table', help='Output format')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed server information')
@click.pass_context
def list_command(
    ctx: click.Context,
    client: Optional[str],
    output_format: str,
    detailed: bool
) -> None:
    """List MCP servers across clients.
    
    Examples:
      sync-mcp-cfg list
      sync-mcp-cfg list --client claude-code
      sync-mcp-cfg list --format json
    """
    registry = ctx.obj['registry']
    
    # Determine which clients to show
    if client:
        try:
            target_clients = [ClientType(client)]
        except ValueError:
            console.print(f"[red]Invalid client type: {client}[/red]")
            return
    else:
        available_clients = registry.get_available_clients()
        target_clients = [client.client_type for client in available_clients]
    
    if not target_clients:
        console.print("[yellow]No clients available.[/yellow]")
        return
    
    # Collect server data
    all_servers = {}
    for client_type in target_clients:
        try:
            client_config = registry.get_client(client_type)
            handler_class = get_client_handler(client_type)
            handler = handler_class(client_config)
            
            servers = handler.load_servers()
            all_servers[client_type] = servers
            
        except ClientNotFoundError:
            if client:  # Only show error if user specifically requested this client
                console.print(f"[red]Client {client_type.value} not available[/red]")
                return
            # Otherwise silently skip unavailable clients
            continue
        except Exception as e:
            console.print(f"[red]Error loading servers from {client_type.value}: {e}[/red]")
            if client:
                return
            continue
    
    # Output based on format
    if output_format == 'table':
        _show_table_format(all_servers, detailed)
    elif output_format == 'json':
        _show_json_format(all_servers)
    elif output_format == 'yaml':
        _show_yaml_format(all_servers)


def _show_table_format(all_servers: dict, detailed: bool) -> None:
    """Show servers in table format."""
    if not any(all_servers.values()):
        console.print("[yellow]No MCP servers found.[/yellow]")
        return
    
    for client_type, servers in all_servers.items():
        if not servers:
            continue
            
        console.print(f"\n[bold blue]{client_type.value}[/bold blue] ({len(servers)} servers)")
        
        table = Table()
        table.add_column("Name")
        table.add_column("Command")
        table.add_column("Type")
        table.add_column("Status")
        
        if detailed:
            table.add_column("Args")
            table.add_column("Env Vars")
            table.add_column("Description")
        
        for server in servers:
            command_display = server.command
            if server.args and not detailed:
                command_display += f" +{len(server.args)} args"
            
            status = "✓" if server.enabled else "✗"
            
            row = [
                server.name,
                command_display,
                server.server_type.value,
                status
            ]
            
            if detailed:
                args_display = " ".join(server.args) if server.args else ""
                env_display = ", ".join(f"{k}=***" for k in server.env.keys()) if server.env else ""
                description_display = server.description or ""
                
                row.extend([args_display, env_display, description_display])
            
            table.add_row(*row)
        
        console.print(table)


def _show_json_format(all_servers: dict) -> None:
    """Show servers in JSON format."""
    import json
    
    output = {}
    for client_type, servers in all_servers.items():
        output[client_type.value] = []
        for server in servers:
            server_dict = {
                "name": server.name,
                "command": server.command,
                "args": server.args,
                "env": server.env,
                "type": server.server_type.value,
                "enabled": server.enabled
            }
            if server.url:
                server_dict["url"] = server.url
            if server.description:
                server_dict["description"] = server.description
            
            output[client_type.value].append(server_dict)
    
    console.print(json.dumps(output, indent=2))


def _show_yaml_format(all_servers: dict) -> None:
    """Show servers in YAML format."""
    try:
        import yaml
    except ImportError:
        console.print("[red]PyYAML not installed. Install with: pip install PyYAML[/red]")
        return
    
    output = {}
    for client_type, servers in all_servers.items():
        output[client_type.value] = []
        for server in servers:
            server_dict = {
                "name": server.name,
                "command": server.command,
                "args": server.args,
                "env": server.env,
                "type": server.server_type.value,
                "enabled": server.enabled
            }
            if server.url:
                server_dict["url"] = server.url
            if server.description:
                server_dict["description"] = server.description
            
            output[client_type.value].append(server_dict)
    
    console.print(yaml.dump(output, default_flow_style=False))


@click.command()
@click.option('--client', '-c', type=click.Choice([ct.value for ct in ClientType]),
              help='Show servers for specific client only')
@click.pass_context
def list_detailed(ctx: click.Context, client: Optional[str]) -> None:
    """List MCP servers with detailed information."""
    # Call the main list command with detailed flag
    ctx.invoke(list_command, client=client, output_format='table', detailed=True)


@click.command()
@click.pass_context
def list_summary(ctx: click.Context) -> None:
    """Show a summary of MCP servers across all clients."""
    registry = ctx.obj['registry']
    
    console.print("[bold blue]MCP Server Summary[/bold blue]")
    console.print("=" * 50)
    
    available_clients = registry.get_available_clients()
    if not available_clients:
        console.print("[yellow]No MCP clients found.[/yellow]")
        return
    
    total_servers = 0
    unique_servers = set()
    
    for client_config in available_clients:
        try:
            handler_class = get_client_handler(client_config.client_type)
            handler = handler_class(client_config)
            servers = handler.load_servers()
            
            server_count = len(servers)
            total_servers += server_count
            
            for server in servers:
                unique_servers.add(server.name)
            
            console.print(f"{client_config.client_type.value}: {server_count} servers")
            
        except Exception as e:
            console.print(f"{client_config.client_type.value}: Error - {e}")
    
    console.print(f"\nTotal servers: {total_servers}")
    console.print(f"Unique server names: {len(unique_servers)}")
    
    if len(unique_servers) < total_servers:
        console.print(f"[yellow]Note: {total_servers - len(unique_servers)} duplicate server names detected[/yellow]")