"""Custom exceptions for sync-mcp-cfg."""


class SyncMCPError(Exception):
    """Base exception for sync-mcp-cfg."""

    pass


class ClientNotFoundError(SyncMCPError):
    """Raised when a client is not found or not available."""

    pass


class ConfigurationError(SyncMCPError):
    """Raised when there's an error in configuration."""

    pass


class ValidationError(SyncMCPError):
    """Raised when validation fails."""

    pass


class BackupError(SyncMCPError):
    """Raised when backup operations fail."""

    pass


class SyncError(SyncMCPError):
    """Raised when sync operations fail."""

    pass


class ServerNotFoundError(SyncMCPError):
    """Raised when a server is not found."""

    pass


class ClientHandlerError(SyncMCPError):
    """Raised when a client handler encounters an error."""

    pass
