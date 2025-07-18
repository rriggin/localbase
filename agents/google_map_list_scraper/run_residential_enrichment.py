"""
Runner script for Residential Property Enrichment Agent

This script runs the residential property enrichment agent on the existing address data
using ATTOM Data API for comprehensive residential property information.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from residential_property_enrichment import ResidentialPropertyEnrichmentAgent
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file."""
    # Try to load from main project directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    load_dotenv(env_path)
    
    api_key = os.getenv('ATTOM_API_KEY')
    if not api_key:
        logger.error("ATTOM_API_KEY not found in environment variables")
        logger.info("Please add ATTOM_API_KEY to your .env file")
        logger.info("Sign up at https://api.developer.attomdata.com/home to get your free API key")
        return None
    
    return api_key

def run_enrichment(max_records=None, test_mode=True):
    """
    Run the residential property enrichment process.
    
    Args:
        max_records: Maximum number of records to process (None for all)
        test_mode: If True, runs with 3 records first
    """
    # Load API key
    api_key = load_environment()
    if not api_key:
        return
    
    # Initialize agent
    agent = ResidentialPropertyEnrichmentAgent(api_key)
    
    # Set file paths
    input_file = "data/addresses_for_clay.csv"
    
    if test_mode:
        output_file = "data/addresses_enriched_residential_test.csv"
        max_records = 3
        logger.info("Running in TEST MODE with 3 records")
    else:
        output_file = "data/addresses_enriched_residential_property_data.csv"
        logger.info(f"Running FULL ENRICHMENT{f' (max {max_records} records)' if max_records else ''}")
    
    try:
        # Process the addresses
        enriched_df = agent.process_address_list(
            csv_file_path=input_file,
            output_file_path=output_file,
            max_records=max_records
        )
        
        # Display summary
        print("\n" + "="*60)
        print("RESIDENTIAL PROPERTY ENRICHMENT SUMMARY")
        print("="*60)
        print(f"Total records processed: {len(enriched_df)}")
        print(f"Output file: {output_file}")
        
        # Show sample of enriched data
        if len(enriched_df) > 0:
            print("\n--- Sample Enriched Data ---")
            columns_to_show = [
                'street_address', 'city', 'year_built', 
                'estimated_value', 'bedrooms', 'bathrooms_total', 'living_sqft',
                'assessed_total_value', 'property_type'
            ]
            available_columns = [col for col in columns_to_show if col in enriched_df.columns]
            
            if available_columns:
                sample_df = enriched_df[available_columns].head(3)
                print(sample_df.to_string(index=False))
            else:
                print("No property data found for sample records")
        
        # Show statistics
        enriched_records = enriched_df[enriched_df['year_built'].notna()]
        if len(enriched_records) > 0:
            print(f"\nSuccessfully enriched: {len(enriched_records)}/{len(enriched_df)} records")
            
            # Show property statistics
            if 'estimated_value' in enriched_df.columns:
                values = enriched_df['estimated_value'].dropna()
                if len(values) > 0:
                    print(f"\n📊 PROPERTY VALUES:")
                    print(f"   Properties with estimated values: {len(values)}")
                    print(f"   Average estimated value: ${values.mean():,.0f}")
                    print(f"   Value range: ${values.min():,.0f} - ${values.max():,.0f}")
            
            if 'year_built' in enriched_df.columns:
                years = enriched_df['year_built'].dropna()
                if len(years) > 0:
                    print(f"\n🏠 PROPERTY AGE:")
                    print(f"   Properties with year built: {len(years)}")
                    print(f"   Average year built: {years.mean():.0f}")
                    print(f"   Year range: {years.min():.0f} - {years.max():.0f}")
                    
            if 'living_sqft' in enriched_df.columns:
                sqft = enriched_df['living_sqft'].dropna()
                if len(sqft) > 0:
                    print(f"\n📏 PROPERTY SIZE:")
                    print(f"   Properties with square footage: {len(sqft)}")
                    print(f"   Average living sqft: {sqft.mean():,.0f}")
                    print(f"   Size range: {sqft.min():,.0f} - {sqft.max():,.0f} sqft")
                    
            if 'bedrooms' in enriched_df.columns:
                beds = enriched_df['bedrooms'].dropna()
                if len(beds) > 0:
                    print(f"\n🛏️ BEDROOMS:")
                    print(f"   Properties with bedroom data: {len(beds)}")
                    print(f"   Average bedrooms: {beds.mean():.1f}")
                    
            if 'assessed_total_value' in enriched_df.columns:
                assessed = enriched_df['assessed_total_value'].dropna()
                if len(assessed) > 0:
                    print(f"\n🏛️ TAX ASSESSMENTS:")
                    print(f"   Properties with assessed values: {len(assessed)}")
                    print(f"   Average assessed value: ${assessed.mean():,.0f}")
                    
        else:
            print(f"\nNo property data found for any of the {len(enriched_df)} addresses")
            print("This could be due to:")
            print("- API rate limits")
            print("- Addresses not found in ATTOM database")
            print("- API key issues")
            print("- Free tier limitations")
        
        print("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Error during enrichment: {str(e)}")

def main():
    """Main function with command line options."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Residential Property Enrichment Agent')
    parser.add_argument('--test', action='store_true', default=True, help='Run in test mode (3 records only)')
    parser.add_argument('--max-records', type=int, help='Maximum number of records to process')
    parser.add_argument('--full', action='store_true', help='Run full enrichment on all records')
    
    args = parser.parse_args()
    
    if args.full:
        run_enrichment(max_records=args.max_records, test_mode=False)
    else:
        run_enrichment(max_records=args.max_records, test_mode=True)

if __name__ == "__main__":
    main() 