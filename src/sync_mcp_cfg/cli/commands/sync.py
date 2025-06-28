"""Sync command for synchronizing MCP servers between clients."""

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
@click.option('--from', 'source_client', type=click.Choice([ct.value for ct in ClientType]),
              required=True, help='Source client to sync from')
@click.option('--to', 'target_clients', multiple=True,
              type=click.Choice([ct.value for ct in ClientType]),
              help='Target clients to sync to (if not specified, will sync to all available)')
@click.option('--servers', '-s', multiple=True,
              help='Specific servers to sync (if not specified, will sync all)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing servers without confirmation')
@click.option('--backup', is_flag=True, default=True, help='Create backup before sync')
@click.option('--dry-run', is_flag=True, help='Show what would be synced without making changes')
@click.pass_context
def sync_command(
    ctx: click.Context,
    source_client: str,
    target_clients: tuple,
    servers: tuple,
    overwrite: bool,
    backup: bool,
    dry_run: bool
) -> None:
    """Sync MCP servers from one client to others.
    
    Examples:
      sync-mcp-cfg sync --from claude-code --to cursor --to vscode
      sync-mcp-cfg sync --from claude-desktop --servers filesystem --servers weather
      sync-mcp-cfg sync --from cursor --dry-run
    """
    registry = ctx.obj['registry']
    
    try:
        source_client_type = ClientType(source_client)
    except ValueError:
        console.print(f"[red]Invalid source client: {source_client}[/red]")
        return
    
    # Get source client and load servers
    try:
        source_config = registry.get_client(source_client_type)
        source_handler_class = get_client_handler(source_client_type)
        source_handler = source_handler_class(source_config)
        
        source_servers = source_handler.load_servers()
        if not source_servers:
            console.print(f"[yellow]No servers found in {source_client}[/yellow]")
            return
            
    except ClientNotFoundError:
        console.print(f"[red]Source client {source_client} not available[/red]")
        return
    except Exception as e:
        console.print(f"[red]Error loading servers from {source_client}: {e}[/red]")
        return
    
    # Filter servers if specific ones requested
    if servers:
        requested_servers = set(servers)
        available_servers = {s.name for s in source_servers}
        missing_servers = requested_servers - available_servers
        
        if missing_servers:
            console.print(f"[red]Servers not found in {source_client}: {', '.join(missing_servers)}[/red]")
            return
        
        source_servers = [s for s in source_servers if s.name in requested_servers]
    
    # Determine target clients
    if target_clients:
        target_client_types = []
        for client_name in target_clients:
            try:
                client_type = ClientType(client_name)
                if client_type == source_client_type:
                    console.print(f"[yellow]Skipping source client {client_name}[/yellow]")
                    continue
                target_client_types.append(client_type)
            except ValueError:
                console.print(f"[red]Invalid target client: {client_name}[/red]")
                return
    else:
        # Sync to all available clients except source
        available_clients = registry.get_available_clients()
        target_client_types = [
            client.client_type for client in available_clients
            if client.client_type != source_client_type
        ]
    
    if not target_client_types:
        console.print("[yellow]No target clients specified or available[/yellow]")
        return
    
    # Show sync plan
    console.print(f"\n[bold blue]Sync Plan[/bold blue]")
    console.print(f"Source: {source_client} ({len(source_servers)} servers)")
    console.print(f"Targets: {', '.join(ct.value for ct in target_client_types)}")
    
    if servers:
        console.print(f"Servers: {', '.join(servers)}")
    else:
        console.print("Servers: All")
    
    # Show servers to sync
    table = Table(title="Servers to Sync")
    table.add_column("Name")
    table.add_column("Command")
    table.add_column("Type")
    table.add_column("Args")
    
    for server in source_servers:
        table.add_row(
            server.name,
            server.command,
            server.server_type.value,
            str(len(server.args)) if server.args else "0"
        )
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]Dry run mode - no changes will be made[/yellow]")
        return
    
    # Confirm sync
    if not overwrite:
        if not Confirm.ask(f"\nSync {len(source_servers)} servers to {len(target_client_types)} clients?"):
            console.print("[yellow]Sync cancelled[/yellow]")
            return
    
    # Perform sync
    success_count = 0
    total_operations = 0
    
    for target_client_type in target_client_types:
        try:
            target_config = registry.get_client(target_client_type)
            target_handler_class = get_client_handler(target_client_type)
            target_handler = target_handler_class(target_config)
            
            # Create backup if requested
            if backup:
                try:
                    backup_path = target_handler.backup_config()
                    console.print(f"[green]✓ Created backup for {target_client_type.value}: {backup_path}[/green]")
                except Exception as e:
                    console.print(f"[yellow]⚠ Failed to create backup for {target_client_type.value}: {e}[/yellow]")
            
            # Load existing servers to check for conflicts
            existing_servers = target_handler.load_servers()
            existing_names = {s.name for s in existing_servers}
            
            # Sync each server
            client_success = 0
            for server in source_servers:
                total_operations += 1
                
                # Check for conflicts
                if server.name in existing_names and not overwrite:
                    if not Confirm.ask(f"Server '{server.name}' exists in {target_client_type.value}. Overwrite?"):
                        console.print(f"[yellow]- Skipped '{server.name}' in {target_client_type.value}[/yellow]")
                        continue
                
                try:
                    target_handler.add_server(server)
                    console.print(f"[green]✓ Synced '{server.name}' to {target_client_type.value}[/green]")
                    client_success += 1
                except Exception as e:
                    console.print(f"[red]✗ Failed to sync '{server.name}' to {target_client_type.value}: {e}[/red]")
            
            if client_success > 0:
                success_count += client_success
                console.print(f"[bold green]✓ Successfully synced {client_success} servers to {target_client_type.value}[/bold green]")
            
        except ClientNotFoundError:
            console.print(f"[red]✗ Target client {target_client_type.value} not available[/red]")
        except Exception as e:
            console.print(f"[red]✗ Error syncing to {target_client_type.value}: {e}[/red]")
    
    # Summary
    console.print(f"\n[bold]Sync Complete[/bold]")
    console.print(f"Successfully synced: {success_count}/{total_operations} operations")
    
    if success_count == total_operations:
        console.print("[bold green]All operations successful![/bold green]")
    elif success_count > 0:
        console.print("[yellow]Some operations failed. Check output above for details.[/yellow]")
    else:
        console.print("[red]All operations failed.[/red]")


@click.command()
@click.pass_context
def sync_interactive(ctx: click.Context) -> None:
    """Sync MCP servers interactively."""
    registry = ctx.obj['registry']
    
    console.print("[bold blue]Sync MCP Servers - Interactive Mode[/bold blue]")
    
    available_clients = registry.get_available_clients()
    if len(available_clients) < 2:
        console.print("[red]At least 2 clients are required for syncing.[/red]")
        return
    
    # Select source client
    console.print("\nSelect source client:")
    for i, client in enumerate(available_clients, 1):
        try:
            handler_class = get_client_handler(client.client_type)
            handler = handler_class(client)
            servers = handler.load_servers()
            console.print(f"{i}. {client.client_type.value} ({len(servers)} servers)")
        except Exception:
            console.print(f"{i}. {client.client_type.value} (error loading)")
    
    while True:
        try:
            selection = int(input("Enter source client number: "))
            if 1 <= selection <= len(available_clients):
                source_client = available_clients[selection-1]
                break
            else:
                console.print("[red]Invalid selection.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")
    
    # Load source servers
    try:
        source_handler_class = get_client_handler(source_client.client_type)
        source_handler = source_handler_class(source_client)
        source_servers = source_handler.load_servers()
        
        if not source_servers:
            console.print(f"[yellow]No servers found in {source_client.client_type.value}[/yellow]")
            return
    except Exception as e:
        console.print(f"[red]Error loading servers: {e}[/red]")
        return
    
    # Select servers to sync
    console.print(f"\n[bold]Servers in {source_client.client_type.value}:[/bold]")
    for i, server in enumerate(source_servers, 1):
        console.print(f"{i}. {server.name} ({server.server_type.value})")
    
    console.print("\nSelect servers to sync:")
    console.print("Enter 'all' for all servers, or comma-separated numbers (e.g., 1,3,5)")
    
    while True:
        selection = input("Selection: ").strip()
        if selection.lower() == 'all':
            selected_servers = source_servers
            break
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(',')]
                if all(1 <= i <= len(source_servers) for i in indices):
                    selected_servers = [source_servers[i-1] for i in indices]
                    break
                else:
                    console.print("[red]Invalid selection. Please enter valid numbers.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter numbers separated by commas.[/red]")
    
    # Select target clients
    target_options = [c for c in available_clients if c.client_type != source_client.client_type]
    console.print(f"\n[bold]Select target clients:[/bold]")
    
    target_clients = []
    for client in target_options:
        if Confirm.ask(f"Sync to {client.client_type.value}?", default=True):
            target_clients.append(client)
    
    if not target_clients:
        console.print("[yellow]No target clients selected.[/yellow]")
        return
    
    # Options
    overwrite = Confirm.ask("Overwrite existing servers without prompting?", default=False)
    backup = Confirm.ask("Create backup before sync?", default=True)
    
    # Show summary and confirm
    console.print(f"\n[bold]Sync Summary:[/bold]")
    console.print(f"Source: {source_client.client_type.value}")
    console.print(f"Servers: {len(selected_servers)}")
    console.print(f"Targets: {', '.join(c.client_type.value for c in target_clients)}")
    console.print(f"Overwrite: {'Yes' if overwrite else 'Prompt'}")
    console.print(f"Backup: {'Yes' if backup else 'No'}")
    
    if not Confirm.ask("\nProceed with sync?"):
        console.print("[yellow]Sync cancelled.[/yellow]")
        return
    
    # Perform sync using the main sync logic
    ctx.invoke(
        sync_command,
        source_client=source_client.client_type.value,
        target_clients=tuple(c.client_type.value for c in target_clients),
        servers=tuple(s.name for s in selected_servers),
        overwrite=overwrite,
        backup=backup,
        dry_run=False
    )