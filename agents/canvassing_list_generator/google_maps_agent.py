"""
Google Maps Agent - Professional Architecture
Extract addresses from Google Maps lists and store them in Airtable.
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent, AgentResult, AgentError
from src.services.airtable import AirtableService, AirtableRecord, AirtableRecordBuilder

class GoogleMapsAgent(BaseAgent):
    """
    Professional Google Maps Agent.
    
    Extracts addresses from Google Maps lists and stores them in Airtable
    with proper error handling and monitoring.
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, config: Dict[str, Any], services: Optional[Dict[str, Any]] = None):
        """Initialize the Google Maps Agent."""
        super().__init__(config, services)
        
        # Validate we have required services
        if 'airtable' not in self.services:
            raise AgentError("GoogleMapsAgent requires 'airtable' service", "missing_service")
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters.
        
        Required:
            list_url (str): Google Maps list URL
            
        Optional:
            headless (bool): Run browser in headless mode (default: True)
            timeout (int): Selenium timeout in seconds (default: 15)
        """
        if 'list_url' not in kwargs:
            raise ValueError("'list_url' is required")
        
        list_url = kwargs['list_url']
        if not isinstance(list_url, str) or not list_url.strip():
            raise ValueError("'list_url' must be a non-empty string")
        
        # Basic URL validation
        if not any(domain in list_url for domain in ['maps.app.goo.gl', 'maps.google.com']):
            raise ValueError("'list_url' must be a valid Google Maps URL")
        
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute Google Maps address extraction.
        
        Args:
            list_url (str): Google Maps list URL to scrape
            headless (bool): Run browser in headless mode (default: True)
            timeout (int): Selenium timeout (default: 15)
            save_to_airtable (bool): Save results to Airtable (default: True)
            business_name (str): Business name for Airtable records (default: "Google Maps Import")
            
        Returns:
            AgentResult with extracted addresses
        """
        # Validate input
        self.validate_input(**kwargs)
        
        list_url = kwargs['list_url']
        headless = kwargs.get('headless', True)
        timeout = kwargs.get('timeout', 15)
        save_to_airtable = kwargs.get('save_to_airtable', True)
        business_name = kwargs.get('business_name', "Google Maps Import")
        
        self._log_execution("Starting Google Maps extraction", 
                          list_url=list_url, headless=headless, timeout=timeout)
        
        try:
            # Use the existing scraper for now (we'll create a service later)
            from .scraper import GoogleMapsListScraper
            
            scraper = GoogleMapsListScraper(headless=headless, timeout=timeout)
            scraper.start()
            
            # Extract addresses
            self.logger.info(f"Scraping addresses from: {list_url}")
            address_items = scraper.scrape_addresses(list_url)
            
            if not address_items:
                scraper.stop()
                return AgentResult(
                    success=False,
                    error="No addresses found in the Google Maps list",
                    metadata={"list_url": list_url}
                ).to_dict()
            
            # Convert to our format
            addresses = []
            for item in address_items:
                addresses.append({
                    "address": item.address,
                    "name": item.name,
                    "source": "Google Maps List",
                    "list_url": list_url,
                    "extracted_at": datetime.now().isoformat()
                })
            
            scraper.stop()
            
            # Save to Airtable if requested
            if save_to_airtable:
                stored_records = self._save_to_airtable(addresses, business_name)
                self.logger.info(f"Saved {len(stored_records)} records to Airtable")
            
            self.logger.info(f"Successfully extracted {len(addresses)} addresses")
            
            return AgentResult(
                success=True,
                data={
                    "addresses": addresses,
                    "total_count": len(addresses),
                    "list_url": list_url,
                    "saved_to_airtable": save_to_airtable
                },
                metadata={
                    "agent_version": self.VERSION,
                    "extraction_time": datetime.now().isoformat(),
                    "headless": headless,
                    "timeout": timeout
                }
            ).to_dict()
            
        except Exception as e:
            self.logger.error(f"Google Maps extraction failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"list_url": list_url}
            ).to_dict()
    
    def _save_to_airtable(self, addresses: List[Dict[str, Any]], business_name: str) -> List[AirtableRecord]:
        """Save addresses to Airtable."""
        airtable: AirtableService = self.services['airtable']
        stored_records = []
        
        for address_data in addresses:
            try:
                # Build Airtable record
                record_data = (AirtableRecordBuilder()
                    .add_field("Name", address_data.get('name', 'Unknown'))
                    .add_field("Address", address_data['address'])
                    .add_field("Business", business_name)
                    .add_field("Source System", "Google Maps Agent")
                    .add_field("Source", address_data['source'])
                    .add_field("List URL", address_data['list_url'])
                    .add_field("Extracted Date", address_data['extracted_at'])
                    .add_timestamp_fields()
                    .build()
                )
                
                record = airtable.create_record(record_data)
                stored_records.append(record)
                
            except Exception as e:
                self.logger.warning(f"Failed to save address to Airtable: {address_data['address']} - {e}")
                continue
        
        return stored_records
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        status = super().get_status()
        status.update({
            "agent_type": "google_maps",
            "capabilities": [
                "extract_addresses_from_maps_lists",
                "save_to_airtable", 
                "selenium_scraping"
            ],
            "required_services": ["airtable"],
            "version": self.VERSION
        })
        return status 