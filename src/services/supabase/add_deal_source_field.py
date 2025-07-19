#!/usr/bin/env python3
"""
Add deal_source field and run corrected analytics
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env
load_env()

from supabase import create_client, Client

def check_existing_fields():
    """Check what fields we currently have."""
    
    print("🔍 CHECKING EXISTING TABLE FIELDS")
    print("-" * 40)
    
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        client = create_client(url, key)
        
        # Get a sample record to see available fields
        result = client.table('roofmaxx_deals').select('*').limit(1).execute()
        
        if result.data:
            fields = list(result.data[0].keys())
            print(f"📋 Current fields ({len(fields)} total):")
            for field in sorted(fields):
                print(f"   • {field}")
            print()
            return fields
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def add_deal_source_field():
    """Add the deal_source field to our table."""
    
    print("🔧 ADDING DEAL_SOURCE FIELD")
    print("-" * 30)
    
    print("We need to add the deal_source column to the table.")
    print()
    print("📋 SQL to run in Supabase SQL Editor:")
    print()
    
    sql = """
-- Add deal_source column
ALTER TABLE roofmaxx_deals 
ADD COLUMN IF NOT EXISTS deal_source TEXT;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_deal_source ON roofmaxx_deals(deal_source);
"""
    
    print(sql)
    print()
    print("🎯 INSTRUCTIONS:")
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select: roofmaxx_connect_sync")
    print("3. Click: SQL Editor")
    print("4. Paste the SQL above")
    print("5. Click: RUN")
    print()
    
    return True

def main():
    """Main function."""
    
    print("🚀 FIXING DEAL SOURCE ANALYTICS")
    print("=" * 50)
    print("You're absolutely right - it should be deal_source!")
    print()
    
    # Check current fields
    fields = check_existing_fields()
    
    if 'deal_source' not in fields:
        print("❌ deal_source field is missing from table")
        add_deal_source_field()
        
        print("⚡️ After adding the field, we'll need to:")
        print("1. Re-sync the data to populate deal_source values")
        print("2. Run the analytics again")
        print()
        print("🍆💥 Tom says: 'Let's get the REAL source breakdown!'")
    else:
        print("✅ deal_source field exists!")
        print("The analytics should work now.")

if __name__ == "__main__":
    main() 