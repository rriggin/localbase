"""
Supabase Service Exceptions
Specific exception classes for Supabase integration errors.
"""

from ..base_service import ServiceError, AuthenticationError, ValidationError

class SupabaseError(ServiceError):
    """Base exception for Supabase service errors."""
    
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        super().__init__(message, service_name="supabase", status_code=status_code, details=details)

class SupabaseAuthError(AuthenticationError):
    """Raised when Supabase authentication fails."""
    
    def __init__(self, message: str = "Supabase authentication failed"):
        super().__init__(message, service_name="supabase")

class SupabaseValidationError(ValidationError):
    """Raised when Supabase data validation fails."""
    
    def __init__(self, message: str, field_name: str = None):
        details = {"field_name": field_name} if field_name else {}
        super().__init__(message, service_name="supabase", details=details)

class SupabaseConnectionError(SupabaseError):
    """Raised when Supabase connection fails."""
    
    def __init__(self, message: str = "Could not connect to Supabase"):
        super().__init__(message, details={"connection_error": True})

class SupabaseNotFoundError(SupabaseError):
    """Raised when Supabase record or table is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"Supabase {resource_type} '{resource_id}' not found"
        super().__init__(message, status_code=404, details={"resource_type": resource_type, "resource_id": resource_id}) 