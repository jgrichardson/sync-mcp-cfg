"""Client handlers for different MCP clients."""

from typing import Dict, Type

from ..core.models import ClientType
from .base import BaseClientHandler
from .claude_code import ClaudeCodeHandler
from .claude_desktop import ClaudeDesktopHandler
from .cursor import CursorHandler
from .vscode import VSCodeHandler

# Registry of client handlers
CLIENT_HANDLERS: Dict[ClientType, Type[BaseClientHandler]] = {
    ClientType.CLAUDE_CODE: ClaudeCodeHandler,
    ClientType.CLAUDE_DESKTOP: ClaudeDesktopHandler,
    ClientType.CURSOR: CursorHandler,
    ClientType.VSCODE: VSCodeHandler,
}


def get_client_handler(client_type: ClientType) -> Type[BaseClientHandler]:
    """Get the handler class for a specific client type."""
    if client_type not in CLIENT_HANDLERS:
        raise ValueError(f"No handler available for client type: {client_type}")
    return CLIENT_HANDLERS[client_type]


__all__ = [
    "BaseClientHandler",
    "ClaudeCodeHandler",
    "ClaudeDesktopHandler", 
    "CursorHandler",
    "VSCodeHandler",
    "CLIENT_HANDLERS",
    "get_client_handler",
]