"""
Residential Property Data Enrichment Agent

This agent takes address data and enriches it with residential property information including:
- Home value estimates (AVM)
- Year built
- Property characteristics (beds, baths, sqft)
- Owner information
- Sales history
- Tax assessment data

Uses ATTOM Data API for comprehensive residential property data.
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

class ResidentialPropertyEnrichmentAgent:
    """Agent for enriching address data with residential property information."""
    
    def __init__(self, api_key: str):
        """
        Initialize the agent with ATTOM Data API key.
        
        Args:
            api_key: ATTOM Data API key
        """
        self.api_key = api_key
        self.base_url = "https://search.onboard-apis.com/propertyapi/v1.0.0"
        self.headers = {
            "accept": "application/json",
            "apikey": api_key
        }
        self.rate_limit_delay = 1.1  # Delay between requests to respect rate limits
        
    def get_property_data(self, address: str, city: str, state: str, zip_code: str = None) -> Optional[Dict]:
        """
        Get property data for a given address using ATTOM Data API.
        
        Args:
            address: Street address
            city: City name
            state: State abbreviation
            zip_code: ZIP code (optional)
            
        Returns:
            Dictionary containing property data or None if not found
        """
        # Property/Detail endpoint
        url = f"{self.base_url}/property/detail"
        params = {
            "address1": address,
            "address2": f"{city}, {state}",
        }
        
        if zip_code:
            params["postalcode"] = zip_code
            
        try:
            logger.info(f"Fetching property data for: {address}, {city}, {state}")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data and data.get('property'):
                    return data['property'][0] if isinstance(data['property'], list) else data['property']
                else:
                    logger.warning(f"No property data found for: {address}, {city}, {state}")
                    return None
            elif response.status_code == 429:
                logger.warning("Rate limit hit, waiting longer...")
                time.sleep(5)
                return self.get_property_data(address, city, state, zip_code)
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching property data for {address}: {str(e)}")
            return None
            
    def get_property_avm(self, address: str, city: str, state: str, zip_code: str = None) -> Optional[Dict]:
        """
        Get AVM (Automated Valuation Model) for a given address.
        
        Args:
            address: Street address
            city: City name
            state: State abbreviation
            zip_code: ZIP code (optional)
            
        Returns:
            Dictionary containing AVM data or None if not found
        """
        # AVM endpoint
        url = f"{self.base_url}/avm"
        params = {
            "address1": address,
            "address2": f"{city}, {state}",
        }
        
        if zip_code:
            params["postalcode"] = zip_code
            
        try:
            logger.info(f"Fetching AVM data for: {address}, {city}, {state}")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data and data.get('avm'):
                    return data['avm'][0] if isinstance(data['avm'], list) else data['avm']
                else:
                    logger.warning(f"No AVM data found for: {address}, {city}, {state}")
                    return None
            elif response.status_code == 429:
                logger.warning("Rate limit hit, waiting longer...")
                time.sleep(5)
                return self.get_property_avm(address, city, state, zip_code)
            else:
                logger.error(f"AVM API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching AVM data for {address}: {str(e)}")
            return None
            
    def enrich_property_data(self, property_data: Dict, avm_data: Dict = None) -> Dict:
        """
        Extract and format relevant property information.
        
        Args:
            property_data: Raw property data from API
            avm_data: Raw AVM data from API
            
        Returns:
            Dictionary with enriched property information
        """
        enriched = {}
        
        try:
            # Basic property identification
            identifier = property_data.get('identifier', {})
            enriched['property_id'] = identifier.get('obPropId')
            enriched['fips_code'] = identifier.get('fips')
            enriched['apn'] = identifier.get('apn')
            
            # Property summary information
            summary = property_data.get('summary', {})
            enriched['year_built'] = summary.get('yearbuilt')
            enriched['property_type'] = summary.get('proptype')
            enriched['property_subtype'] = summary.get('propsubtype')
            enriched['property_class'] = summary.get('propclass')
            enriched['land_use'] = summary.get('propLandUse')
            enriched['owner_occupied'] = summary.get('absenteeInd')
            
            # Building characteristics
            building = property_data.get('building', {})
            
            # Size information
            size_info = building.get('size', {})
            enriched['building_sqft'] = size_info.get('bldgsize')
            enriched['living_sqft'] = size_info.get('livingsize')
            enriched['gross_sqft'] = size_info.get('grosssize')
            
            # Room information
            rooms = building.get('rooms', {})
            enriched['bedrooms'] = rooms.get('beds')
            enriched['bathrooms_total'] = rooms.get('bathstotal')
            enriched['bathrooms_full'] = rooms.get('bathsfull')
            enriched['bathrooms_half'] = rooms.get('bathshalf')
            enriched['total_rooms'] = rooms.get('roomsTotal')
            
            # Building details
            building_summary = building.get('summary', {})
            enriched['building_type'] = building_summary.get('bldgType')
            enriched['stories'] = building_summary.get('levels')
            enriched['units_count'] = building_summary.get('unitsCount')
            enriched['year_built_effective'] = building_summary.get('yearbuilteffective')
            
            # Construction details
            construction = building.get('construction', {})
            enriched['condition'] = construction.get('condition')
            enriched['wall_type'] = construction.get('wallType')
            
            # Lot information
            lot = property_data.get('lot', {})
            enriched['lot_size_sqft'] = lot.get('lotsize2')
            enriched['lot_size_acres'] = lot.get('lotsize1')
            enriched['lot_depth'] = lot.get('depth')
            enriched['lot_frontage'] = lot.get('frontage')
            
            # Assessment and tax information
            assessment = property_data.get('assessment', {})
            
            # Assessed values
            assessed = assessment.get('assessed', {})
            enriched['assessed_total_value'] = assessed.get('assdttlvalue')
            enriched['assessed_land_value'] = assessed.get('assdlandvalue')
            enriched['assessed_improvement_value'] = assessed.get('assdimprvalue')
            
            # Tax information
            tax_info = assessment.get('tax', {})
            enriched['tax_amount'] = tax_info.get('taxamt')
            enriched['tax_year'] = tax_info.get('taxyear')
            
            # Market values if available
            market = assessment.get('market', {})
            enriched['market_total_value'] = market.get('mktttlvalue')
            enriched['market_land_value'] = market.get('mktlandvalue')
            enriched['market_improvement_value'] = market.get('mktimprvalue')
            
            # AVM data if available
            if avm_data:
                avm_amount = avm_data.get('amount', {})
                enriched['estimated_value'] = avm_amount.get('value')
                enriched['avm_high'] = avm_amount.get('high')
                enriched['avm_low'] = avm_amount.get('low')
                enriched['avm_score'] = avm_amount.get('scr')
                enriched['value_range'] = avm_amount.get('valueRange')
                
                # AVM calculations
                avm_calc = avm_data.get('calculations', {})
                enriched['price_per_sqft'] = avm_calc.get('perSizeUnit')
                enriched['avm_confidence'] = avm_calc.get('rangePctOfValue')
                
                # AVM metadata
                enriched['avm_date'] = avm_data.get('eventDate')
            
            # Location information
            location = property_data.get('location', {})
            enriched['latitude'] = location.get('latitude')
            enriched['longitude'] = location.get('longitude')
            enriched['elevation'] = location.get('elevation')
            
            # Address information
            address_info = property_data.get('address', {})
            enriched['formatted_address'] = address_info.get('oneLine')
            enriched['address_match_code'] = address_info.get('matchCode')
            
            # Sales history (most recent)
            sale_history = property_data.get('sale', {})
            if isinstance(sale_history, list) and len(sale_history) > 0:
                recent_sale = sale_history[0]
                amount_info = recent_sale.get('amount', {})
                enriched['last_sale_price'] = amount_info.get('saleamt')
                enriched['last_sale_date'] = recent_sale.get('saleTransDate')
                enriched['sale_transaction_type'] = amount_info.get('saletranstype')
            
            # Processing metadata
            enriched['data_source'] = 'ATTOM Data API'
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
            avm_data = None
            
            if property_data:
                # Get AVM estimate
                avm_data = self.get_property_avm(street_address, city, state, zip_code)
                time.sleep(self.rate_limit_delay)  # Rate limiting
                
            # Enrich the data
            enriched = self.enrich_property_data(property_data or {}, avm_data)
            
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
    api_key = os.getenv('ATTOM_API_KEY')
    if not api_key:
        logger.error("ATTOM_API_KEY environment variable not set")
        logger.info("Please add ATTOM_API_KEY to your .env file")
        logger.info("Sign up at https://api.developer.attomdata.com/home to get your free API key")
        return
        
    # Initialize agent
    agent = ResidentialPropertyEnrichmentAgent(api_key)
    
    # Process the address list (test with first 3 records)
    input_file = "data/addresses_for_clay.csv"
    output_file = "data/addresses_enriched_with_property_data.csv"
    
    try:
        enriched_df = agent.process_address_list(
            csv_file_path=input_file,
            output_file_path=output_file,
            max_records=3  # Test with 3 records first
        )
        
        # Display sample results
        print("\n=== Sample Enriched Data ===")
        columns_to_show = [
            'street_address', 'city', 'state', 'year_built', 
            'estimated_value', 'bedrooms', 'bathrooms_total', 'living_sqft'
        ]
        available_columns = [col for col in columns_to_show if col in enriched_df.columns]
        print(enriched_df[available_columns].head())
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 