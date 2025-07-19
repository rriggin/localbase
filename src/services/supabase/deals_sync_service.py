#!/usr/bin/env python3
"""
RoofMaxx Deals Sync Service

Syncs all RoofMaxx Connect deals to Supabase for permanent storage and analytics.
This is where business intelligence becomes permanent! 💎
"""

import sys
import os
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import time

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.roofmaxxconnect.client import RoofmaxxConnectService
from src.services.supabase.client import SupabaseService
from .deals_models import RoofmaxxDealRecord, DealsSyncStatus

class DealsSyncService:
    """Service to sync RoofMaxx deals to Supabase for permanent analytics."""
    
    def __init__(self, roofmaxx_config: Dict[str, Any], supabase_config: Dict[str, Any]):
        """Initialize with both service configs."""
        self.roofmaxx_service = RoofmaxxConnectService(roofmaxx_config)
        self.supabase_service = SupabaseService(supabase_config)
        self.dealer_id = 6637  # Your dealer ID
        self.table_name = 'roofmaxx_deals'
        
    def create_deals_table(self) -> bool:
        """Create the deals table in Supabase if it doesn't exist."""
        
        print("🏗️  Creating/verifying Supabase deals table...")
        
        # SQL to create the table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS roofmaxx_deals (
            id BIGSERIAL PRIMARY KEY,
            deal_id BIGINT UNIQUE,
            rmc_id BIGINT,
            dispatch_id BIGINT,
            dealer_id INTEGER,
            deal_name TEXT,
            deal_type TEXT,
            deal_lifecycle TEXT,
            stage_label TEXT,
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
        
        -- Enable Row Level Security (optional)
        ALTER TABLE roofmaxx_deals ENABLE ROW LEVEL SECURITY;
        """
        
        try:
            # Execute the SQL
            response = self.supabase_service.session.post(
                f"{self.supabase_service.url}/rest/v1/rpc/exec_sql",
                json={"sql": create_table_sql}
            )
            
            if response.status_code in [200, 201]:
                print("✅ Deals table created/verified successfully!")
                return True
            else:
                print(f"❌ Failed to create table: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            return False
    
    def fetch_all_roofmaxx_deals(self) -> List[Dict[str, Any]]:
        """Fetch all deals from RoofMaxx Connect API."""
        
        print("📥 Fetching all deals from RoofMaxx Connect...")
        
        if not self.roofmaxx_service.authenticate():
            raise Exception("Failed to authenticate with RoofMaxx Connect")
        
        all_deals = []
        page = 1
        
        while page <= 87:  # We know there are 87 pages
            try:
                print(f"   📄 Fetching page {page}/87...")
                response = self.roofmaxx_service.get_dealer_deals(self.dealer_id, page=page)
                
                if not response or 'data' not in response:
                    break
                
                page_deals = response['data']
                if not page_deals:
                    break
                
                all_deals.extend(page_deals)
                
                if page % 20 == 0:
                    print(f"   🚀 Progress: {page}/87 pages ({len(all_deals)} deals)")
                
                page += 1
                
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        
        print(f"✅ Retrieved {len(all_deals)} deals from RoofMaxx Connect")
        return all_deals
    
    def sync_deals_to_supabase(self, deals: List[Dict[str, Any]]) -> DealsSyncStatus:
        """Sync all deals to Supabase."""
        
        start_time = time.time()
        sync_status = DealsSyncStatus()
        sync_status.total_deals_api = len(deals)
        
        print(f"📊 Syncing {len(deals)} deals to Supabase...")
        
        # Convert to our data model
        deal_records = []
        for deal_data in deals:
            try:
                deal_record = RoofmaxxDealRecord.from_roofmaxx_api(deal_data, self.dealer_id)
                deal_records.append(deal_record)
            except Exception as e:
                print(f"⚠️  Error converting deal {deal_data.get('id', 'unknown')}: {e}")
                sync_status.sync_errors += 1
        
        print(f"✅ Converted {len(deal_records)} deals to database format")
        
        # Batch insert to Supabase
        batch_size = 50  # Supabase handles batches well
        total_batches = (len(deal_records) + batch_size - 1) // batch_size
        
        for i in range(0, len(deal_records), batch_size):
            batch = deal_records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"   📦 Syncing batch {batch_num}/{total_batches} ({len(batch)} deals)...")
            
            try:
                # Convert to Supabase format
                batch_data = [deal.to_supabase_dict() for deal in batch]
                
                # Insert with upsert (on conflict update)
                response = self.supabase_service.session.post(
                    f"{self.supabase_service.url}/rest/v1/{self.table_name}",
                    json=batch_data,
                    headers={
                        'Prefer': 'resolution=merge-duplicates'  # Upsert on conflict
                    }
                )
                
                if response.status_code in [200, 201]:
                    sync_status.new_deals_synced += len(batch)
                    if batch_num % 5 == 0:  # Progress every 5 batches
                        print(f"   ✅ Synced {sync_status.new_deals_synced}/{len(deal_records)} deals...")
                else:
                    print(f"   ❌ Batch {batch_num} failed: {response.status_code} - {response.text[:100]}")
                    sync_status.sync_errors += len(batch)
                    
            except Exception as e:
                print(f"   ❌ Error syncing batch {batch_num}: {e}")
                sync_status.sync_errors += len(batch)
        
        # Update sync status
        sync_status.last_sync_time = datetime.now()
        sync_status.sync_duration_seconds = time.time() - start_time
        
        # Get final count from database
        try:
            count_response = self.supabase_service.session.get(
                f"{self.supabase_service.url}/rest/v1/{self.table_name}",
                params={'select': 'count', 'dealer_id': f'eq.{self.dealer_id}'},
                headers={'Prefer': 'count=exact'}
            )
            if count_response.status_code == 200:
                # Extract count from headers
                count_header = count_response.headers.get('Content-Range', '0-0/0')
                sync_status.total_deals_db = int(count_header.split('/')[-1])
        except:
            pass
        
        return sync_status
    
    def run_full_sync(self) -> DealsSyncStatus:
        """Run complete sync process: create table, fetch deals, sync to Supabase."""
        
        print("🚀 STARTING FULL ROOFMAXX DEALS SYNC")
        print("=" * 60)
        print(f"Dealer ID: {self.dealer_id}")
        print(f"Target Table: {self.table_name}")
        print()
        
        # Step 1: Create/verify table
        if not self.create_deals_table():
            raise Exception("Failed to create/verify Supabase table")
        
        # Step 2: Fetch all deals from API
        deals = self.fetch_all_roofmaxx_deals()
        
        # Step 3: Sync to Supabase
        sync_status = self.sync_deals_to_supabase(deals)
        
        # Results
        print("\n🎉 SYNC COMPLETE!")
        print("=" * 60)
        print(f"📊 API Deals: {sync_status.total_deals_api:,}")
        print(f"💾 DB Deals: {sync_status.total_deals_db:,}")
        print(f"✅ Synced: {sync_status.new_deals_synced:,}")
        print(f"❌ Errors: {sync_status.sync_errors:,}")
        print(f"⏱️  Duration: {sync_status.sync_duration_seconds:.1f}s")
        print()
        print("🎯 Your deals are now permanently stored in Supabase!")
        print("Ready for dashboards, analytics, and business intelligence! 📈")
        
        return sync_status

if __name__ == "__main__":
    # Configuration
    roofmaxx_config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    # You'll need to provide your Supabase config
    supabase_config = {
        'url': 'YOUR_SUPABASE_URL',
        'access_token': 'YOUR_SUPABASE_ACCESS_TOKEN'
    }
    
    print("⚠️  PLEASE UPDATE SUPABASE CONFIG BEFORE RUNNING!")
    print("Update the supabase_config dictionary with your actual Supabase credentials")
    print()
    print("Then run: python3 src/services/supabase/deals_sync_service.py")
    
    # Uncomment when config is ready:
    # sync_service = DealsSyncService(roofmaxx_config, supabase_config)
    # sync_status = sync_service.run_full_sync() 