"""
Airtable Service
Professional Airtable integration with clean interfaces.
"""

from .client import AirtableService
from .models import AirtableRecord, AirtableTable, AirtableQuery, AirtableRecordBuilder
from .exceptions import AirtableError, AirtableAuthError, AirtableValidationError

__all__ = [
    "AirtableService",
    "AirtableRecord", 
    "AirtableTable",
    "AirtableQuery",
    "AirtableRecordBuilder",
    "AirtableError",
    "AirtableAuthError",
    "AirtableValidationError"
] 