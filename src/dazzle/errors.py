class DazzleError(Exception):
    """Base exception for dazzle errors."""


class CompileError(DazzleError):
    """Raised when markdown compilation fails."""

