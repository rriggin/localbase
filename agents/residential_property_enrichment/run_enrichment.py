"""
Runner script for Residential Property Enrichment Agent

This standalone agent enriches address data with comprehensive residential property information.
"""

import os
import sys
from dotenv import load_dotenv
import argparse

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from property_enrichment_agent import ResidentialPropertyEnrichmentAgent
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file."""
    # Load from main project directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    load_dotenv(env_path)
    
    api_key = os.getenv('ATTOM_API_KEY')
    if not api_key:
        logger.error("ATTOM_API_KEY not found in environment variables")
        logger.info("Please add ATTOM_API_KEY to your .env file")
        logger.info("Sign up at https://api.developer.attomdata.com/home to get your free API key")
        return None
    
    return api_key

def run_enrichment(input_file: str, output_file: str = None, max_records: int = None, test_mode: bool = False):
    """
    Run the residential property enrichment process.
    
    Args:
        input_file: Path to input CSV file with address data
        output_file: Path for output CSV file (optional)
        max_records: Maximum number of records to process (None for all)
        test_mode: If True, runs with 3 records first
    """
    # Load API key
    api_key = load_environment()
    if not api_key:
        return
    
    # Initialize agent
    agent = ResidentialPropertyEnrichmentAgent(api_key)
    
    # Set up output file
    if test_mode:
        if not output_file:
            output_file = "enriched_addresses_test.csv"
        max_records = 3
        logger.info("Running in TEST MODE with 3 records")
    else:
        if not output_file:
            # Generate output filename based on input
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}_enriched.csv"
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
        print("🏠 RESIDENTIAL PROPERTY ENRICHMENT SUMMARY")
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
        
        return enriched_df
        
    except Exception as e:
        logger.error(f"Error during enrichment: {str(e)}")
        return None

def main():
    """Main function with command line options."""
    parser = argparse.ArgumentParser(description='Residential Property Enrichment Agent')
    parser.add_argument('input_file', help='Input CSV file with address data')
    parser.add_argument('--output', '-o', help='Output CSV file path')
    parser.add_argument('--test', action='store_true', help='Run in test mode (3 records only)')
    parser.add_argument('--max-records', type=int, help='Maximum number of records to process')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' not found")
        return
    
    # Run enrichment
    result = run_enrichment(
        input_file=args.input_file,
        output_file=args.output,
        max_records=args.max_records,
        test_mode=args.test
    )
    
    if result is not None:
        print("✅ Enrichment completed successfully!")
    else:
        print("❌ Enrichment failed")

if __name__ == "__main__":
    main() 