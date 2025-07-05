"""Add command for adding MCP servers."""

from typing import List, Optional

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ...clients import get_client_handler
from ...core.exceptions import ClientHandlerError, ClientNotFoundError
from ...core.models import ClientType, MCPServer, MCPServerType

console = Console()


@click.command()
@click.argument('name')
@click.argument('command')
@click.option('--args', '-a', multiple=True, help='Command arguments')
@click.option('--env', '-e', multiple=True, help='Environment variables (KEY=VALUE)')
@click.option(
    '--type',
    'server_type',
    type=click.Choice(['stdio', 'sse', 'http']),
    default='stdio',
    help='Server transport type',
)
@click.option('--url', help='URL for SSE/HTTP servers')
@click.option(
    '--clients',
    '-c',
    multiple=True,
    type=click.Choice([ct.value for ct in ClientType]),
    help='Target clients (if not specified, will prompt)',
)
@click.option('--description', '-d', help='Server description')
@click.option('--disabled', is_flag=True, help='Add server as disabled')
@click.pass_context
def add_command(
    ctx: click.Context,
    name: str,
    command: str,
    args: tuple,
    env: tuple,
    server_type: str,
    url: Optional[str],
    clients: tuple,
    description: Optional[str],
    disabled: bool,
) -> None:
    """Add an MCP server to one or more clients.

    NAME: Unique name for the MCP server
    COMMAND: Command to execute the server

    Examples:
      sync-mcp-cfg add filesystem npx -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/path/to/dir"
      sync-mcp-cfg add weather node -a "/path/to/weather/server.js" -e "API_KEY=your-key"
    """
    registry = ctx.obj['registry']

    # Parse environment variables
    env_dict = {}
    for env_var in env:
        if '=' not in env_var:
            console.print(f"[red]Invalid environment variable format: {env_var}[/red]")
            console.print("Use format: KEY=VALUE")
            return
        key, value = env_var.split('=', 1)
        env_dict[key] = value

    # Validate URL for SSE/HTTP servers
    if server_type in ('sse', 'http') and not url:
        console.print(f"[red]URL is required for {server_type} servers[/red]")
        return

    # Create server object
    try:
        server = MCPServer(
            name=name,
            command=command,
            args=list(args),
            env=env_dict,
            server_type=MCPServerType(server_type),
            url=url,
            enabled=not disabled,
            description=description,
        )
    except ValueError as e:
        console.print(f"[red]Invalid server configuration: {e}[/red]")
        return

    # Determine target clients
    target_clients = []
    if clients:
        for client_name in clients:
            try:
                client_type = ClientType(client_name)
                target_clients.append(client_type)
            except ValueError:
                console.print(f"[red]Invalid client type: {client_name}[/red]")
                return
    else:
        # Prompt user to select clients
        available_clients = registry.get_available_clients()
        if not available_clients:
            console.print("[red]No MCP clients found on this system.[/red]")
            return

        console.print(f"\n[bold]Add server '{name}' to which clients?[/bold]")
        for i, client in enumerate(available_clients, 1):
            console.print(f"{i}. {client.client_type.value}")

        while True:
            try:
                selection = Prompt.ask(
                    "Enter client numbers (comma-separated) or 'all'"
                )
                if selection.lower() == 'all':
                    target_clients = [
                        client.client_type for client in available_clients
                    ]
                    break
                else:
                    indices = [int(x.strip()) for x in selection.split(',')]
                    if all(1 <= i <= len(available_clients) for i in indices):
                        target_clients = [
                            available_clients[i - 1].client_type for i in indices
                        ]
                        break
                    else:
                        console.print(
                            "[red]Invalid selection. Please enter valid numbers.[/red]"
                        )
            except (ValueError, IndexError):
                console.print(
                    "[red]Invalid input. Please enter numbers separated by commas.[/red]"
                )

    # Add server to selected clients
    success_count = 0
    for client_type in target_clients:
        try:
            client_config = registry.get_client(client_type)
            handler_class = get_client_handler(client_type)
            handler = handler_class(client_config)

            # Check if server already exists
            existing_server = handler.get_server(name)
            if existing_server:
                if not Confirm.ask(
                    f"Server '{name}' already exists in {client_type.value}. Overwrite?"
                ):
                    console.print(f"[yellow]Skipped {client_type.value}[/yellow]")
                    continue

            # Add server
            handler.add_server(server)
            console.print(f"[green]✓ Added '{name}' to {client_type.value}[/green]")
            success_count += 1

        except ClientNotFoundError:
            console.print(f"[red]✗ {client_type.value} not available[/red]")
        except ClientHandlerError as e:
            console.print(f"[red]✗ Failed to add to {client_type.value}: {e}[/red]")
        except Exception as e:
            console.print(
                f"[red]✗ Unexpected error with {client_type.value}: {e}[/red]"
            )

    if success_count > 0:
        console.print(
            f"\n[bold green]Successfully added server to {success_count} client(s)[/bold green]"
        )
    else:
        console.print("\n[red]Failed to add server to any clients[/red]")


@click.command()
@click.pass_context
def add_interactive(ctx: click.Context) -> None:
    """Add an MCP server interactively."""
    registry = ctx.obj['registry']

    console.print("[bold blue]Add MCP Server - Interactive Mode[/bold blue]")

    # Get server details
    name = Prompt.ask("Server name")
    command = Prompt.ask("Command")

    # Get arguments
    args = []
    console.print("\nEnter command arguments (press Enter on empty line to finish):")
    while True:
        arg = Prompt.ask("Argument", default="")
        if not arg:
            break
        args.append(arg)

    # Get environment variables
    env_dict = {}
    console.print(
        "\nEnter environment variables (press Enter on empty line to finish):"
    )
    while True:
        env_var = Prompt.ask("Environment variable (KEY=VALUE)", default="")
        if not env_var:
            break
        if '=' not in env_var:
            console.print("[red]Invalid format. Use KEY=VALUE[/red]")
            continue
        key, value = env_var.split('=', 1)
        env_dict[key] = value

    # Get server type
    server_type = Prompt.ask(
        "Server type", choices=['stdio', 'sse', 'http'], default='stdio'
    )

    # Get URL if needed
    url = None
    if server_type in ('sse', 'http'):
        url = Prompt.ask(f"URL for {server_type} server")

    # Get description
    description = Prompt.ask("Description (optional)", default="")
    if not description:
        description = None

    # Create server
    try:
        server = MCPServer(
            name=name,
            command=command,
            args=args,
            env=env_dict,
            server_type=MCPServerType(server_type),
            url=url,
            enabled=True,
            description=description,
        )
    except ValueError as e:
        console.print(f"[red]Invalid server configuration: {e}[/red]")
        return

    # Select clients
    available_clients = registry.get_available_clients()
    if not available_clients:
        console.print("[red]No MCP clients found on this system.[/red]")
        return

    console.print(f"\n[bold]Add server to which clients?[/bold]")
    selected_clients = []
    for client in available_clients:
        if Confirm.ask(f"Add to {client.client_type.value}?", default=True):
            selected_clients.append(client.client_type)

    if not selected_clients:
        console.print("[yellow]No clients selected. Server not added.[/yellow]")
        return

    # Add server to selected clients
    success_count = 0
    for client_type in selected_clients:
        try:
            client_config = registry.get_client(client_type)
            handler_class = get_client_handler(client_type)
            handler = handler_class(client_config)

            handler.add_server(server)
            console.print(f"[green]✓ Added '{name}' to {client_type.value}[/green]")
            success_count += 1

        except Exception as e:
            console.print(f"[red]✗ Failed to add to {client_type.value}: {e}[/red]")

    if success_count > 0:
        console.print(
            f"\n[bold green]Successfully added server to {success_count} client(s)[/bold green]"
        )
    else:
        console.print("\n[red]Failed to add server to any clients[/red]")
