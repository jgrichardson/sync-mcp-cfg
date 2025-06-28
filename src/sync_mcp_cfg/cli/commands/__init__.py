"""CLI commands for sync-mcp-cfg."""

from .add import add_command, add_interactive
from .list import list_command, list_detailed, list_summary
from .remove import remove_command, remove_interactive
from .sync import sync_command, sync_interactive

__all__ = [
    "add_command",
    "add_interactive",
    "remove_command", 
    "remove_interactive",
    "list_command",
    "list_detailed",
    "list_summary",
    "sync_command",
    "sync_interactive",
]