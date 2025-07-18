"""
ATTOM Property Enrichment Agent

Professional MCP agent for enriching addresses with residential property data
using the ATTOM Data API. Follows the BaseAgent architecture with dependency injection.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd

from agents.base_agent import BaseAgent, AgentResult, AgentError
from src.services.airtable import AirtableService, AirtableRecord, AirtableRecordBuilder


class AttomPropertyAgent(BaseAgent):
    """
    ATTOM Property Enrichment Agent
    
    Enriches address data with comprehensive residential property information including:
    - Home value estimates (AVM)
    - Year built, beds, baths, square footage
    - Owner information
    - Sales history
    - Tax assessment data
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, config: Dict[str, Any], services: Optional[Dict[str, Any]] = None):
        super().__init__(config, services)
        
        # Validate required services
        if 'airtable' not in self.services:
            raise AgentError("AttomPropertyAgent requires 'airtable' service", "missing_service")
        
        # ATTOM API configuration
        self.api_key = config.get('config', {}).get('api_key')
        if not self.api_key:
            raise AgentError("ATTOM API key is required", "missing_api_key")
            
        self.base_url = config.get('config', {}).get('base_url', 
                                                    "https://api.gateway.attomdata.com/propertyapi/v1.0.0")
        self.rate_limit_delay = config.get('config', {}).get('rate_limit_delay', 1.1)
        self.batch_size = config.get('config', {}).get('batch_size', 50)
        self.max_retries = config.get('config', {}).get('max_retries', 3)
        self.timeout = config.get('config', {}).get('timeout', 30)
        
        # API headers
        self.headers = {
            "accept": "application/json",
            "apikey": self.api_key
        }
        
        self.logger.info(f"AttomPropertyAgent v{self.VERSION} initialized with batch size {self.batch_size}")
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters for ATTOM property enrichment."""
        addresses = kwargs.get('addresses')
        
        if not addresses:
            raise AgentError("'addresses' parameter is required", "invalid_input")
        
        if isinstance(addresses, str):
            # Single address as string
            return True
        elif isinstance(addresses, list):
            if len(addresses) == 0:
                raise AgentError("Address list cannot be empty", "invalid_input")
            return True
        elif isinstance(addresses, pd.DataFrame):
            if addresses.empty:
                raise AgentError("Address DataFrame cannot be empty", "invalid_input")
            required_columns = ['address', 'city', 'state']
            missing_columns = [col for col in required_columns if col not in addresses.columns]
            if missing_columns:
                raise AgentError(f"DataFrame missing required columns: {missing_columns}", "invalid_input")
            return True
        else:
            raise AgentError("'addresses' must be string, list, or DataFrame", "invalid_input")
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute ATTOM property enrichment for addresses.
        
        Args:
            addresses: Address data (string, list, or DataFrame)
            save_to_airtable: Whether to save enriched data to Airtable (default: True)
            business_name: Business name for Airtable records (default: "ATTOM Property Data")
            
        Returns:
            AgentResult with enrichment statistics and data
        """
        try:
            addresses = kwargs.get('addresses')
            save_to_airtable = kwargs.get('save_to_airtable', True)
            business_name = kwargs.get('business_name', "ATTOM Property Data")
            
            self.logger.info(f"Starting ATTOM property enrichment: {kwargs}")
            
            # Normalize addresses to DataFrame
            address_df = self._normalize_addresses(addresses)
            total_addresses = len(address_df)
            
            self.logger.info(f"Processing {total_addresses} addresses for property enrichment")
            
            # Process addresses in batches
            enriched_records = []
            successful_enrichments = 0
            failed_enrichments = 0
            
            for i in range(0, total_addresses, self.batch_size):
                batch = address_df.iloc[i:i + self.batch_size]
                
                self.logger.info(f"Processing batch {i//self.batch_size + 1}: {len(batch)} addresses")
                
                for _, row in batch.iterrows():
                    try:
                        property_data = self._get_property_data(
                            address=row['address'],
                            city=row['city'], 
                            state=row['state'],
                            zip_code=row.get('zip_code')
                        )
                        
                        if property_data:
                            enriched_record = self._build_enriched_record(row, property_data, business_name)
                            enriched_records.append(enriched_record)
                            successful_enrichments += 1
                        else:
                            failed_enrichments += 1
                            
                        # Rate limiting
                        time.sleep(self.rate_limit_delay)
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to enrich address {row['address']}: {str(e)}")
                        failed_enrichments += 1
                        continue
            
            # Save to Airtable if requested
            airtable_records_created = 0
            if save_to_airtable and enriched_records:
                airtable_service: AirtableService = self.services['airtable']
                
                for record in enriched_records:
                    try:
                        result = airtable_service.create_record(record)
                        if result:
                            airtable_records_created += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to save record to Airtable: {str(e)}")
                        continue
            
            # Build result
            result_data = {
                "total_addresses": total_addresses,
                "successful_enrichments": successful_enrichments,
                "failed_enrichments": failed_enrichments,
                "enriched_records": enriched_records,
                "airtable_records_created": airtable_records_created,
                "save_to_airtable": save_to_airtable
            }
            
            self.logger.info(f"ATTOM enrichment completed: {successful_enrichments}/{total_addresses} successful")
            
            return AgentResult(
                success=True,
                data=result_data,
                metadata={"agent_name": "AttomPropertyAgent", "version": self.VERSION}
            ).to_dict()
            
        except Exception as e:
            error_msg = f"ATTOM property enrichment failed: {str(e)}"
            self.logger.error(error_msg)
            raise AgentError(error_msg, "execution_failed")
    
    def _normalize_addresses(self, addresses) -> pd.DataFrame:
        """Normalize various address input formats to DataFrame."""
        if isinstance(addresses, str):
            # Single address string - try to parse
            parts = addresses.split(',')
            if len(parts) >= 3:
                return pd.DataFrame([{
                    'address': parts[0].strip(),
                    'city': parts[1].strip(),
                    'state': parts[2].strip(),
                    'zip_code': parts[3].strip() if len(parts) > 3 else None
                }])
            else:
                raise AgentError("Address string must include at least address, city, state", "invalid_format")
                
        elif isinstance(addresses, list):
            # List of address strings or dictionaries
            normalized = []
            for addr in addresses:
                if isinstance(addr, str):
                    parts = addr.split(',')
                    if len(parts) >= 3:
                        normalized.append({
                            'address': parts[0].strip(),
                            'city': parts[1].strip(),
                            'state': parts[2].strip(),
                            'zip_code': parts[3].strip() if len(parts) > 3 else None
                        })
                elif isinstance(addr, dict):
                    normalized.append(addr)
            return pd.DataFrame(normalized)
            
        elif isinstance(addresses, pd.DataFrame):
            return addresses
            
        else:
            raise AgentError("Unsupported address format", "invalid_format")
    
    def _get_property_data(self, address: str, city: str, state: str, zip_code: str = None) -> Optional[Dict]:
        """Get property data from ATTOM Data API with retries."""
        
        # Build API parameters (using correct ATTOM API format)
        params = {
            "address1": address,
            "address2": f"{city} {state}"
        }
        # Note: postalcode parameter causes "Invalid Parameter Combination" error with ATTOM API
        # So we include zip in address2 if available, but don't use separate postalcode param
        if zip_code:
            params["address2"] = f"{city} {state} {zip_code}"
        
        url = f"{self.base_url}/property/detail"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status', {}).get('code') == 0 and data.get('property'):
                        return data['property'][0] if data['property'] else None
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = (attempt + 1) * 2
                    self.logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 404:
                    # Property not found
                    return None
                else:
                    self.logger.warning(f"API error {response.status_code}: {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep((attempt + 1) * 1.5)
                    continue
                return None
        
        return None
    
    def _build_enriched_record(self, address_row: pd.Series, property_data: Dict, business_name: str) -> Dict[str, Any]:
        """Build an enriched record for Airtable from property data."""
        
        builder = AirtableRecordBuilder()
        
        # Original address information
        builder.add_field("Address", address_row['address'])
        builder.add_field("City", address_row['city'])
        builder.add_field("State", address_row['state'])
        if address_row.get('zip_code'):
            builder.add_field("Zip Code", address_row['zip_code'])
        
        # Add business fields
        builder.add_business_fields(business_name, "ATTOM Data API")
        
        # Property characteristics
        building = property_data.get('building', {})
        if building:
            builder.add_field("Year Built", building.get('yearBuilt'))
            builder.add_field("Bedrooms", building.get('rooms', {}).get('beds'))
            builder.add_field("Bathrooms", building.get('rooms', {}).get('bathstotal'))
            builder.add_field("Living Sqft", building.get('size', {}).get('livingsize'))
            builder.add_field("Total Sqft", building.get('size', {}).get('universalsize'))
        
        # Property value estimates
        assessment = property_data.get('assessment', {})
        if assessment:
            builder.add_field("Assessed Value", assessment.get('assessed', {}).get('assdttlvalue'))
            builder.add_field("Market Value", assessment.get('market', {}).get('mktttlvalue'))
        
        # AVM (Automated Valuation Model)
        avm = property_data.get('avm', {})
        if avm:
            builder.add_field("AVM Estimate", avm.get('amount', {}).get('value'))
            builder.add_field("AVM Confidence", avm.get('eventinfo', {}).get('confidence'))
        
        # Lot information
        lot = property_data.get('lot', {})
        if lot:
            builder.add_field("Lot Size", lot.get('lotsize1'))
        
        # Owner information
        owner = property_data.get('owner', {})
        if owner:
            builder.add_field("Owner Name", owner.get('owner1', {}).get('lastname'))
        
        # Add timestamp fields
        builder.add_timestamp_fields()
        
        return builder.build() 