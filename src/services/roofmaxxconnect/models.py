"""
RoofMaxx Connect Data Models
Type-safe models for dealer data and API responses.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import json

@dataclass
class DealerRecord:
    """Represents a dealer record from RoofMaxx Connect."""
    
    id: Optional[int] = None
    name: Optional[str] = None
    brand_name: Optional[str] = None
    hubspot_company_id: Optional[int] = None
    microsite_url: Optional[str] = None
    google_review_link: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'DealerRecord':
        """Create dealer record from API response."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            brand_name=data.get('brand_name'),
            hubspot_company_id=data.get('hubspot_company_id'),
            microsite_url=data.get('microsite_url'),
            google_review_link=data.get('google_review_link')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        for field, value in self.__dict__.items():
            if value is not None:
                result[field] = value
        return result

@dataclass
class RoofmaxxRecord:
    """Represents a RoofMaxx Connect record with type safety."""
    
    id: Optional[str] = None
    rmc_id: Optional[str] = None  # RoofMaxx Connect ID
    dealer_id: Optional[str] = None
    deal_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'RoofmaxxRecord':
        """Create record from RoofMaxx Connect API response."""
        return cls(
            id=data.get('id'),
            rmc_id=data.get('rmc_id'),
            dealer_id=data.get('dealer_id'),
            deal_id=data.get('deal_id'),
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email'),
            customer_phone=data.get('customer_phone'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            status=data.get('status'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            raw_data=data
        )
    
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """Get a field value with default."""
        return getattr(self, field_name, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {}
        for field, value in self.__dict__.items():
            if value is not None and field != 'raw_data':
                result[field] = value
        return result

@dataclass
class DealRecord:
    """Represents a deal/lead record from RoofMaxx Connect."""
    
    deal_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    property_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    roof_age: Optional[int] = None
    roof_condition: Optional[str] = None
    lead_source: Optional[str] = None
    status: Optional[str] = None
    estimated_value: Optional[float] = None
    appointment_date: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'DealRecord':
        """Create deal record from API response."""
        return cls(
            deal_id=data.get('deal_id') or data.get('id'),
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email'),
            customer_phone=data.get('customer_phone'),
            property_address=data.get('property_address') or data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code') or data.get('zip'),
            roof_age=data.get('roof_age'),
            roof_condition=data.get('roof_condition'),
            lead_source=data.get('lead_source'),
            status=data.get('status'),
            estimated_value=data.get('estimated_value'),
            appointment_date=data.get('appointment_date'),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass 
class PaginationMeta:
    """Represents pagination metadata from API responses."""
    
    current_page: int = 1
    from_record: Optional[int] = None
    last_page: int = 1
    per_page: int = 100
    to_record: Optional[int] = None
    total: int = 0
    
    @classmethod
    def from_api_response(cls, meta: Dict[str, Any]) -> 'PaginationMeta':
        """Create pagination meta from API response."""
        return cls(
            current_page=meta.get('current_page', 1),
            from_record=meta.get('from'),
            last_page=meta.get('last_page', 1),
            per_page=meta.get('per_page', 100),
            to_record=meta.get('to'),
            total=meta.get('total', 0)
        )

@dataclass
class PaginatedResponse:
    """Represents a paginated API response."""
    
    data: List[Any]
    meta: PaginationMeta
    links: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any], data_type: type = dict) -> 'PaginatedResponse':
        """Create paginated response from API response."""
        data = response.get('data', [])
        
        # Convert data items if a specific type is provided
        if data_type != dict and hasattr(data_type, 'from_api_response'):
            data = [data_type.from_api_response(item) for item in data]
        
        return cls(
            data=data,
            meta=PaginationMeta.from_api_response(response.get('meta', {})),
            links=response.get('links', {})
        )

class RoofmaxxTable:
    """Represents a table/collection in RoofMaxx Connect."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.base_url = f"/api/v2"
    
    def build_url(self, endpoint: str = None) -> str:
        """Build URL for API requests."""
        url = self.base_url
        if endpoint:
            url += f"/{endpoint}"
        return url

class RoofmaxxQuery:
    """Query builder for RoofMaxx Connect API requests."""
    
    def __init__(self, table: RoofmaxxTable):
        self.table = table
        self.filters = {}
        self.columns = []
        self.page = 1
        self.per_page = 100
        self.sort_by = None
        self.sort_order = "asc"
    
    def select(self, columns: List[str]) -> 'RoofmaxxQuery':
        """Select specific columns."""
        self.columns = columns
        return self
    
    def where(self, field: str, value: Any) -> 'RoofmaxxQuery':
        """Add a filter condition."""
        self.filters[field] = value
        return self
    
    def paginate(self, page: int = 1, per_page: int = 100) -> 'RoofmaxxQuery':
        """Set pagination parameters."""
        self.page = page
        self.per_page = per_page
        return self
    
    def order_by(self, field: str, direction: str = "asc") -> 'RoofmaxxQuery':
        """Set sort order."""
        self.sort_by = field
        self.sort_order = direction
        return self
    
    def build_params(self) -> Dict[str, Any]:
        """Build query parameters."""
        params = {}
        
        if self.columns:
            params['columns'] = ','.join(self.columns)
        
        if self.page:
            params['page'] = self.page
            
        if self.per_page:
            params['per_page'] = self.per_page
            
        if self.sort_by:
            params['sort_by'] = self.sort_by
            params['sort_order'] = self.sort_order
        
        # Add filter parameters
        params.update(self.filters)
        
        return params

class DealQueryBuilder:
    """Specialized query builder for deals."""
    
    def __init__(self, rmc_id: str):
        self.rmc_id = rmc_id
        self.filters = {}
        self.page = 1
        self.per_page = 50
    
    def filter_by_status(self, status: str) -> 'DealQueryBuilder':
        """Filter deals by status."""
        self.filters['status'] = status
        return self
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> 'DealQueryBuilder':
        """Filter deals by date range."""
        self.filters['start_date'] = start_date
        self.filters['end_date'] = end_date
        return self
    
    def paginate(self, page: int = 1, per_page: int = 50) -> 'DealQueryBuilder':
        """Set pagination."""
        self.page = page
        self.per_page = per_page
        return self
    
    def build_params(self) -> Dict[str, Any]:
        """Build query parameters for deals endpoint."""
        params = {
            'page': self.page,
            'per_page': self.per_page
        }
        params.update(self.filters)
        return params 