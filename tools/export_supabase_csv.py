#!/usr/bin/env python3
"""
Export Supabase Data to CSV

Simple tool that uses the existing Supabase service to export data to CSV files.
"""

import sys
import os
import pandas as pd
import argparse
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Load environment and services
from config.env import load_env
load_env()

from src.services.supabase.client import SupabaseService

def export_roofmaxx_deals_csv(output_file: str = None, limit: int = None):
    """Export RoofMaxx deals to CSV using existing Supabase service."""
    
    print("🏢 EXPORTING ROOFMAXX DEALS TO CSV")
    print("=" * 50)
    
    # Initialize Supabase service
    supabase_config = {
        'url': os.getenv('SUPABASE_URL'),
        'access_token': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }
    
    try:
        service = SupabaseService(supabase_config)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return None
    
    # Query the data
    try:
        url = f"{service.url}/rest/v1/roofmaxx_deals"
        params = {'select': '*'}
        
        if limit:
            params['limit'] = limit
            print(f"📊 Limiting to {limit:,} rows")
        
        response = service.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            print("⚠️  No data found in roofmaxx_deals table")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"data/exports/roofmaxx_deals_export_{timestamp}.csv"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Export to CSV
        df.to_csv(output_file, index=False)
        
        print(f"✅ Exported {len(df):,} rows to: {output_file}")
        print(f"📋 Columns: {', '.join(df.columns.tolist())}")
        
        # Show business summary
        if 'deal_type' in df.columns:
            print(f"\n📊 BUSINESS SUMMARY:")
            print(f"   🎯 Total Deals: {len(df):,}")
            print(f"   🏆 Deal Types: {df['deal_type'].nunique()}")
            
            print(f"   📈 Top Sources:")
            for source, count in df['deal_type'].value_counts().head(5).items():
                print(f"      {source}: {count:,} deals")
        
        if 'state' in df.columns:
            print(f"   🗺️  States: {df['state'].nunique()}")
            print(f"   🏙️  Top States:")
            for state, count in df['state'].value_counts().head(5).items():
                print(f"      {state}: {count:,} deals")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return None

def export_table_csv(table_name: str, output_file: str = None, limit: int = None):
    """Export any table to CSV using existing Supabase service."""
    
    print(f"📊 EXPORTING TABLE: {table_name}")
    print("=" * 50)
    
    # Initialize Supabase service
    supabase_config = {
        'url': os.getenv('SUPABASE_URL'),
        'access_token': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }
    
    try:
        service = SupabaseService(supabase_config)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return None
    
    # Query the data
    try:
        url = f"{service.url}/rest/v1/{table_name}"
        params = {'select': '*'}
        
        if limit:
            params['limit'] = limit
            print(f"📊 Limiting to {limit:,} rows")
        
        response = service.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            print(f"⚠️  No data found in {table_name} table")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"data/exports/{table_name}_export_{timestamp}.csv"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Export to CSV
        df.to_csv(output_file, index=False)
        
        print(f"✅ Exported {len(df):,} rows to: {output_file}")
        print(f"📋 Columns ({len(df.columns)}): {', '.join(df.columns.tolist()[:10])}{'...' if len(df.columns) > 10 else ''}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return None

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description='Export Supabase data to CSV using existing service')
    parser.add_argument('--table', '-t', help='Table name to export')
    parser.add_argument('--output', '-o', help='Output CSV file path')
    parser.add_argument('--limit', '-l', type=int, help='Maximum number of rows to export')
    parser.add_argument('--deals', action='store_true', help='Export RoofMaxx deals (default if no table specified)')
    
    args = parser.parse_args()
    
    print("🚀 SUPABASE CSV EXPORT TOOL")
    print("=" * 50)
    print("✅ Using existing Supabase service")
    print()
    
    if args.table:
        result = export_table_csv(args.table, args.output, args.limit)
    else:
        # Default to deals export
        result = export_roofmaxx_deals_csv(args.output, args.limit)
    
    if result:
        print(f"\n🎯 SUCCESS! Data exported to: {result}")
    else:
        print(f"\n❌ Export failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 