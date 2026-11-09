"""
Exceptions for the connector framework.
"""


class ConnectorError(Exception):
    """Base exception for connector errors."""

    def __init__(self, message: str, source: str = None, original_error: Exception = None):
        super().__init__(message)
        self.message = message
        self.source = source
        self.original_error = original_error


class RateLimitError(ConnectorError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class AuthError(ConnectorError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, **kwargs)


class ValidationError(ConnectorError):
    """Raised when data validation fails."""
    pass


class SourceUnavailableError(ConnectorError):
    """Raised when a source is temporarily unavailable."""
    pass


class CAPTCHARequiredError(ConnectorError):
    """Raised when CAPTCHA is required (and should not be bypassed)."""

    def __init__(self, message: str = "CAPTCHA required - access blocked", **kwargs):
        super().__init__(message, **kwargs)