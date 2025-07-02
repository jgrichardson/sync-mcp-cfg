"""Remove command for removing MCP servers."""

from typing import List, Optional

import click
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from ...clients import get_client_handler
from ...core.exceptions import ClientHandlerError, ClientNotFoundError
from ...core.models import ClientType

console = Console()


@click.command()
@click.argument('name')
@click.option(
    '--clients',
    '-c',
    multiple=True,
    type=click.Choice([ct.value for ct in ClientType]),
    help='Target clients (if not specified, will remove from all)',
)
@click.option('--force', '-f', is_flag=True, help='Force removal without confirmation')
@click.pass_context
def remove_command(ctx: click.Context, name: str, clients: tuple, force: bool) -> None:
    """Remove an MCP server from one or more clients.

    NAME: Name of the MCP server to remove

    Examples:
      sync-mcp-cfg remove filesystem
      sync-mcp-cfg remove weather --clients claude-code --clients cursor
    """
    registry = ctx.obj['registry']

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
        # Use all available clients
        available_clients = registry.get_available_clients()
        target_clients = [client.client_type for client in available_clients]

    if not target_clients:
        console.print("[red]No target clients specified or available.[/red]")
        return

    # Find servers to remove
    servers_to_remove = []
    for client_type in target_clients:
        try:
            client_config = registry.get_client(client_type)
            handler_class = get_client_handler(client_type)
            handler = handler_class(client_config)

            server = handler.get_server(name)
            if server:
                servers_to_remove.append((client_type, server))

        except ClientNotFoundError:
            console.print(f"[yellow]Client {client_type.value} not available[/yellow]")
        except Exception as e:
            console.print(f"[red]Error checking {client_type.value}: {e}[/red]")

    if not servers_to_remove:
        console.print(
            f"[yellow]Server '{name}' not found in any of the specified clients.[/yellow]"
        )
        return

    # Show what will be removed
    console.print(f"\n[bold]Server '{name}' found in:[/bold]")
    table = Table()
    table.add_column("Client")
    table.add_column("Command")
    table.add_column("Type")

    for client_type, server in servers_to_remove:
        table.add_row(
            client_type.value,
            (
                f"{server.command} {' '.join(server.args)}"
                if server.args
                else server.command
            ),
            server.server_type.value,
        )

    console.print(table)

    # Confirm removal
    if not force:
        if not Confirm.ask(
            f"\nRemove server '{name}' from {len(servers_to_remove)} client(s)?"
        ):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

    # Remove servers
    success_count = 0
    for client_type, server in servers_to_remove:
        try:
            client_config = registry.get_client(client_type)
            handler_class = get_client_handler(client_type)
            handler = handler_class(client_config)

            if handler.remove_server(name):
                console.print(
                    f"[green]✓ Removed '{name}' from {client_type.value}[/green]"
                )
                success_count += 1
            else:
                console.print(
                    f"[yellow]! Server '{name}' not found in {client_type.value}[/yellow]"
                )

        except ClientHandlerError as e:
            console.print(
                f"[red]✗ Failed to remove from {client_type.value}: {e}[/red]"
            )
        except Exception as e:
            console.print(
                f"[red]✗ Unexpected error with {client_type.value}: {e}[/red]"
            )

    if success_count > 0:
        console.print(
            f"\n[bold green]Successfully removed server from {success_count} client(s)[/bold green]"
        )
    else:
        console.print("\n[red]Failed to remove server from any clients[/red]")


@click.command()
@click.option(
    '--client',
    '-c',
    type=click.Choice([ct.value for ct in ClientType]),
    help='Target client (if not specified, will prompt)',
)
@click.option('--force', '-f', is_flag=True, help='Force removal without confirmation')
@click.pass_context
def remove_interactive(ctx: click.Context, client: Optional[str], force: bool) -> None:
    """Remove an MCP server interactively."""
    registry = ctx.obj['registry']

    console.print("[bold blue]Remove MCP Server - Interactive Mode[/bold blue]")

    # Select client if not specified
    if not client:
        available_clients = registry.get_available_clients()
        if not available_clients:
            console.print("[red]No MCP clients found on this system.[/red]")
            return

        console.print("\nSelect client:")
        for i, client_config in enumerate(available_clients, 1):
            console.print(f"{i}. {client_config.client_type.value}")

        while True:
            try:
                selection = int(input("Enter client number: "))
                if 1 <= selection <= len(available_clients):
                    client_type = available_clients[selection - 1].client_type
                    break
                else:
                    console.print("[red]Invalid selection.[/red]")
            except (ValueError, IndexError):
                console.print("[red]Invalid input. Please enter a number.[/red]")
    else:
        client_type = ClientType(client)

    # Get servers for the selected client
    try:
        client_config = registry.get_client(client_type)
        handler_class = get_client_handler(client_type)
        handler = handler_class(client_config)

        servers = handler.load_servers()
        if not servers:
            console.print(f"[yellow]No servers found in {client_type.value}.[/yellow]")
            return

    except ClientNotFoundError:
        console.print(f"[red]Client {client_type.value} not available.[/red]")
        return
    except Exception as e:
        console.print(f"[red]Error loading servers from {client_type.value}: {e}[/red]")
        return

    # Show servers and let user select
    console.print(f"\n[bold]Servers in {client_type.value}:[/bold]")
    table = Table()
    table.add_column("#")
    table.add_column("Name")
    table.add_column("Command")
    table.add_column("Type")
    table.add_column("Enabled")

    for i, server in enumerate(servers, 1):
        table.add_row(
            str(i),
            server.name,
            (
                f"{server.command} {' '.join(server.args)}"
                if server.args
                else server.command
            ),
            server.server_type.value,
            "✓" if server.enabled else "✗",
        )

    console.print(table)

    # Select server to remove
    while True:
        try:
            selection = int(
                input(f"\nEnter server number to remove (1-{len(servers)}): ")
            )
            if 1 <= selection <= len(servers):
                server_to_remove = servers[selection - 1]
                break
            else:
                console.print("[red]Invalid selection.[/red]")
        except (ValueError, IndexError):
            console.print("[red]Invalid input. Please enter a number.[/red]")

    # Confirm removal
    if not force:
        if not Confirm.ask(
            f"Remove server '{server_to_remove.name}' from {client_type.value}?"
        ):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

    # Remove server
    try:
        if handler.remove_server(server_to_remove.name):
            console.print(
                f"[green]✓ Removed '{server_to_remove.name}' from {client_type.value}[/green]"
            )
        else:
            console.print(
                f"[yellow]Server '{server_to_remove.name}' not found.[/yellow]"
            )
    except Exception as e:
        console.print(f"[red]Error removing server: {e}[/red]")
