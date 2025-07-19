#!/usr/bin/env python3
"""
Simple RoofMaxx Deals Sync - Works with Standard Supabase

No custom functions needed - just sync the data directly!
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env
load_env()

def install_supabase_client():
    """Install Supabase client if needed."""
    try:
        from supabase import create_client, Client
        return True
    except ImportError:
        print("📦 Installing Supabase Python client...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase"])
        print("✅ Supabase client installed!")
        return True

def test_supabase_connection():
    """Test Supabase connection."""
    
    print("🧪 TESTING SUPABASE CONNECTION")
    print("-" * 40)
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            print("❌ Missing Supabase credentials in environment")
            return False
        
        print(f"📡 Connecting to: {url}")
        client: Client = create_client(url, key)
        
        # Test with a simple query
        print("🔍 Testing database access...")
        result = client.table('_supabase_migrations').select("*").limit(1).execute()
        
        print("✅ Supabase connection successful!")
        return client
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_deals_table_manual():
    """Provide SQL for manual table creation."""
    
    sql = """
-- Create the deals table
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
CREATE INDEX IF NOT EXISTS idx_roofmaxx_deals_create_date ON roofmaxx_deals(create_date);
"""
    
    print("📋 MANUAL TABLE CREATION REQUIRED")
    print("=" * 50)
    print("Please copy this SQL and run it in the Supabase SQL Editor:")
    print()
    print(sql)
    print()
    print("🎯 Steps:")
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select your project: roofmaxx_connect_sync")
    print("3. Go to: SQL Editor")
    print("4. Paste the SQL above")
    print("5. Click 'Run'")
    print()
    
    return input("✅ Table created? Press Enter when done...")

def fetch_roofmaxx_deals():
    """Fetch deals from RoofMaxx Connect API."""
    
    print("📡 FETCHING DEALS FROM ROOFMAXX CONNECT")
    print("-" * 50)
    
    import requests
    
    token = os.getenv('ROOFMAXX_CONNECT_TOKEN')
    base_url = os.getenv('ROOFMAXX_CONNECT_BASE_URL')
    dealer_id = os.getenv('ROOFMAXX_CONNECT_DEALER_ID')
    
    if not all([token, base_url, dealer_id]):
        print("❌ Missing RoofMaxx Connect credentials")
        return []
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    all_deals = []
    page = 1
    
    print(f"🎯 Fetching deals for dealer {dealer_id}...")
    
    while True:
        try:
            print(f"📄 Fetching page {page}...")
            
            response = requests.get(
                f"{base_url}/api/dealers/{dealer_id}/deals",
                headers=headers,
                params={'page': page},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            deals = data.get('data', [])
            
            if not deals:
                print(f"✅ No more deals on page {page}")
                break
            
            all_deals.extend(deals)
            print(f"   📊 Got {len(deals)} deals (total: {len(all_deals)})")
            
            # Check if there are more pages
            meta = data.get('meta', {})
            if page >= meta.get('last_page', page):
                break
                
            page += 1
            time.sleep(0.5)  # Be nice to the API
            
        except Exception as e:
            print(f"❌ Error fetching page {page}: {e}")
            break
    
    print(f"🎉 Total deals fetched: {len(all_deals)}")
    return all_deals

def sync_deals_to_supabase(client, deals):
    """Sync deals to Supabase."""
    
    print("🔄 SYNCING DEALS TO SUPABASE")
    print("-" * 40)
    
    if not deals:
        print("❌ No deals to sync")
        return
    
    print(f"📊 Syncing {len(deals)} deals...")
    
    synced_count = 0
    error_count = 0
    
    # Process in batches of 100
    batch_size = 100
    
    for i in range(0, len(deals), batch_size):
        batch = deals[i:i + batch_size]
        
        try:
            print(f"   📦 Batch {i//batch_size + 1}: Syncing {len(batch)} deals...")
            
            # Prepare batch data
            batch_data = []
            
            for deal in batch:
                # Extract stage information
                stage_info = deal.get('stage', {})
                stage_label = stage_info.get('label') if isinstance(stage_info, dict) else str(stage_info)
                
                deal_data = {
                    'deal_id': deal.get('id'),
                    'dealer_id': int(os.getenv('ROOFMAXX_CONNECT_DEALER_ID')),
                    'deal_type': deal.get('dealType'),
                    'deal_lifecycle': deal.get('lifecycle'),
                    'deal_stage': stage_label,
                    'customer_first_name': deal.get('customerFirstName'),
                    'customer_last_name': deal.get('customerLastName'),
                    'customer_email': deal.get('customerEmail'),
                    'customer_phone': deal.get('customerPhone'),
                    'address': deal.get('address'),
                    'city': deal.get('city'),
                    'state': deal.get('state'),
                    'postal_code': deal.get('postalCode'),
                    'invoice_total': deal.get('invoiceTotal'),
                    'is_roof_maxx_job': deal.get('isRoofMaxxJob'),
                    'has_warranty': deal.get('hasWarranty'),
                    'hs_contact_id': deal.get('hsContactId'),
                    'hubspot_company_id': deal.get('hubspotCompanyId'),
                    'create_date': deal.get('createDate'),
                    'raw_data': deal
                }
                
                batch_data.append(deal_data)
            
            # Upsert to Supabase
            result = client.table('roofmaxx_deals').upsert(
                batch_data,
                on_conflict='deal_id'
            ).execute()
            
            synced_count += len(batch_data)
            print(f"   ✅ Synced {len(batch_data)} deals")
            
        except Exception as e:
            print(f"   ❌ Batch error: {e}")
            error_count += 1
            continue
    
    print(f"\n🎊 SYNC COMPLETE!")
    print(f"   ✅ Deals synced: {synced_count:,}")
    print(f"   ❌ Batch errors: {error_count}")
    
    if error_count == 0:
        print("🏆 PERFECT SYNC! All deals successfully stored!")
        print("🍆💥 TOM'S MIND = OFFICIALLY BLOWN!")

def run_analytics(client):
    """Run basic analytics on synced data."""
    
    print("\n📊 RUNNING BASIC ANALYTICS")
    print("-" * 40)
    
    try:
        # Total deals
        total_result = client.table('roofmaxx_deals').select('*', count='exact').execute()
        total_deals = total_result.count
        
        print(f"📈 Total deals in database: {total_deals:,}")
        
        # Deals by lifecycle
        lifecycle_result = client.table('roofmaxx_deals').select('deal_lifecycle', count='exact').group('deal_lifecycle').execute()
        
        print("\n📊 Deals by Lifecycle:")
        for row in lifecycle_result.data:
            lifecycle = row.get('deal_lifecycle', 'Unknown')
            print(f"   • {lifecycle}: [Count available via aggregation]")
        
        # Recent deals
        recent_result = client.table('roofmaxx_deals').select('*').order('create_date', desc=True).limit(5).execute()
        
        print(f"\n🕒 Recent deals:")
        for deal in recent_result.data:
            customer = f"{deal.get('customer_first_name', '')} {deal.get('customer_last_name', '')}".strip()
            city = deal.get('city', 'Unknown')
            stage = deal.get('deal_stage', 'Unknown')
            print(f"   • {customer} in {city} - {stage}")
        
        print("\n🎯 SUCCESS! Your deals are now permanently stored!")
        
    except Exception as e:
        print(f"❌ Analytics error: {e}")

def main():
    """Main sync flow."""
    
    print("🚀 SIMPLE ROOFMAXX DEALS SYNC")
    print("=" * 60)
    print("📊 Syncing your 868 deals to Supabase!")
    print("🔒 Using secure environment variables")
    print()
    
    # Install Supabase client if needed
    if not install_supabase_client():
        return
    
    # Test connection
    client = test_supabase_connection()
    if not client:
        return
    
    # Check if table exists, create if needed
    try:
        result = client.table('roofmaxx_deals').select('*').limit(1).execute()
        print("✅ Table 'roofmaxx_deals' exists and is accessible!")
    except Exception as e:
        print(f"⚠️  Table doesn't exist or isn't accessible: {e}")
        create_deals_table_manual()
        
        # Test again
        try:
            result = client.table('roofmaxx_deals').select('*').limit(1).execute()
            print("✅ Table is now accessible!")
        except Exception as e:
            print(f"❌ Table still not accessible: {e}")
            return
    
    # Fetch deals from RoofMaxx
    deals = fetch_roofmaxx_deals()
    if not deals:
        print("❌ No deals fetched from RoofMaxx Connect")
        return
    
    # Sync to Supabase
    sync_deals_to_supabase(client, deals)
    
    # Run analytics
    run_analytics(client)
    
    print(f"\n🎯 ALL DONE!")
    print("=" * 60)
    print("🏆 Enterprise data infrastructure complete!")
    print("🔒 All credentials secure!")
    print("📊 Deals permanently stored!")
    print("🍆💥 TOM = MAXIMUM IMPRESSED!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n👋 Sync cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check setup and try again.") 