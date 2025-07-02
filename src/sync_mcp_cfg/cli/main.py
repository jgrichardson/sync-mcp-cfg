"""Main CLI entry point for sync-mcp-cfg."""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.traceback import install

from ..core.registry import ClientRegistry
from ..version import __version__
from .commands.add import add_command
from .commands.list import list_command
from .commands.remove import remove_command
from .commands.sync import sync_command

# Install rich traceback handler for better error display
install()

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--no-color', is_flag=True, help='Disable colored output')
@click.pass_context
def cli(ctx: click.Context, verbose: bool, no_color: bool) -> None:
    """Sync MCP Config - Manage and sync MCP Server configurations across AI clients.

    This tool helps you manage Model Context Protocol (MCP) server configurations
    across multiple AI clients including Claude Code, Claude Desktop, Cursor, and VS Code.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Store global options
    ctx.obj['verbose'] = verbose
    ctx.obj['no_color'] = no_color

    # Configure console
    if no_color:
        console._color_system = None

    # Initialize client registry
    try:
        ctx.obj['registry'] = ClientRegistry()
    except Exception as e:
        console.print(f"[red]Error initializing client registry: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show status of available MCP clients and their configurations."""
    registry: ClientRegistry = ctx.obj['registry']

    console.print("\n[bold blue]MCP Client Status[/bold blue]")
    console.print("=" * 50)

    available_clients = registry.get_available_clients()

    if not available_clients:
        console.print("[yellow]No MCP clients found on this system.[/yellow]")
        console.print("\nSupported clients:")
        console.print("• Claude Code CLI")
        console.print("• Claude Desktop")
        console.print("• Cursor")
        console.print("• VS Code with Copilot")
        return

    for client in available_clients:
        from ..clients import get_client_handler

        handler_class = get_client_handler(client.client_type)
        handler = handler_class(client)

        try:
            servers = handler.load_servers()
            server_count = len(servers)
            config_exists = handler.config_exists()

            status_icon = "✓" if config_exists else "○"
            console.print(f"\n{status_icon} [bold]{client.client_type.value}[/bold]")
            console.print(f"   Config: {client.config_path}")
            console.print(f"   Servers: {server_count}")

            if ctx.obj['verbose'] and servers:
                for server in servers:
                    enabled_icon = "✓" if server.enabled else "✗"
                    console.print(
                        f"     {enabled_icon} {server.name} ({server.server_type.value})"
                    )

        except Exception as e:
            console.print(f"\n✗ [bold red]{client.client_type.value}[/bold red]")
            console.print(f"   Error: {e}")


@cli.command()
@click.option('--config-dir', type=click.Path(), help='Configuration directory path')
@click.pass_context
def init(ctx: click.Context, config_dir: Optional[str]) -> None:
    """Initialize sync-mcp-cfg configuration."""
    import platformdirs
    from pathlib import Path

    if config_dir:
        app_config_dir = Path(config_dir)
    else:
        app_config_dir = Path(platformdirs.user_config_dir("sync-mcp-cfg"))

    app_config_dir.mkdir(parents=True, exist_ok=True)
    config_file = app_config_dir / "config.json"

    from ..core.models import AppConfig

    if config_file.exists():
        console.print(f"[yellow]Configuration already exists at {config_file}[/yellow]")
        return

    # Create default configuration
    app_config = AppConfig()
    app_config.save_to_file(config_file)

    console.print(f"[green]✓ Initialized configuration at {config_file}[/green]")
    console.print("\nNext steps:")
    console.print("1. Run 'sync-mcp-cfg status' to see available clients")
    console.print("2. Use 'sync-mcp-cfg add' to add MCP servers")
    console.print("3. Use 'sync-mcp-cfg sync' to sync configurations")


@cli.command()
@click.pass_context
def tui(ctx: click.Context) -> None:
    """Launch the text-based user interface."""
    try:
        from ..tui.app import SyncMCPApp

        app = SyncMCPApp(ctx.obj['registry'])
        app.run()
    except ImportError:
        console.print(
            "[red]TUI dependencies not installed. Install with: pip install sync-mcp-cfg[/red]"
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error launching TUI: {e}[/red]")
        sys.exit(1)


# Add commands from submodules
cli.add_command(add_command, name='add')
cli.add_command(remove_command, name='remove')
cli.add_command(list_command, name='list')
cli.add_command(sync_command, name='sync')


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            console.print_exception()
        sys.exit(1)


if __name__ == '__main__':
    main()
