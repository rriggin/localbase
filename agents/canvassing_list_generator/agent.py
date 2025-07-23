"""
Google Maps Agent - Professional Architecture
Extract addresses from Google Maps lists and store them in Airtable.
"""

import sys
import os
import requests
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
        
        # Airtable service is optional - only needed for legacy workflow
        # Validation will happen in execute() method
    
    def validate_input(self, **kwargs) -> None:
        """Validate input parameters for the agent."""
        required_fields = ['list_url']
        
        for field in required_fields:
            if field not in kwargs or not kwargs[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate URL format
        list_url = kwargs['list_url']
        if not self._is_valid_google_maps_url(list_url):
            raise ValueError(f"Invalid Google Maps URL: {list_url}")
    
    def _is_valid_google_maps_url(self, url: str) -> bool:
        """Validate if the URL is a valid Google Maps URL."""
        valid_patterns = [
            'maps.google.com',
            'www.google.com/maps',
            'google.com/maps',
            'maps.app.goo.gl'
        ]
        
        return any(pattern in url.lower() for pattern in valid_patterns)
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Google Maps list scraping agent."""
        try:
            # Extract parameters
            list_url = input_data.get('list_url', '')
            list_title = input_data.get('list_title', '')
            headless = input_data.get('headless', True)
            timeout = input_data.get('timeout', 60)
            
            # Validate required inputs
            if not list_url:
                raise ValueError("list_url is required")
            
            # Extract list title from page if not provided
            if not list_title:
                try:
                    from .scraper import GoogleMapsListScraper
                    temp_scraper = GoogleMapsListScraper(headless=True, timeout=30)
                    temp_scraper.start()
                    list_title = temp_scraper.get_list_title(list_url)
                    temp_scraper.stop()
                    
                    if list_title:
                        self.logger.info(f"📋 Extracted list title: {list_title}")
                    else:
                        list_title = "Google Maps List"
                        self.logger.info(f"📋 Using default list title: {list_title}")
                except Exception as e:
                    self.logger.warning(f"Could not extract list title: {e}")
                    list_title = "Google Maps List"
            
            # Validate the URL
            if not self._is_valid_google_maps_url(list_url):
                raise ValueError("Invalid Google Maps URL provided")
            
            self.logger.info(f"🚀 Starting extraction from Google Maps list: {list_title}")
            
            # Try different extraction methods
            address_items = []
            
            # Method 1: Try shared list extractor first (best for large lists)
            try:
                address_items = self._extract_from_shared_list(list_url)
                if len(address_items) < 50:  # If we get limited results, try dynamic scraper
                    self.logger.info(f"Shared extractor returned {len(address_items)} addresses, trying dynamic scraper for more...")
                    dynamic_items = self._extract_with_dynamic_scraper(list_url, headless, timeout)
                    if len(dynamic_items) > len(address_items):
                        address_items = dynamic_items
                        self.logger.info(f"Dynamic scraper found more addresses: {len(address_items)}")
            except Exception as e:
                self.logger.warning(f"Shared list extraction failed: {e}")
                # Fallback to dynamic scraper
                address_items = self._extract_with_dynamic_scraper(list_url, headless, timeout)
            
            if not address_items:
                return {
                    "status": "error",
                    "message": "No addresses found in the Google Maps list",
                    "addresses_count": 0
                }
            
            # Convert to standardized format
            addresses = []
            for item in address_items:
                address_data = {
                    'address': item.address if hasattr(item, 'address') else str(item),
                    'name': item.name if hasattr(item, 'name') else '',
                    'source': f'Google Maps Agent - {list_title}',
                    'list_url': list_url,
                    'extracted_at': datetime.now().isoformat()
                }
                addresses.append(address_data)
            
            # Always use gist workflow
            self._save_to_gist_workflow(addresses, list_title)
            
            return {
                "status": "success",
                "message": f"Successfully extracted {len(addresses)} addresses from Google Maps list",
                "addresses_count": len(addresses),
                "list_title": list_title,
                "list_url": list_url,
                "workflow": "gist"
            }
            
        except Exception as e:
            self.logger.error(f"Google Maps extraction failed: {e}")
            return {
                "status": "error", 
                "message": str(e),
                "addresses_count": 0
            }
    
    def _extract_from_shared_list(self, list_url: str) -> List[Any]:
        """Extract addresses using the shared list extractor."""
        try:
            from .backup.shared_list_extractor import SharedListExtractor
            
            extractor = SharedListExtractor()
            places = extractor.extract_from_shared_list(list_url)
            
            # Convert to AddressItem format
            from .scraper import AddressItem
            address_items = []
            for place in places:
                address_items.append(AddressItem(
                    address=place.address or f"{place.latitude}, {place.longitude}",
                    name=place.name
                ))
            
            return address_items
            
        except Exception as e:
            self.logger.warning(f"Shared list extraction failed: {e}")
            return []
    
    def _extract_with_dynamic_scraper(self, list_url: str, headless: bool, timeout: int) -> List[Any]:
        """Extract addresses using the dynamic scraper optimized for large lists."""
        try:
            from .backup.dynamic_list_scraper import DynamicListScraper
            
            self.logger.info("Using dynamic scraper for large list extraction...")
            scraper = DynamicListScraper(headless=headless)
            
            # Extract addresses using dynamic scrolling
            addresses = scraper.extract_addresses_from_list(list_url, max_scroll_attempts=100)
            
            # Convert to AddressItem format
            from .scraper import AddressItem
            address_items = []
            for addr in addresses:
                address_items.append(AddressItem(
                    address=addr.address,
                    name=addr.name
                ))
            
            self.logger.info(f"Dynamic scraper found {len(address_items)} addresses")
            return address_items
            
        except Exception as e:
            self.logger.error(f"Dynamic scraper failed: {e}")
            # Fallback to basic scraper
            return self._extract_with_basic_scraper(list_url, headless, timeout)
    
    def _extract_with_basic_scraper(self, list_url: str, headless: bool, timeout: int) -> List[Any]:
        """Fallback to basic scraper if dynamic scraper fails."""
        try:
            from .scraper import GoogleMapsListScraper
            
            self.logger.info("Using basic scraper as fallback...")
            scraper = GoogleMapsListScraper(headless=headless, timeout=timeout)
            scraper.start()
            
            address_items = scraper.scrape_addresses(list_url)
            scraper.stop()
            
            return address_items
            
        except Exception as e:
            self.logger.error(f"Basic scraper failed: {e}")
            return []
    
    def _save_to_gist_workflow(self, addresses: List[Dict[str, Any]], list_title: str):
        """Save addresses following the gist → Zapier → Clay workflow."""
        try:
            # Save to CSV first
            import csv
            import os
            
            # Ensure data directory exists
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Save raw addresses
            csv_file = os.path.join(data_dir, 'addresses.csv')
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['address', 'name', 'source', 'list_url', 'extracted_at'])
                writer.writeheader()
                for addr in addresses:
                    writer.writerow(addr)
            
            self.logger.info(f"Saved {len(addresses)} addresses to {csv_file}")
            
            # Format for gist using the dedicated script
            self._format_for_gist(addresses, list_title)
            
            # Update gist (if available)
            self._update_gist()
            
            self.logger.info("✅ Gist workflow completed - addresses ready for Clay import via Zapier")
            
        except Exception as e:
            self.logger.error(f"Gist workflow failed: {e}")
    
    def _format_for_gist(self, addresses: List[Dict[str, Any]], list_title: str):
        """Format addresses for Gist - consolidated logic from backup scripts."""
        try:
            import csv
            import os
            import re
            from datetime import datetime
            
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            gist_file = os.path.join(data_dir, 'addresses_formatted_for_gist.csv')
            
            # Gist format headers
            headers = [
                'name', 'address', 'street_address', 'city', 'state', 'zip_code', 
                'full_address', 'source', 'import_date', 'import_time'
            ]
            
            current_time = datetime.now()
            import_date = current_time.strftime('%Y-%m-%d')
            import_time = current_time.strftime('%H:%M:%S')
            
            with open(gist_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                
                for addr in addresses:
                    # Parse address components
                    address_parts = self._parse_address(addr['address'])
                    
                    formatted_row = {
                        'name': addr.get('name', ''),
                        'address': addr['address'],
                        'street_address': address_parts['street_address'],
                        'city': address_parts['city'],
                        'state': address_parts['state'],
                        'zip_code': address_parts['zip_code'],
                        'full_address': addr['address'],
                        'source': f'Google Maps List Scraper - {list_title}',
                        'import_date': import_date,
                        'import_time': import_time
                    }
                    writer.writerow(formatted_row)
            
            self.logger.info(f"✅ Addresses formatted for Gist: {len(addresses)} addresses saved to {gist_file}")
            
        except Exception as e:
            self.logger.error(f"Gist formatting failed: {e}")
    
    def _update_gist(self):
        """Update GitHub gist with new addresses - consolidated logic."""
        try:
            import os
            import requests
            import csv
            from datetime import datetime
            from dotenv import load_dotenv
            
            # Load environment variables
            load_dotenv('../../.env')
            
            GIST_ID = "1cb623ab465f4ebe6ddf3a934bacc5a7"
            github_token = os.getenv("GITHUB_TOKEN")
            
            if not github_token:
                self.logger.warning("GITHUB_TOKEN not found - skipping Gist update")
                return
            
            # Get new data file
            csv_path = os.path.join(os.path.dirname(__file__), 'data', 'addresses_formatted_for_gist.csv')
            if not os.path.exists(csv_path):
                self.logger.error(f"CSV file not found: {csv_path}")
                return
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                new_content = f.read().strip()
            
            # Get existing Gist content
            existing_content = self._get_existing_gist_content(github_token, GIST_ID)
            
            # Combine content (append new to existing)
            combined_content, total_addresses = self._append_new_data_to_gist(existing_content, new_content)
            
            # Update the gist
            url = f"https://api.github.com/gists/{GIST_ID}"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            payload = {
                "description": f"Canvassing Data - Running Record - {total_addresses} Total Addresses - Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "files": {
                    "canvassing-data": {
                        "content": combined_content
                    }
                }
            }
            
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            gist_url = data["html_url"]
            raw_url = f"https://gist.githubusercontent.com/rriggin/{GIST_ID}/raw/canvassing-data"
            
            self.logger.info("✅ GitHub Gist updated successfully!")
            self.logger.info(f"   Gist URL: {gist_url}")
            self.logger.info(f"   Raw CSV URL: {raw_url}")
            self.logger.info(f"   Total addresses: {total_addresses}")
            
        except Exception as e:
            self.logger.warning(f"Gist update failed: {e}")
    
    def _get_existing_gist_content(self, github_token: str, gist_id: str) -> str:
        """Download the current content of the Gist."""
        try:
            url = f"https://api.github.com/gists/{gist_id}"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if "canvassing-data" in data["files"]:
                return data["files"]["canvassing-data"]["content"]
            else:
                return ""
                
        except Exception as e:
            self.logger.warning(f"Could not fetch existing Gist content: {e}")
            return ""
    
    def _append_new_data_to_gist(self, existing_content: str, new_content: str) -> tuple:
        """Append new CSV data to existing Gist content."""
        import csv
        import io
        
        if existing_content:
            self.logger.info(f"📥 Found existing Gist content, appending new data...")
            
            # Parse existing content
            existing_lines = existing_content.strip().split('\n')
            header_line = existing_lines[0] if existing_lines else ""
            existing_data_lines = existing_lines[1:] if len(existing_lines) > 1 else []
            
            # Parse new content
            new_lines = new_content.strip().split('\n')
            new_data_lines = new_lines[1:] if len(new_lines) > 1 else []  # Skip header
            
            # Create set of existing addresses to avoid duplicates
            existing_addresses = set()
            for line in existing_data_lines:
                if line.strip():
                    try:
                        reader = csv.reader([line])
                        row = next(reader)
                        if len(row) > 1:
                            existing_addresses.add(row[1].strip())  # address column
                    except:
                        continue
            
            # Filter out duplicate addresses from new data
            new_unique_lines = []
            duplicates_count = 0
            for line in new_data_lines:
                if line.strip():
                    try:
                        reader = csv.reader([line])
                        row = next(reader)
                        if len(row) > 1:
                            address = row[1].strip()
                            if address not in existing_addresses:
                                new_unique_lines.append(line)
                                existing_addresses.add(address)
                            else:
                                duplicates_count += 1
                    except:
                        continue
            
            if duplicates_count > 0:
                self.logger.info(f"🔄 Skipped {duplicates_count} duplicate addresses")
            
            if new_unique_lines:
                combined_content = header_line + '\n' + '\n'.join(existing_data_lines + new_unique_lines)
                total_addresses = len(existing_data_lines) + len(new_unique_lines)
                self.logger.info(f"✅ Adding {len(new_unique_lines)} new addresses to existing {len(existing_data_lines)} addresses")
                self.logger.info(f"📊 Total addresses in Gist: {total_addresses}")
            else:
                self.logger.info("ℹ️  No new unique addresses to add")
                combined_content = existing_content
                total_addresses = len(existing_data_lines)
        else:
            self.logger.info(f"📝 No existing Gist content found, creating new...")
            combined_content = new_content
            new_lines = new_content.strip().split('\n')
            total_addresses = len(new_lines) - 1 if len(new_lines) > 1 else 0
        
        return combined_content, total_addresses

    def _manual_format_for_gist(self, addresses: List[Dict[str, Any]], list_title: str):
        """Manual fallback for gist formatting."""
        # This method is now redundant since _format_for_gist handles everything
        self._format_for_gist(addresses, list_title)

    def _format_for_clay(self, addresses: List[Dict[str, Any]], list_title: str):
        """Format addresses for Clay import (legacy method, now redirects to gist format)."""
        # Redirect to gist formatting since that's the current workflow
        self._format_for_gist(addresses, list_title)
    
    def _parse_address(self, address: str) -> Dict[str, str]:
        """Parse address into components."""
        import re
        
        result = {
            'street_address': address,
            'city': '',
            'state': '',
            'zip_code': ''
        }
        
        # Try to parse address components
        parts = [part.strip() for part in address.split(',')]
        
        if len(parts) >= 3:
            result['street_address'] = parts[0]
            result['city'] = parts[1]
            
            state_zip = parts[2].strip()
            state_zip_match = re.match(r'^([A-Z]{2})\s+(\d{5}(?:-\d{4})?).*$', state_zip)
            if state_zip_match:
                result['state'] = state_zip_match.group(1)
                result['zip_code'] = state_zip_match.group(2)
        
        return result
    
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