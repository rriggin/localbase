"""
D3.js Service Exceptions
Custom exceptions for D3 visualization service errors.
"""

class D3Error(Exception):
    """Base exception for D3 service errors."""
    pass

class D3ValidationError(D3Error):
    """Raised when chart configuration or data validation fails."""
    pass

class D3RenderError(D3Error):
    """Raised when chart rendering fails."""
    pass

class D3DataError(D3Error):
    """Raised when data processing fails."""
    pass

class D3TemplateError(D3Error):
    """Raised when chart template loading fails."""
    pass 