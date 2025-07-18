"""
Base Service Interface
Common interface for all external service integrations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime

class BaseService(ABC):
    """
    Base interface for all external service integrations.
    
    Provides common patterns for authentication, error handling,
    rate limiting, and monitoring across all services.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the service with configuration.
        
        Args:
            config: Service-specific configuration including credentials
        """
        self.config = config
        self.logger = self._setup_logging()
        self._authenticated = False
        self._last_request = None
        
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the external service.
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Check service health and connectivity.
        
        Returns:
            Dict with health status and metrics
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return {
            "service_name": self.__class__.__name__,
            "authenticated": self._authenticated,
            "last_request": self._last_request,
            "config_present": bool(self.config)
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the service."""
        logger = logging.getLogger(f"localbase.services.{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _log_request(self, method: str, endpoint: str, **kwargs):
        """Log service requests for monitoring."""
        self._last_request = datetime.now().isoformat()
        self.logger.debug(f"{method} {endpoint}: {kwargs}")


class ServiceError(Exception):
    """Base exception for service errors."""
    
    def __init__(self, message: str, service_name: str = None, status_code: int = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.service_name = service_name
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(ServiceError):
    """Raised when service authentication fails."""
    pass


class RateLimitError(ServiceError):
    """Raised when service rate limits are exceeded."""
    pass


class ValidationError(ServiceError):
    """Raised when service input validation fails."""
    pass 