"""
RoofmaxxConnect Service Exceptions
Specific exception classes for RoofmaxxConnect integration errors.
"""

from ..base_service import ServiceError, AuthenticationError, ValidationError

class RoofmaxxError(ServiceError):
    """Base exception for RoofmaxxConnect service errors."""
    
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        super().__init__(message, service_name="roofmaxxconnect", status_code=status_code, details=details)

class RoofmaxxAuthError(AuthenticationError):
    """Raised when RoofmaxxConnect authentication fails."""
    
    def __init__(self, message: str = "RoofmaxxConnect authentication failed"):
        super().__init__(message, service_name="roofmaxxconnect")

class RoofmaxxValidationError(ValidationError):
    """Raised when RoofmaxxConnect data validation fails."""
    
    def __init__(self, message: str, field_name: str = None):
        details = {"field_name": field_name} if field_name else {}
        super().__init__(message, service_name="roofmaxxconnect", details=details)

class RoofmaxxRateLimitError(RoofmaxxError):
    """Raised when RoofmaxxConnect rate limits are exceeded."""
    
    def __init__(self, retry_after: int = None):
        message = f"RoofmaxxConnect rate limit exceeded. Retry after {retry_after} seconds." if retry_after else "RoofmaxxConnect rate limit exceeded."
        super().__init__(message, status_code=429, details={"retry_after": retry_after})

class RoofmaxxNotFoundError(RoofmaxxError):
    """Raised when RoofmaxxConnect record or resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"RoofmaxxConnect {resource_type} '{resource_id}' not found"
        super().__init__(message, status_code=404, details={"resource_type": resource_type, "resource_id": resource_id}) 