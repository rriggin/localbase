"""
Supabase Service
Professional Supabase integration for call logs and real-time data.
"""

from .client import SupabaseService
from .models import CallLogRecord, SupabaseTable
from .exceptions import SupabaseError, SupabaseAuthError, SupabaseValidationError

__all__ = [
    "SupabaseService",
    "CallLogRecord",
    "SupabaseTable", 
    "SupabaseError",
    "SupabaseAuthError",
    "SupabaseValidationError"
] 