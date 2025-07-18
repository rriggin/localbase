"""
Airtable Data Models
Type-safe models for Airtable records and tables.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

@dataclass
class AirtableRecord:
    """Represents an Airtable record with type safety."""
    
    id: str
    fields: Dict[str, Any]
    created_time: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'AirtableRecord':
        """Create record from Airtable API response."""
        return cls(
            id=data.get('id', ''),
            fields=data.get('fields', {}),
            created_time=data.get('createdTime')
        )
    
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """Get a field value with default."""
        return self.fields.get(field_name, default)
    
    def set_field(self, field_name: str, value: Any) -> None:
        """Set a field value."""
        self.fields[field_name] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {"fields": self.fields}
        if self.id:
            result["id"] = self.id
        return result


@dataclass
class AirtableTable:
    """Represents an Airtable table configuration."""
    
    base_id: str
    table_name: str
    primary_field: Optional[str] = None
    
    @property
    def url(self) -> str:
        """Get the API URL for this table."""
        return f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"


@dataclass
class AirtableQuery:
    """Represents an Airtable query with filters and options."""
    
    filter_formula: Optional[str] = None
    sort: Optional[List[Dict[str, str]]] = None
    fields: Optional[List[str]] = None
    max_records: Optional[int] = None
    page_size: Optional[int] = None
    view: Optional[str] = None
    
    def to_params(self) -> Dict[str, Any]:
        """Convert to API query parameters."""
        params = {}
        
        if self.filter_formula:
            params['filterByFormula'] = self.filter_formula
        if self.sort:
            params['sort'] = self.sort
        if self.fields:
            params['fields'] = self.fields
        if self.max_records:
            params['maxRecords'] = self.max_records
        if self.page_size:
            params['pageSize'] = self.page_size
        if self.view:
            params['view'] = self.view
            
        return params


class AirtableRecordBuilder:
    """Builder pattern for creating Airtable records."""
    
    def __init__(self):
        self.fields = {}
    
    def add_field(self, name: str, value: Any) -> 'AirtableRecordBuilder':
        """Add a field to the record."""
        self.fields[name] = value
        return self
    
    def add_business_fields(self, business: str, source_system: str) -> 'AirtableRecordBuilder':
        """Add standard business identification fields."""
        return self.add_field("Business", business).add_field("Source System", source_system)
    
    def add_timestamp_fields(self) -> 'AirtableRecordBuilder':
        """Add current timestamp fields."""
        now = datetime.now().isoformat()
        return self.add_field("Updated Date", now).add_field("Last Sync", now)
    
    def build(self) -> Dict[str, Any]:
        """Build the final record dictionary."""
        return {"fields": self.fields} 