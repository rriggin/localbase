"""
LocalBase Configuration
Centralized configuration for all LocalBase scripts and agents.
"""

import os
from typing import Dict, Any, Optional

# Load environment variables from .env file
try:
    from load_env import load_env
    load_env()
except ImportError:
    # If load_env module is not available, continue without it
    pass

class LocalBaseConfig:
    """Centralized configuration for LocalBase project"""
    
    def __init__(self):
        # Python Configuration
        self.PYTHON_EXECUTABLE = os.getenv("PYTHON_EXECUTABLE", "python3")
        
        # Airtable Configuration - Use environment variables for security
        self.AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
        self.AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "app9Mj5rbIFvK9p9D")
        self.AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Leads")
        self.AIRTABLE_URL = f"https://api.airtable.com/v0/{self.AIRTABLE_BASE_ID}/{self.AIRTABLE_TABLE_NAME}"
        
        # Supabase Configuration
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
        self.SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
        
        # RingCentral Configuration
        self.RINGCENTRAL_CLIENT_ID = os.getenv("RINGCENTRAL_CLIENT_ID")
        self.RINGCENTRAL_CLIENT_SECRET = os.getenv("RINGCENTRAL_CLIENT_SECRET")
        self.RINGCENTRAL_USERNAME = os.getenv("RINGCENTRAL_USERNAME")
        self.RINGCENTRAL_PASSWORD = os.getenv("RINGCENTRAL_PASSWORD")
        self.RINGCENTRAL_ACCOUNT_ID = os.getenv("RINGCENTRAL_ACCOUNT_ID")
        
        # GitHub Configuration
        self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        
        # Clay Configuration
        self.CLAY_API_KEY = os.getenv("CLAY_API_KEY")
        
        # Zapier Configuration
        self.ZAPIER_ROOFR_WEBHOOK_URL = os.getenv("ZAPIER_ROOFR_WEBHOOK_URL")
        self.ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")
        self.ZAPIER_CLAY_WEBHOOK_URL = os.getenv("ZAPIER_CLAY_WEBHOOK_URL")
        
        # ATTOM Data Configuration
        self.ATTOM_API_KEY = os.getenv("ATTOM_API_KEY")
        
        # OpenAI Configuration
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        # Data Source Paths
        self.DATA_DIR = "data"
        self.DISPATCH_CSV_PATH = f"{self.DATA_DIR}/843.csv"
        self.ROOFR_CSV_PATH = f"{self.DATA_DIR}/roofr.csv"
        
        # Field Mappings
        self.FIELD_MAPPINGS = {
            "airtable": {
                "email": "Email",
                "phone": "Phone", 
                "name": "Name",
                "status": "Status",
                "source": "Source",
                "business": "Business",
                "created": "Created",
                "last_modified": "Last Modified",
                "address": "Address Line 1",
                "city": "City",
                "roofr_sync_status": "roofr_sync_status"
            },
            "dispatch": {
                "job_id": "job id",
                "created_date": "created date",
                "customer": "customer",
                "customer_email": "customer_email", 
                "customer_mobile": "customer_mobile",
                "title": "title",
                "street": "street",
                "postal_code": "postal_code",
                "city": "city",
                "status": "status",
                "completed_date": "completed date",
                "reason": "reason",
                "label": "label",
                "notes": "notes",
                "type": "type",
                "source": "source",
                "brand_name": "brand name"
            },
            "roofr": {
                "team_id": "Team Id",
                "team_name": "Team Name", 
                "job_id": "Job ID",
                "job_details": "Job Details",
                "job_created_at": "Job Created at (UTC)",
                "job_address": "Job Address",
                "customer_name": "Customer Name",
                "customer_email": "Customer Email",
                "customer_phone": "Customer Phone",
                "job_lead_source": "Job Lead Source Name",
                "current_status": "Current Job Workflow Stage Name"
            }
        }
        
        # Business Configurations
        self.BUSINESSES = {
            "bud_roofing": {
                "name": "Bud Roofing",
                "source_systems": ["Roofr", "Dispatch"],
                "primary_source": "Roofr"
            },
            "cutcher_lawn": {
                "name": "Cutcher Lawn", 
                "source_systems": ["Yardbook"],
                "primary_source": "Yardbook"
            },
            "royal_services": {
                "name": "Royal Services",
                "source_systems": ["HubSpot"],
                "primary_source": "HubSpot"
            }
        }
        
        # Validate critical configurations
        self._validate_config()
    
    def _validate_config(self):
        """Validate that critical configuration is present"""
        critical_vars = [
            ("AIRTABLE_TOKEN", self.AIRTABLE_TOKEN),
            ("SUPABASE_ACCESS_TOKEN", self.SUPABASE_ACCESS_TOKEN)
        ]
        
        missing_vars = []
        for var_name, var_value in critical_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            print("⚠️  Warning: Missing critical environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            print("   Check your .env file configuration")
    
    def get_supabase_config(self) -> Dict[str, str]:
        """Get Supabase configuration for client initialization"""
        return {
            "url": self.SUPABASE_URL,
            "key": self.SUPABASE_ANON_KEY,
            "access_token": self.SUPABASE_ACCESS_TOKEN
        }
    
    def get_headers_for_airtable(self) -> Dict[str, str]:
        """Get headers for Airtable API requests"""
        return {
            "Authorization": f"Bearer {self.AIRTABLE_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def get_headers_for_supabase(self) -> Dict[str, str]:
        """Get headers for Supabase API requests"""
        return {
            "Authorization": f"Bearer {self.SUPABASE_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "apikey": self.SUPABASE_ANON_KEY
        }
    
    def get_field_name(self, source: str, field_key: str) -> str:
        """Get the actual field name for a given source and field key"""
        return self.FIELD_MAPPINGS.get(source, {}).get(field_key, field_key)
    
    def get_business_config(self, business_key: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific business"""
        return self.BUSINESSES.get(business_key)
    
    def get_status_source_of_truth(self, business_key: str) -> Optional[str]:
        """Get the status source of truth for a business"""
        business_config = self.get_business_config(business_key)
        return business_config.get("primary_source") if business_config else None
    
    def get_status_mapping(self, business_key: str, airtable_status: str) -> Optional[str]:
        """Get the Roofr status mapping for an Airtable status"""
        # This method needs to be updated to use the new BUSINESSES structure
        # For now, returning a placeholder as the original logic was tied to old BUSINESSES
        # and the new BUSINESSES structure doesn't have direct status mappings here.
        # This will need to be re-evaluated based on the new BUSINESSES structure.
        return None # Placeholder
    
    def get_all_status_mappings(self, business_key: str) -> Dict[str, str]:
        """Get all status mappings for a business"""
        # This method needs to be updated to use the new BUSINESSES structure
        # For now, returning an empty dict as the original logic was tied to old BUSINESSES
        # and the new BUSINESSES structure doesn't have direct status mappings here.
        # This will need to be re-evaluated based on the new BUSINESSES structure.
        return {} # Placeholder
    
    def get_data_source_path(self, source: str) -> str:
        """Get the file path for a data source"""
        if source == "dispatch":
            return self.DISPATCH_CSV_PATH
        elif source == "roofr":
            return self.ROOFR_CSV_PATH
        else:
            raise ValueError(f"Unknown data source: {source}")
    
    def validate_config(self) -> bool:
        """Validate that required configuration is present"""
        required_fields = [
            self.AIRTABLE_TOKEN,
            self.AIRTABLE_BASE_ID,
            self.AIRTABLE_TABLE_NAME
        ]
        
        for field in required_fields:
            if not field:
                print(f"Missing required configuration field: {field}")
                return False
        
        return True

# Global config instance
_config = None

def get_config() -> LocalBaseConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = LocalBaseConfig()
    return _config

def get_airtable_config() -> Dict[str, str]:
    """Get Airtable configuration as a dictionary"""
    config = get_config()
    return {
        "token": config.AIRTABLE_TOKEN,
        "base_id": config.AIRTABLE_BASE_ID,
        "table_name": config.AIRTABLE_TABLE_NAME,
        "url": config.AIRTABLE_URL
    }

def get_field_mapping(source: str, field_key: str) -> str:
    """Get field mapping for a source and field key"""
    config = get_config()
    return config.get_field_name(source, field_key)

def get_status_source_of_truth(business_key: str) -> Optional[str]:
    """Get status source of truth for a business"""
    config = get_config()
    return config.get_status_source_of_truth(business_key)

def get_status_mapping(business_key: str, airtable_status: str) -> Optional[str]:
    """Get status mapping for a business and Airtable status"""
    config = get_config()
    return config.get_status_mapping(business_key, airtable_status)

def get_all_status_mappings(business_key: str) -> Dict[str, str]:
    """Get all status mappings for a business"""
    config = get_config()
    return config.get_all_status_mappings(business_key)

def get_python_executable() -> str:
    """Get the Python executable to use for running scripts"""
    config = get_config()
    return config.PYTHON_EXECUTABLE 