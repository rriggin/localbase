"""
Real Estate Data Enrichment Agent

This agent takes address data and enriches it with property information including:
- Home value estimates
- Year built
- Property characteristics (beds, baths, sqft)
- Owner information
- Sales history
- Tax assessment data

Uses RentCast API for property data retrieval.
"""

import requests
import pandas as pd
import time
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealEstateEnrichmentAgent:
    """Agent for enriching address data with real estate information."""
    
    def __init__(self, api_key: str):
        """
        Initialize the agent with RentCast API key.
        
        Args:
            api_key: RentCast API key
        """
        self.api_key = api_key
        self.base_url = "https://api.rentcast.io/v1"
        self.headers = {
            "accept": "application/json",
            "X-Api-Key": api_key
        }
        self.rate_limit_delay = 1.1  # Delay between requests to respect rate limits
        
    def get_property_data(self, address: str, city: str, state: str, zip_code: str = None) -> Optional[Dict]:
        """
        Get property data for a given address.
        
        Args:
            address: Street address
            city: City name
            state: State abbreviation
            zip_code: ZIP code (optional)
            
        Returns:
            Dictionary containing property data or None if not found
        """
        # Construct full address
        full_address = f"{address}, {city}, {state}"
        if zip_code:
            full_address += f" {zip_code}"
            
        # Property Records endpoint
        url = f"{self.base_url}/properties"
        params = {
            "address": full_address,
            "limit": 1
        }
        
        try:
            logger.info(f"Fetching property data for: {full_address}")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return data[0]  # Return first match
                else:
                    logger.warning(f"No property data found for: {full_address}")
                    return None
            elif response.status_code == 429:
                logger.warning("Rate limit hit, waiting longer...")
                time.sleep(5)
                return self.get_property_data(address, city, state, zip_code)
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching property data for {full_address}: {str(e)}")
            return None
            
    def get_property_value(self, address: str, city: str, state: str, zip_code: str = None) -> Optional[Dict]:
        """
        Get property value estimate for a given address.
        
        Args:
            address: Street address
            city: City name
            state: State abbreviation
            zip_code: ZIP code (optional)
            
        Returns:
            Dictionary containing value estimate data or None if not found
        """
        # Construct full address
        full_address = f"{address}, {city}, {state}"
        if zip_code:
            full_address += f" {zip_code}"
            
        # Value Estimate endpoint
        url = f"{self.base_url}/properties/value"
        params = {
            "address": full_address
        }
        
        try:
            logger.info(f"Fetching property value for: {full_address}")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 429:
                logger.warning("Rate limit hit, waiting longer...")
                time.sleep(5)
                return self.get_property_value(address, city, state, zip_code)
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching property value for {full_address}: {str(e)}")
            return None
            
    def enrich_property_data(self, property_data: Dict, value_data: Dict = None) -> Dict:
        """
        Extract and format relevant property information.
        
        Args:
            property_data: Raw property data from API
            value_data: Raw value data from API
            
        Returns:
            Dictionary with enriched property information
        """
        enriched = {}
        
        try:
            # Basic property info
            enriched['property_id'] = property_data.get('id')
            enriched['year_built'] = property_data.get('yearBuilt')
            enriched['property_type'] = property_data.get('propertyType')
            enriched['property_subtype'] = property_data.get('propertySubType')
            
            # Property characteristics
            enriched['bedrooms'] = property_data.get('bedrooms')
            enriched['bathrooms'] = property_data.get('bathrooms')
            enriched['square_feet'] = property_data.get('squareFootage')
            enriched['lot_size'] = property_data.get('lotSize')
            
            # Financial data
            enriched['assessed_value'] = property_data.get('assessedValue')
            enriched['market_value'] = property_data.get('marketValue')
            enriched['tax_amount'] = property_data.get('taxAmount')
            enriched['tax_year'] = property_data.get('taxYear')
            
            # Owner information
            owner_info = property_data.get('owner', {})
            enriched['owner_name'] = owner_info.get('name')
            enriched['owner_occupied'] = owner_info.get('ownerOccupied')
            
            # Sales history
            last_sale = property_data.get('lastSale', {})
            enriched['last_sale_date'] = last_sale.get('date')
            enriched['last_sale_price'] = last_sale.get('amount')
            
            # Value estimate if available
            if value_data:
                enriched['estimated_value'] = value_data.get('value')
                enriched['value_range_low'] = value_data.get('valueLow')
                enriched['value_range_high'] = value_data.get('valueHigh')
                enriched['confidence_score'] = value_data.get('confidenceScore')
                
            # Address validation
            address_info = property_data.get('address', {})
            enriched['formatted_address'] = address_info.get('line')
            enriched['latitude'] = address_info.get('latitude')
            enriched['longitude'] = address_info.get('longitude')
            
            # Processing metadata
            enriched['data_source'] = 'RentCast API'
            enriched['enrichment_date'] = datetime.now().strftime('%Y-%m-%d')
            enriched['enrichment_time'] = datetime.now().strftime('%H:%M:%S')
            
        except Exception as e:
            logger.error(f"Error enriching property data: {str(e)}")
            
        return enriched
        
    def process_address_list(self, csv_file_path: str, output_file_path: str = None, max_records: int = None) -> pd.DataFrame:
        """
        Process a CSV file of addresses and enrich with property data.
        
        Args:
            csv_file_path: Path to input CSV file
            output_file_path: Path for output CSV file (optional)
            max_records: Maximum number of records to process (for testing)
            
        Returns:
            DataFrame with enriched property data
        """
        logger.info(f"Processing address list from: {csv_file_path}")
        
        # Read input CSV
        df = pd.read_csv(csv_file_path)
        
        if max_records:
            df = df.head(max_records)
            logger.info(f"Processing first {max_records} records for testing")
            
        # Initialize results list
        enriched_records = []
        
        # Process each address
        for index, row in df.iterrows():
            logger.info(f"Processing record {index + 1}/{len(df)}")
            
            # Extract address components
            street_address = row.get('street_address', '')
            city = row.get('city', '')
            state = row.get('state', '')
            zip_code = row.get('zip_code', '')
            
            # Get property data
            property_data = self.get_property_data(street_address, city, state, zip_code)
            value_data = None
            
            if property_data:
                # Get value estimate
                value_data = self.get_property_value(street_address, city, state, zip_code)
                time.sleep(self.rate_limit_delay)  # Rate limiting
                
            # Enrich the data
            enriched = self.enrich_property_data(property_data or {}, value_data)
            
            # Combine with original data
            enriched_record = row.to_dict()
            enriched_record.update(enriched)
            enriched_records.append(enriched_record)
            
            # Rate limiting between requests
            time.sleep(self.rate_limit_delay)
            
        # Create DataFrame
        enriched_df = pd.DataFrame(enriched_records)
        
        # Save to file if specified
        if output_file_path:
            enriched_df.to_csv(output_file_path, index=False)
            logger.info(f"Enriched data saved to: {output_file_path}")
            
        logger.info(f"Successfully processed {len(enriched_df)} records")
        return enriched_df

def main():
    """Main function for testing the agent."""
    # Load API key from environment
    api_key = os.getenv('RENTCAST_API_KEY')
    if not api_key:
        logger.error("RENTCAST_API_KEY environment variable not set")
        return
        
    # Initialize agent
    agent = RealEstateEnrichmentAgent(api_key)
    
    # Process the address list (test with first 5 records)
    input_file = "data/addresses_for_clay.csv"
    output_file = "data/addresses_enriched_with_property_data.csv"
    
    try:
        enriched_df = agent.process_address_list(
            csv_file_path=input_file,
            output_file_path=output_file,
            max_records=5  # Test with 5 records first
        )
        
        # Display sample results
        print("\n=== Sample Enriched Data ===")
        columns_to_show = [
            'street_address', 'city', 'state', 'year_built', 
            'estimated_value', 'bedrooms', 'bathrooms', 'square_feet'
        ]
        available_columns = [col for col in columns_to_show if col in enriched_df.columns]
        print(enriched_df[available_columns].head())
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 