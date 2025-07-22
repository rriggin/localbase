#!/usr/bin/env python3
"""
Supabase Search Tool
Search for specific data across Supabase tables.
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Load environment variables
from config.env import load_env
load_env()

from supabase import create_client, Client

def search_supabase(search_term: str = "Dennis King"):
    """
    Search for a term across Supabase tables.
    
    Args:
        search_term: The term to search for
    """
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("❌ Missing Supabase credentials. Please check your environment variables.")
        return
    
    print(f"🔍 Searching for: '{search_term}'")
    print(f"📡 Connecting to: {url}")
    print("=" * 60)
    
    try:
        client: Client = create_client(url, key)
        
        # Search for full term
        print(f"\n🎯 Searching for full term: '{search_term}'")
        search_roofmaxx_deals(client, search_term)
        
        # Search for partial terms
        terms = search_term.split()
        if len(terms) > 1:
            print(f"\n🔍 Searching for partial terms: {terms}")
            for term in terms:
                print(f"\n   Searching for: '{term}'")
                search_roofmaxx_deals(client, term)
        
        # Search in raw_data JSONB fields
        search_raw_data(client, search_term)
        
        # List all available tables
        list_available_tables(client)
        
    except Exception as e:
        print(f"❌ Search failed: {e}")

def search_roofmaxx_deals(client: Client, search_term: str):
    """Search in roofmaxx_deals table."""
    try:
        # Search in customer name fields with partial matching
        result = client.table('roofmaxx_deals').select('*').or_(
            f'customer_first_name.ilike.%{search_term}%,customer_last_name.ilike.%{search_term}%'
        ).execute()
        
        if result.data:
            print(f"✅ Found {len(result.data)} records in roofmaxx_deals:")
            for record in result.data:
                print(f"  🏠 Deal ID: {record.get('deal_id', 'N/A')}")
                print(f"     Customer: {record.get('customer_first_name', '')} {record.get('customer_last_name', '')}")
                print(f"     Address: {record.get('address', 'N/A')}")
                print(f"     City: {record.get('city', 'N/A')}, {record.get('state', 'N/A')}")
                print(f"     Deal Type: {record.get('deal_type', 'N/A')}")
                print(f"     Create Date: {record.get('create_date', 'N/A')}")
                print(f"     Email: {record.get('customer_email', 'N/A')}")
                print(f"     Phone: {record.get('customer_phone', 'N/A')}")
                print()
        else:
            print("   No records found in roofmaxx_deals")
            
    except Exception as e:
        print(f"   ❌ Error searching roofmaxx_deals: {e}")

def search_raw_data(client: Client, search_term: str):
    """Search in raw_data JSONB fields."""
    print(f"\n🔍 Searching in raw_data JSONB fields for '{search_term}'...")
    
    try:
        # Search in roofmaxx_deals raw_data
        result = client.table('roofmaxx_deals').select('*').execute()
        
        found_in_raw = []
        for record in result.data:
            raw_data = record.get('raw_data', {})
            if isinstance(raw_data, dict):
                # Convert to string and search
                raw_str = str(raw_data).lower()
                if search_term.lower() in raw_str:
                    found_in_raw.append(record)
        
        if found_in_raw:
            print(f"✅ Found {len(found_in_raw)} records with '{search_term}' in raw_data:")
            for record in found_in_raw:
                print(f"  🏠 Deal ID: {record.get('deal_id', 'N/A')}")
                print(f"     Customer: {record.get('customer_first_name', '')} {record.get('customer_last_name', '')}")
                print(f"     Raw data contains the search term")
                print()
                
            # Show detailed information for the first match
            if found_in_raw:
                show_detailed_record(found_in_raw[0])
        else:
            print("   No records found in raw_data")
            
    except Exception as e:
        print(f"   ❌ Error searching raw_data: {e}")

def show_detailed_record(record: Dict[str, Any]):
    """Show detailed information about a record."""
    print(f"\n📋 DETAILED RECORD INFORMATION")
    print("=" * 50)
    print(f"🏠 Deal ID: {record.get('deal_id', 'N/A')}")
    print(f"📅 Created: {record.get('created_at', 'N/A')}")
    print(f"🔄 Updated: {record.get('updated_at', 'N/A')}")
    print(f"🔄 Synced: {record.get('synced_at', 'N/A')}")
    print()
    
    print("👤 CUSTOMER INFORMATION:")
    print(f"   First Name: {record.get('customer_first_name', 'N/A')}")
    print(f"   Last Name: {record.get('customer_last_name', 'N/A')}")
    print(f"   Email: {record.get('customer_email', 'N/A')}")
    print(f"   Phone: {record.get('customer_phone', 'N/A')}")
    print()
    
    print("📍 ADDRESS INFORMATION:")
    print(f"   Address: {record.get('address', 'N/A')}")
    print(f"   City: {record.get('city', 'N/A')}")
    print(f"   State: {record.get('state', 'N/A')}")
    print(f"   Postal Code: {record.get('postal_code', 'N/A')}")
    print()
    
    print("💼 DEAL INFORMATION:")
    print(f"   Dealer ID: {record.get('dealer_id', 'N/A')}")
    print(f"   Deal Type: {record.get('deal_type', 'N/A')}")
    print(f"   Deal Lifecycle: {record.get('deal_lifecycle', 'N/A')}")
    print(f"   Deal Stage: {record.get('deal_stage', 'N/A')}")
    print(f"   Invoice Total: {record.get('invoice_total', 'N/A')}")
    print(f"   Is Roof Maxx Job: {record.get('is_roof_maxx_job', 'N/A')}")
    print(f"   Has Warranty: {record.get('has_warranty', 'N/A')}")
    print(f"   Create Date: {record.get('create_date', 'N/A')}")
    print()
    
    print("🔗 INTEGRATION IDs:")
    print(f"   HubSpot Contact ID: {record.get('hs_contact_id', 'N/A')}")
    print(f"   HubSpot Company ID: {record.get('hubspot_company_id', 'N/A')}")
    print()
    
    # Show raw_data if it exists
    raw_data = record.get('raw_data')
    if raw_data:
        print("📄 RAW DATA (JSON):")
        print("=" * 30)
        try:
            # Pretty print the JSON
            formatted_json = json.dumps(raw_data, indent=2, default=str)
            print(formatted_json)
        except Exception as e:
            print(f"Error formatting JSON: {e}")
            print(str(raw_data))
        print()

def list_available_tables(client: Client):
    """List all available tables in the database."""
    print(f"\n📋 Available tables in database:")
    print("=" * 40)
    
    # Common table names to check
    potential_tables = [
        'roofmaxx_deals', 'call_logs', 'deals', 'customers', 'contacts', 
        'leads', 'prospects', 'addresses', 'properties', 'calls', 
        'activities', 'users', 'profiles'
    ]
    
    existing_tables = []
    for table_name in potential_tables:
        try:
            # Try to get a sample record to see if table exists
            result = client.table(table_name).select('*').limit(1).execute()
            existing_tables.append(table_name)
            print(f"✅ {table_name}")
        except Exception as e:
            # Table doesn't exist
            pass
    
    if not existing_tables:
        print("❌ No tables found")
    else:
        print(f"\n📊 Total tables found: {len(existing_tables)}")

def search_all_text_fields(client: Client, search_term: str):
    """Search in all text fields across all tables."""
    print(f"\n🔍 Comprehensive search for '{search_term}' across all tables...")
    
    # Get all tables first
    try:
        # This is a simplified approach - in production you'd want to query the schema
        tables_to_search = ['roofmaxx_deals']  # Add more tables as needed
        
        for table_name in tables_to_search:
            print(f"\n📋 Searching in {table_name}...")
            try:
                # Get all records and search in Python
                result = client.table(table_name).select('*').execute()
                
                found_records = []
                for record in result.data:
                    # Search in all string fields
                    for key, value in record.items():
                        if isinstance(value, str) and search_term.lower() in value.lower():
                            found_records.append((record, key, value))
                
                if found_records:
                    print(f"✅ Found {len(found_records)} matches:")
                    for record, field, value in found_records[:5]:  # Show first 5
                        print(f"  📝 Field '{field}': {value}")
                        print(f"     Record ID: {record.get('id', 'N/A')}")
                        print()
                else:
                    print("   No matches found")
                    
            except Exception as e:
                print(f"   ❌ Error searching {table_name}: {e}")
                
    except Exception as e:
        print(f"❌ Error in comprehensive search: {e}")

if __name__ == "__main__":
    search_term = "Dennis King"
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    
    search_supabase(search_term) 