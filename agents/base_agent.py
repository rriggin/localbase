"""
Base Agent Interface
Common interface for all LocalBase AI MCP agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

class BaseAgent(ABC):
    """
    Base interface for all LocalBase agents.
    
    All agents must implement this interface to ensure consistency
    and enable proper testing, monitoring, and management.
    """
    
    def __init__(self, config: Dict[str, Any], services: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent with configuration and services.
        
        Args:
            config: Agent-specific configuration
            services: Injected service dependencies
        """
        self.config = config
        self.services = services or {}
        self.logger = self._setup_logging()
        self.metadata = {
            "agent_name": self.__class__.__name__,
            "created_at": datetime.now().isoformat(),
            "version": getattr(self, "VERSION", "1.0.0")
        }
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Main agent execution method.
        
        Args:
            **kwargs: Agent-specific input parameters
            
        Returns:
            Dict containing execution results and metadata
        """
        pass
    
    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters before execution.
        
        Args:
            **kwargs: Input parameters to validate
            
        Returns:
            True if input is valid, False otherwise
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metadata."""
        return {
            "status": "ready",
            "metadata": self.metadata,
            "config_keys": list(self.config.keys()),
            "services": list(self.services.keys())
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the agent."""
        logger = logging.getLogger(f"localbase.{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _log_execution(self, action: str, **kwargs):
        """Log agent execution details."""
        self.logger.info(f"{action}: {kwargs}")


class AgentResult:
    """
    Standardized result object for agent executions.
    """
    
    def __init__(self, success: bool, data: Any = None, error: str = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class AgentError(Exception):
    """Base exception for agent errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {} 