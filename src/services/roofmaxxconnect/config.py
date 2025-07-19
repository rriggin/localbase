"""
RoofMaxx Connect Service Configuration

Configuration utilities and environment variable management
for the RoofMaxx Connect service.
"""

import os
from typing import Dict, Any, Optional

class RoofmaxxConnectConfig:
    """Configuration manager for RoofMaxx Connect service."""
    
    def __init__(self):
        self.bearer_token = None
        self.base_url = 'https://roofmaxxconnect.com'
        self.default_dealer_id = None
        self.timeout = 30
        self.max_retries = 3
    
    def from_env(self) -> 'RoofmaxxConnectConfig':
        """Load configuration from environment variables."""
        self.bearer_token = os.getenv('ROOFMAXX_CONNECT_TOKEN')
        self.base_url = os.getenv('ROOFMAXX_CONNECT_BASE_URL', self.base_url)
        self.default_dealer_id = os.getenv('ROOFMAXX_CONNECT_DEALER_ID')
        
        timeout_str = os.getenv('ROOFMAXX_CONNECT_TIMEOUT', str(self.timeout))
        try:
            self.timeout = int(timeout_str)
        except ValueError:
            pass
        
        return self
    
    def from_dict(self, config: Dict[str, Any]) -> 'RoofmaxxConnectConfig':
        """Load configuration from dictionary."""
        self.bearer_token = config.get('bearer_token')
        self.base_url = config.get('base_url', self.base_url)
        self.default_dealer_id = config.get('default_dealer_id')
        self.timeout = config.get('timeout', self.timeout)
        self.max_retries = config.get('max_retries', self.max_retries)
        return self
    
    def to_service_config(self) -> Dict[str, Any]:
        """Convert to service configuration dictionary."""
        return {
            'bearer_token': self.bearer_token,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'max_retries': self.max_retries
        }
    
    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self.bearer_token:
            raise ValueError("bearer_token is required")
        
        if not self.base_url:
            raise ValueError("base_url is required")
        
        return True

def get_roofmaxx_config(bearer_token: Optional[str] = None, 
                       base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Get RoofMaxx Connect configuration.
    
    Args:
        bearer_token: Override bearer token
        base_url: Override base URL
        
    Returns:
        Configuration dictionary for the service
    """
    config = RoofmaxxConnectConfig().from_env()
    
    # Override with provided values
    if bearer_token:
        config.bearer_token = bearer_token
    if base_url:
        config.base_url = base_url
    
    config.validate()
    return config.to_service_config()

def create_roofmaxx_service_from_env():
    """
    Create a RoofMaxx Connect service instance from environment variables.
    
    Returns:
        Configured RoofmaxxConnectService instance
    """
    from .client import RoofmaxxConnectService
    
    config = get_roofmaxx_config()
    return RoofmaxxConnectService(config)

# Environment variable documentation
ENV_VARS_DOCS = """
RoofMaxx Connect Environment Variables:

Required:
  ROOFMAXX_CONNECT_TOKEN          Bearer token for API authentication

Optional:
  ROOFMAXX_CONNECT_BASE_URL      Base URL for the API (default: https://roofmaxxconnect.com)
  ROOFMAXX_CONNECT_DEALER_ID     Default dealer ID for operations
  ROOFMAXX_CONNECT_TIMEOUT       Request timeout in seconds (default: 30)

Example .env file:
  ROOFMAXX_CONNECT_TOKEN=aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd
  ROOFMAXX_CONNECT_DEALER_ID=rmc001
  ROOFMAXX_CONNECT_TIMEOUT=45
""" 