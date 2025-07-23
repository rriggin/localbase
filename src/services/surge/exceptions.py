"""
Surge.sh Service Exceptions
Custom exceptions for Surge.sh deployment operations.
"""

class SurgeError(Exception):
    """Base exception for Surge.sh service errors."""
    pass

class SurgeDeploymentError(SurgeError):
    """Raised when deployment to Surge.sh fails."""
    pass

class SurgeAuthenticationError(SurgeError):
    """Raised when Surge.sh authentication fails."""
    pass

class SurgeValidationError(SurgeError):
    """Raised when deployment validation fails."""
    pass

class SurgeConnectionError(SurgeError):
    """Raised when connection to Surge.sh fails."""
    pass 