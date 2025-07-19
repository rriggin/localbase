#!/usr/bin/env python3
"""
Simple Supabase Connection Test
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env
load_env()

from supabase import create_client, Client

def test_connection():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print(f"🧪 Testing connection to: {url}")
    
    try:
        client: Client = create_client(url, key)
        
        # Test with a simple health check - this should work on any Supabase project
        result = client.auth.get_session()
        print("✅ Supabase connection successful!")
        
        # Now provide the table creation SQL
        print("\n📋 CREATE YOUR DEALS TABLE")
        print("=" * 50)
        print("Copy this SQL and run it in Supabase SQL Editor:")
        print()
        
        sql = """-- Create the deals table
CREATE TABLE IF NOT EXISTS roofmaxx_deals (
    id SERIAL PRIMARY KEY,
    deal_id BIGINT UNIQUE NOT NULL,
    dealer_id INTEGER,
    deal_type TEXT,
    deal_lifecycle TEXT,
    deal_stage TEXT,
    customer_first_name TEXT,
    customer_last_name TEXT,
    customer_email TEXT,
    customer_phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    invoice_total TEXT,
    is_roof_maxx_job BOOLEAN,
    has_warranty BOOLEAN,
    hs_contact_id BIGINT,
    hubspot_company_id BIGINT,
    create_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    raw_data JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_dealer_id ON roofmaxx_deals(dealer_id);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_deal_type ON roofmaxx_deals(deal_type);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_lifecycle ON roofmaxx_deals(deal_lifecycle);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_city ON roofmaxx_deals(city);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_state ON roofmaxx_deals(state);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_create_date ON roofmaxx_deals(create_date);"""
        
        print(sql)
        
        print(f"\n🎯 Steps:")
        print("1. Go to: https://supabase.com/dashboard")
        print("2. Select your project: roofmaxx_connect_sync")
        print("3. Go to: SQL Editor")
        print("4. Paste the SQL above")
        print("5. Click 'Run'")
        print()
        print("Then run: python3 src/services/supabase/simple_deals_sync.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection() 