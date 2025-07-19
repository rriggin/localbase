#!/usr/bin/env python3
"""
Expand Table Schema & Re-sync Full Data

Adds all the missing columns and re-syncs with complete deal information.
"""

print("🔧 EXPANDING TABLE SCHEMA FOR FULL DATA")
print("=" * 60)
print("We already have 868 deal IDs stored!")
print("Now let's add columns for complete business analytics! 📊")
print()

print("📋 STEP 1: Add Missing Columns to Supabase Table")
print("-" * 50)
print("Go to Supabase SQL Editor and run this SQL:")
print()

sql_commands = """
-- Add all the business intelligence columns
ALTER TABLE roofmaxx_deals 
ADD COLUMN IF NOT EXISTS dealer_id INTEGER,
ADD COLUMN IF NOT EXISTS deal_type TEXT,
ADD COLUMN IF NOT EXISTS deal_lifecycle TEXT,
ADD COLUMN IF NOT EXISTS deal_stage TEXT,
ADD COLUMN IF NOT EXISTS customer_first_name TEXT,
ADD COLUMN IF NOT EXISTS customer_last_name TEXT,
ADD COLUMN IF NOT EXISTS customer_email TEXT,
ADD COLUMN IF NOT EXISTS customer_phone TEXT,
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS city TEXT,
ADD COLUMN IF NOT EXISTS state TEXT,
ADD COLUMN IF NOT EXISTS postal_code TEXT,
ADD COLUMN IF NOT EXISTS invoice_total TEXT,
ADD COLUMN IF NOT EXISTS is_roof_maxx_job BOOLEAN,
ADD COLUMN IF NOT EXISTS has_warranty BOOLEAN,
ADD COLUMN IF NOT EXISTS hs_contact_id BIGINT,
ADD COLUMN IF NOT EXISTS hubspot_company_id BIGINT,
ADD COLUMN IF NOT EXISTS create_date TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS synced_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS raw_data JSONB;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_dealer_id ON roofmaxx_deals(dealer_id);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_deal_type ON roofmaxx_deals(deal_type);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_lifecycle ON roofmaxx_deals(deal_lifecycle);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_city ON roofmaxx_deals(city);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_state ON roofmaxx_deals(state);
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_create_date ON roofmaxx_deals(create_date);
"""

print(sql_commands)

print("=" * 60)
print("🎯 INSTRUCTIONS:")
print("1. Go to: https://supabase.com/dashboard")
print("2. Select: roofmaxx_connect_sync")  
print("3. Click: SQL Editor")
print("4. Paste the SQL above")
print("5. Click: RUN")
print("6. Come back and run the full sync!")
print()
print("⚡️ Then run: python3 src/services/supabase/working_sync.py")
print("💥 Result: COMPLETE business intelligence database!")

if __name__ == "__main__":
    print("\n🚀 Ready to expand your data empire? Copy that SQL! 📊") 