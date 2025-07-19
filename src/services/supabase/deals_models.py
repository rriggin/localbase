"""
RoofMaxx Deals Data Models for Supabase Storage

Type-safe models for storing and analyzing RoofMaxx Connect deals data.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import json

@dataclass
class RoofmaxxDealRecord:
    """Represents a RoofMaxx Connect deal record for Supabase storage."""
    
    # Primary identifiers
    id: Optional[int] = None  # Supabase primary key
    deal_id: Optional[int] = None  # RoofMaxx deal_id
    rmc_id: Optional[int] = None  # Internal RoofMaxx ID
    dispatch_id: Optional[int] = None
    dealer_id: Optional[int] = None  # Your dealer ID (6637)
    
    # Deal information
    deal_name: Optional[str] = None
    deal_type: Optional[str] = None  # ASP, NAP, RMCL, etc.
    deal_lifecycle: Optional[str] = None  # Lead, Lost, etc.
    stage_label: Optional[str] = None
    deal_stage: Optional[str] = None
    
    # Customer information
    customer_first_name: Optional[str] = None
    customer_last_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    
    # Location data
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    
    # Business data
    invoice_total: Optional[str] = None
    is_roof_maxx_job: Optional[bool] = None
    has_warranty: Optional[bool] = None
    
    # HubSpot integration
    hs_contact_id: Optional[int] = None
    hubspot_company_id: Optional[int] = None
    
    # Timestamps
    create_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    synced_at: Optional[datetime] = None
    
    # Raw data backup
    raw_data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_roofmaxx_api(cls, data: Dict[str, Any], dealer_id: int = 6637) -> 'RoofmaxxDealRecord':
        """Create record from RoofMaxx Connect API response."""
        
        # Extract customer info from hubspot_contact
        hubspot_contact = data.get('hubspot_contact', {}) or {}
        
        # Convert createdate timestamp to datetime
        create_date = None
        if data.get('createdate'):
            try:
                create_date = datetime.fromtimestamp(int(data['createdate']) / 1000)
            except:
                pass
        
        # Extract stage info
        stage = data.get('stage', {}) or {}
        stage_label = stage.get('label') if isinstance(stage, dict) else str(stage)
        
        return cls(
            # Identifiers
            deal_id=data.get('deal_id'),
            rmc_id=data.get('id'),  # RoofMaxx internal ID
            dispatch_id=data.get('dispatch_id'),
            dealer_id=dealer_id,
            
            # Deal information
            deal_name=data.get('deal_name'),
            deal_type=data.get('dealtype'),
            deal_lifecycle=data.get('deal_lifecycle'),
            stage_label=stage_label,
            deal_stage=data.get('dealstage'),
            
            # Customer information
            customer_first_name=hubspot_contact.get('firstname'),
            customer_last_name=hubspot_contact.get('lastname'),
            customer_email=hubspot_contact.get('email'),
            customer_phone=hubspot_contact.get('phone'),
            
            # Location
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            
            # Business data
            invoice_total=data.get('invoice_total_currency'),
            is_roof_maxx_job=data.get('is_roof_maxx_job') == 'true' or data.get('is_roof_maxx_job') is True,
            has_warranty=data.get('has_warranty') is True,
            
            # HubSpot
            hs_contact_id=data.get('hs_contact_id'),
            hubspot_company_id=None,  # This would come from dealer info
            
            # Timestamps
            create_date=create_date,
            synced_at=datetime.now(),
            
            # Raw backup
            raw_data=data
        )
    
    def to_supabase_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Supabase insertion."""
        return {
            'deal_id': self.deal_id,
            'rmc_id': self.rmc_id,
            'dispatch_id': self.dispatch_id,
            'dealer_id': self.dealer_id,
            'deal_name': self.deal_name,
            'deal_type': self.deal_type,
            'deal_lifecycle': self.deal_lifecycle,
            'stage_label': self.stage_label,
            'deal_stage': self.deal_stage,
            'customer_first_name': self.customer_first_name,
            'customer_last_name': self.customer_last_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'invoice_total': self.invoice_total,
            'is_roof_maxx_job': self.is_roof_maxx_job,
            'has_warranty': self.has_warranty,
            'hs_contact_id': self.hs_contact_id,
            'hubspot_company_id': self.hubspot_company_id,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'synced_at': self.synced_at.isoformat() if self.synced_at else None,
            'raw_data': self.raw_data
        }

@dataclass 
class DealsSyncStatus:
    """Track sync status and statistics."""
    
    total_deals_api: int = 0
    total_deals_db: int = 0
    new_deals_synced: int = 0
    updated_deals: int = 0
    sync_errors: int = 0
    last_sync_time: Optional[datetime] = None
    sync_duration_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage."""
        return {
            'total_deals_api': self.total_deals_api,
            'total_deals_db': self.total_deals_db,
            'new_deals_synced': self.new_deals_synced,
            'updated_deals': self.updated_deals,
            'sync_errors': self.sync_errors,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'sync_duration_seconds': self.sync_duration_seconds
        } 