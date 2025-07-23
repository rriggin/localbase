"""
Surge.sh Service Models
Data models for Surge.sh deployment configuration and results.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class SurgeConfig:
    """Configuration for Surge.sh deployment."""
    
    # Optional custom domain (if None, random will be generated)
    domain: Optional[str] = None
    
    # Project metadata
    project_name: Optional[str] = None
    description: Optional[str] = None
    
    # Deployment options
    force_https: bool = True
    cleanup_on_failure: bool = True
    
    # Authentication (if needed)
    email: Optional[str] = None
    token: Optional[str] = None

@dataclass 
class SurgeDeployment:
    """Result of a Surge.sh deployment."""
    
    success: bool
    domain: str
    url: str
    project_name: Optional[str] = None
    
    # Deployment metadata
    deployed_at: Optional[datetime] = None
    file_count: Optional[int] = None
    total_size: Optional[str] = None
    
    # Error information
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    @property
    def public_url(self) -> str:
        """Get the full public URL."""
        protocol = "https" if self.url.startswith("https") else "http"
        return f"{protocol}://{self.domain}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'domain': self.domain,
            'url': self.url,
            'public_url': self.public_url,
            'project_name': self.project_name,
            'deployed_at': self.deployed_at.isoformat() if self.deployed_at else None,
            'file_count': self.file_count,
            'total_size': self.total_size,
            'error': self.error,
            'error_details': self.error_details
        } 