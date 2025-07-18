"""
Airtable Service Exceptions
Specific exception classes for Airtable integration errors.
"""

from ..base_service import ServiceError, AuthenticationError, ValidationError

class AirtableError(ServiceError):
    """Base exception for Airtable service errors."""
    
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        super().__init__(message, service_name="airtable", status_code=status_code, details=details)

class AirtableAuthError(AuthenticationError):
    """Raised when Airtable authentication fails."""
    
    def __init__(self, message: str = "Airtable authentication failed"):
        super().__init__(message, service_name="airtable")

class AirtableValidationError(ValidationError):
    """Raised when Airtable data validation fails."""
    
    def __init__(self, message: str, field_name: str = None):
        details = {"field_name": field_name} if field_name else {}
        super().__init__(message, service_name="airtable", details=details)

class AirtableRateLimitError(AirtableError):
    """Raised when Airtable rate limits are exceeded."""
    
    def __init__(self, retry_after: int = None):
        message = f"Airtable rate limit exceeded. Retry after {retry_after} seconds." if retry_after else "Airtable rate limit exceeded."
        super().__init__(message, status_code=429, details={"retry_after": retry_after})

class AirtableNotFoundError(AirtableError):
    """Raised when Airtable record or table is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"Airtable {resource_type} '{resource_id}' not found"
        super().__init__(message, status_code=404, details={"resource_type": resource_type, "resource_id": resource_id}) 