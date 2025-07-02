"""Text-based User Interface for sync-mcp-cfg."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Static, DataTable, Log
from textual.binding import Binding

from ..core.registry import ClientRegistry


class SyncMCPApp(App):
    """Main TUI application for sync-mcp-cfg."""

    TITLE = "Sync MCP Config"
    SUB_TITLE = "Manage MCP Server Configurations"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, registry: ClientRegistry):
        super().__init__()
        self.registry = registry

    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        yield Header()

        with Container(id="main-container"):
            with Vertical(id="left-panel"):
                yield Static("Clients", classes="panel-title")
                yield DataTable(id="clients-table")

            with Vertical(id="right-panel"):
                yield Static("Servers", classes="panel-title")
                yield DataTable(id="servers-table")

            with Horizontal(id="bottom-panel"):
                yield Button("Add Server", id="add-btn")
                yield Button("Remove Server", id="remove-btn")
                yield Button("Sync", id="sync-btn")
                yield Button("Refresh", id="refresh-btn")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application."""
        self.load_clients()
        self.load_servers()

    def load_clients(self) -> None:
        """Load available clients into the table."""
        clients_table = self.query_one("#clients-table", DataTable)
        clients_table.clear(columns=True)
        clients_table.add_columns("Client", "Status", "Servers")

        available_clients = self.registry.get_available_clients()

        for client in available_clients:
            from ..clients import get_client_handler

            handler_class = get_client_handler(client.client_type)
            handler = handler_class(client)

            try:
                servers = handler.load_servers()
                server_count = len(servers)
                status = "✓ Active" if handler.config_exists() else "○ Inactive"

                clients_table.add_row(
                    client.client_type.value, status, str(server_count)
                )
            except Exception as e:
                clients_table.add_row(
                    client.client_type.value, f"✗ Error: {str(e)[:20]}...", "0"
                )

    def load_servers(self) -> None:
        """Load all servers into the table."""
        servers_table = self.query_one("#servers-table", DataTable)
        servers_table.clear(columns=True)
        servers_table.add_columns("Server", "Command", "Clients")

        # Collect all servers from all clients
        all_servers = {}
        available_clients = self.registry.get_available_clients()

        for client in available_clients:
            from ..clients import get_client_handler

            handler_class = get_client_handler(client.client_type)
            handler = handler_class(client)

            try:
                servers = handler.load_servers()
                for server in servers:
                    if server.name not in all_servers:
                        all_servers[server.name] = {'server': server, 'clients': set()}
                    all_servers[server.name]['clients'].add(client.client_type.value)
            except Exception:
                continue

        # Add servers to table
        for server_name, server_data in all_servers.items():
            server = server_data['server']
            clients_list = ', '.join(sorted(server_data['clients']))

            servers_table.add_row(
                server_name,
                f"{server.command} {' '.join(server.args[:2])}...",
                clients_list,
            )

    def action_refresh(self) -> None:
        """Refresh all data."""
        self.load_clients()
        self.load_servers()
        self.notify("Data refreshed")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-btn":
            self.action_refresh()
        elif event.button.id == "add-btn":
            self.notify("Add server functionality coming soon!")
        elif event.button.id == "remove-btn":
            self.notify("Remove server functionality coming soon!")
        elif event.button.id == "sync-btn":
            self.notify("Sync functionality coming soon!")
