"""
Services Package
External service integrations with clean interfaces.
"""

from typing import Dict, Type, List
from .base_service import BaseService

# Service registry for dependency injection
_SERVICE_REGISTRY: Dict[str, Type[BaseService]] = {}

def register_service(name: str, service_class: Type[BaseService]):
    """Register a service class."""
    _SERVICE_REGISTRY[name] = service_class

def get_service(name: str) -> Type[BaseService]:
    """Get a registered service class."""
    if name not in _SERVICE_REGISTRY:
        raise ValueError(f"Service '{name}' not found. Available: {list(_SERVICE_REGISTRY.keys())}")
    return _SERVICE_REGISTRY[name]

def list_services() -> List[str]:
    """List all registered services."""
    return list(_SERVICE_REGISTRY.keys())

# Auto-import and register services
try:
    from .airtable.client import AirtableService
    register_service("airtable", AirtableService)
except ImportError:
    pass

try:
    from .supabase.client import SupabaseService
    register_service("supabase", SupabaseService)
except ImportError:
    pass

try:
    from .roofmaxxconnect.client import RoofmaxxConnectService
    register_service("roofmaxxconnect", RoofmaxxConnectService)
except ImportError:
    pass

try:
    from .ringcentral.client import RingCentralService
    register_service("ringcentral", RingCentralService)
except ImportError:
    pass

try:
    from .zapier.client import ZapierService
    register_service("zapier", ZapierService)
except ImportError:
    pass 