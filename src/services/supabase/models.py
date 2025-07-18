"""
Supabase Data Models
Type-safe models for call logs and Supabase records.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import json

@dataclass
class CallLogRecord:
    """Represents a call log record with type safety."""
    
    id: Optional[int] = None
    call_id: Optional[str] = None
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    from_name: Optional[str] = None
    to_name: Optional[str] = None
    direction: Optional[str] = None  # 'Inbound', 'Outbound'
    duration: Optional[int] = None  # seconds
    result: Optional[str] = None  # 'Connected', 'No Answer', etc.
    start_time: Optional[str] = None
    extension: Optional[str] = None
    queue: Optional[str] = None
    handle_time: Optional[int] = None
    raw_data: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'CallLogRecord':
        """Create record from Supabase API response."""
        return cls(
            id=data.get('id'),
            call_id=data.get('call_id'),
            from_number=data.get('from_number'),
            to_number=data.get('to_number'),
            from_name=data.get('from_name'),
            to_name=data.get('to_name'),
            direction=data.get('direction'),
            duration=data.get('duration'),
            result=data.get('result'),
            start_time=data.get('start_time'),
            extension=data.get('extension'),
            queue=data.get('queue'),
            handle_time=data.get('handle_time'),
            raw_data=data.get('raw_data'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @classmethod
    def from_zapier_webhook(cls, data: Dict[str, Any]) -> 'CallLogRecord':
        """Create record from Zapier webhook data."""
        return cls(
            call_id=data.get('call_id') or data.get('id'),
            from_number=data.get('from_number') or data.get('from'),
            to_number=data.get('to_number') or data.get('to'),
            from_name=data.get('from_name'),
            to_name=data.get('to_name'),
            direction=data.get('direction', 'Unknown'),
            duration=cls._parse_duration(data.get('duration')),
            result=data.get('result', 'Unknown'),
            start_time=data.get('start_time') or data.get('timestamp'),
            extension=data.get('extension'),
            queue=data.get('queue'),
            handle_time=cls._parse_duration(data.get('handle_time')),
            raw_data=data
        )
    
    @staticmethod
    def _parse_duration(duration_value: Any) -> Optional[int]:
        """Parse duration value to seconds."""
        if duration_value is None:
            return None
        
        if isinstance(duration_value, (int, float)):
            return int(duration_value)
        
        if isinstance(duration_value, str):
            try:
                return int(duration_value)
            except ValueError:
                return None
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        data = {}
        
        # Only include non-None values
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                data[field_name] = field_value
        
        # Don't include id for inserts
        if 'id' in data and data['id'] is None:
            del data['id']
            
        return data
    
    def is_over_threshold(self, threshold_seconds: int = 90) -> bool:
        """Check if call duration is over threshold."""
        return self.duration is not None and self.duration > threshold_seconds
    
    def get_formatted_duration(self) -> str:
        """Get human-readable duration."""
        if self.duration is None:
            return "Unknown"
        
        if self.duration < 60:
            return f"{self.duration}s"
        
        minutes = self.duration // 60
        seconds = self.duration % 60
        
        if self.duration < 3600:
            return f"{minutes}:{seconds:02d}"
        
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"


@dataclass
class SupabaseTable:
    """Represents a Supabase table configuration."""
    
    name: str
    primary_key: str = "id"
    
    @property
    def url(self) -> str:
        """Get the REST API URL for this table."""
        return f"/rest/v1/{self.name}"


@dataclass
class SupabaseQuery:
    """Represents a Supabase query with filters and options."""
    
    select: Optional[str] = None  # Columns to select
    filter_conditions: Optional[List[str]] = None  # WHERE conditions
    order_by: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    def to_params(self) -> Dict[str, Any]:
        """Convert to Supabase REST API parameters."""
        params = {}
        
        if self.select:
            params['select'] = self.select
        
        if self.filter_conditions:
            for condition in self.filter_conditions:
                # Parse condition like "duration=gte.90"
                if '=' in condition:
                    key, value = condition.split('=', 1)
                    params[key] = value
        
        if self.order_by:
            params['order'] = self.order_by
            
        if self.limit:
            params['limit'] = self.limit
            
        if self.offset:
            params['offset'] = self.offset
            
        return params


class CallLogQueryBuilder:
    """Builder for common call log queries."""
    
    def __init__(self):
        self.conditions = []
        self.order = None
        self.limit_value = None
    
    def over_threshold(self, seconds: int = 90) -> 'CallLogQueryBuilder':
        """Filter calls over duration threshold."""
        self.conditions.append(f"duration=gte.{seconds}")
        return self
    
    def by_direction(self, direction: str) -> 'CallLogQueryBuilder':
        """Filter by call direction."""
        self.conditions.append(f"direction=eq.{direction}")
        return self
    
    def by_extension(self, extension: str) -> 'CallLogQueryBuilder':
        """Filter by extension."""
        self.conditions.append(f"extension=eq.{extension}")
        return self
    
    def date_range(self, start_date: str, end_date: str = None) -> 'CallLogQueryBuilder':
        """Filter by date range."""
        self.conditions.append(f"start_time=gte.{start_date}")
        if end_date:
            self.conditions.append(f"start_time=lte.{end_date}")
        return self
    
    def order_by_duration(self, descending: bool = True) -> 'CallLogQueryBuilder':
        """Order by call duration."""
        self.order = f"duration.{'desc' if descending else 'asc'}"
        return self
    
    def limit(self, count: int) -> 'CallLogQueryBuilder':
        """Limit number of results."""
        self.limit_value = count
        return self
    
    def build(self) -> SupabaseQuery:
        """Build the final query."""
        return SupabaseQuery(
            filter_conditions=self.conditions if self.conditions else None,
            order_by=self.order,
            limit=self.limit_value
        ) 