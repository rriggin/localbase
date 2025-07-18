"""
LocalBase Configuration System
Professional configuration with service dependency injection.
"""

import os
from typing import Dict, Any, Optional, Type
from datetime import datetime

# Import services  
from .services import get_service, BaseService
from .services.airtable import AirtableService
from .services.supabase import SupabaseService

class LocalBaseConfig:
    """
    Professional configuration system with service dependency injection.
    
    Manages environment variables, service initialization, and dependency
    injection for agents and tools.
    """
    
    def __init__(self):
        # Load environment variables
        self._load_environment()
        
        # Initialize service instances
        self._services: Dict[str, BaseService] = {}
        
        # Agent configurations
        self.agent_configs = self._build_agent_configs()
        
    def _load_environment(self):
        """Load and validate environment variables."""
        # Try to load from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Core configuration
        self.python_executable = os.getenv("PYTHON_EXECUTABLE", "python3")
        
        # Airtable configuration
        self.airtable_token = os.getenv("AIRTABLE_TOKEN")
        self.airtable_base_id = os.getenv("AIRTABLE_BASE_ID", "app9Mj5rbIFvK9p9D")
        self.airtable_table_name = os.getenv("AIRTABLE_TABLE_NAME", "Leads and Opportunities")
        
        # Supabase configuration
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_access_token = os.getenv("SUPABASE_ACCESS_TOKEN")
        
        # RoofmaxxConnect configuration
        self.roofmaxxconnect_base_url = os.getenv("ROOFMAXXCONNECT_BASE_URL", "https://api.roofmaxxconnect.com")
        self.roofmaxxconnect_bearer_token = os.getenv("ROOFMAXXCONNECT_BEARER_TOKEN")
        
        # RingCentral configuration (for future direct API if fixed)
        self.ringcentral_client_id = os.getenv("RINGCENTRAL_CLIENT_ID")
        self.ringcentral_client_secret = os.getenv("RINGCENTRAL_CLIENT_SECRET")
        
        # Zapier configuration
        self.zapier_webhook_url = os.getenv("ZAPIER_WEBHOOK_URL")
        
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # ATTOM Data configuration 
        self.attom_api_key = os.getenv("ATTOM_API_KEY")
        
    def _build_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Build configuration dictionaries for each agent type."""
        return {
            "airtable_viewer": {
                "name": "Airtable Data Viewer",
                "description": "View and analyze Airtable data",
                "required_services": ["airtable"],
                "config": {
                    "default_view": "Grid view",
                    "export_formats": ["csv", "json"],
                    "max_records_display": 50
                }
            },
            "call_log_analyzer": {
                "name": "Call Log Analyzer", 
                "description": "Analyze RingCentral call logs for insights",
                "required_services": ["supabase"],
                "config": {
                    "threshold_seconds": 90,
                    "analysis_window_days": 30,
                    "report_formats": ["json", "chart"]
                }
            },
            "google_maps_scraper": {
                "name": "Google Maps Address Scraper",
                "description": "Extract addresses from Google Maps lists and save to Airtable",
                "required_services": ["airtable"],
                "config": {
                    "default_headless": True,
                    "default_timeout": 15,
                    "batch_size": 100,
                    "max_retries": 3,
                    "default_business_name": "Google Maps Import"
                }
            },
            "roofmaxx_data_sync": {
                "name": "RoofmaxxConnect Data Sync",
                "description": "Sync clean roofing data from RoofmaxxConnect",
                "required_services": ["roofmaxxconnect", "airtable"],
                "config": {
                    "sync_interval_hours": 6,
                    "batch_size": 100,
                    "data_fields": ["customers", "jobs", "estimates"]
                }
            },
            "attom_property_enrichment": {
                "name": "ATTOM Property Enrichment Agent",
                "description": "Enrich addresses with property data using ATTOM Data API",
                "required_services": ["airtable"],
                "config": {
                    "api_key": self.attom_api_key,
                    "base_url": "https://api.gateway.attomdata.com/propertyapi/v1.0.0",
                    "rate_limit_delay": 1.1,
                    "batch_size": 50,
                    "max_retries": 3,
                    "timeout": 30
                }
            }
        }
    
    def get_service(self, service_name: str) -> BaseService:
        """
        Get or create a service instance with dependency injection.
        
        Args:
            service_name: Name of the service ('airtable', 'supabase', 'roofmaxxconnect', etc.)
            
        Returns:
            Initialized service instance
            
        Raises:
            ValueError: If service not available or missing configuration
        """
        # Return cached instance if exists
        if service_name in self._services:
            return self._services[service_name]
        
        # Create new service instance
        service_class = get_service(service_name)
        service_config = self._get_service_config(service_name)
        
        # Initialize and cache service
        service_instance = service_class(service_config)
        self._services[service_name] = service_instance
        
        return service_instance
    
    def _get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service."""
        configs = {
            "airtable": {
                "token": self.airtable_token,
                "base_id": self.airtable_base_id,
                "table_name": self.airtable_table_name
            },
            "supabase": {
                "url": self.supabase_url,
                "anon_key": self.supabase_anon_key,
                "access_token": self.supabase_access_token
            },
            "roofmaxxconnect": {
                "base_url": self.roofmaxxconnect_base_url,
                "bearer_token": self.roofmaxxconnect_bearer_token
            },
            "ringcentral": {
                "client_id": self.ringcentral_client_id,
                "client_secret": self.ringcentral_client_secret
            },
            "zapier": {
                "webhook_url": self.zapier_webhook_url
            }
        }
        
        config = configs.get(service_name)
        if not config:
            raise ValueError(f"No configuration found for service: {service_name}")
        
        # Validate required config keys exist
        missing_keys = [key for key, value in config.items() if not value]
        if missing_keys:
            raise ValueError(f"Missing configuration for {service_name}: {missing_keys}")
        
        return config
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        if agent_name not in self.agent_configs:
            raise ValueError(f"No configuration found for agent: {agent_name}")
        
        return self.agent_configs[agent_name]
    
    def initialize_services_for_agent(self, agent_name: str) -> Dict[str, BaseService]:
        """Initialize all required services for an agent."""
        agent_config = self.get_agent_config(agent_name)
        required_services = agent_config.get("required_services", [])
        
        services = {}
        for service_name in required_services:
            services[service_name] = self.get_service(service_name)
        
        return services
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services."""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "services": {}
        }
        
        unhealthy_services = []
        
        for service_name in ["airtable", "supabase", "roofmaxxconnect"]:
            try:
                service = self.get_service(service_name)
                service_health = service.health_check()
                health_status["services"][service_name] = service_health
                
                if service_health.get("status") != "healthy":
                    unhealthy_services.append(service_name)
                    
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "error",
                    "error": str(e)
                }
                unhealthy_services.append(service_name)
        
        if unhealthy_services:
            health_status["overall_status"] = "degraded"
            health_status["unhealthy_services"] = unhealthy_services
        
        return health_status
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall configuration status."""
        return {
            "config_loaded": True,
            "environment_file": os.path.exists(".env"),
            "services_available": list(self._services.keys()),
            "agents_configured": list(self.agent_configs.keys()),
            "airtable_configured": bool(self.airtable_token),
            "supabase_configured": bool(self.supabase_url and self.supabase_access_token),
            "roofmaxxconnect_configured": bool(self.roofmaxxconnect_bearer_token)
        }


# Global configuration instance
config = LocalBaseConfig() 