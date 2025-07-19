"""
Supabase Service
Professional Supabase integration for call logs, deals data, and real-time analytics.
"""

from .client import SupabaseService
from .models import CallLogRecord, SupabaseTable
from .exceptions import SupabaseError, SupabaseAuthError, SupabaseValidationError

# RoofMaxx Deals Integration
from .deals_models import RoofmaxxDealRecord, DealsSyncStatus
from .deals_sync_service import DealsSyncService
from .deals_analytics import DealsAnalytics

__all__ = [
    # Core Supabase service
    "SupabaseService",
    "CallLogRecord",
    "SupabaseTable", 
    "SupabaseError",
    "SupabaseAuthError",
    "SupabaseValidationError",
    
    # RoofMaxx Deals Integration
    "RoofmaxxDealRecord",
    "DealsSyncStatus",
    "DealsSyncService", 
    "DealsAnalytics"
] 