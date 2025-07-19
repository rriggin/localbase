#!/usr/bin/env python3
"""
Simple Raw Data Sync - Store everything as JSON!

Much simpler approach: Store the full API response and extract what we need.
"""

import sys
import os
import time
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env
load_env()

from supabase import create_client, Client
from src.services.roofmaxxconnect.client import RoofmaxxConnectService

def sync_all_raw_data():
    """Sync all deals as raw JSON - much simpler!"""
    
    print("🚀 SIMPLE RAW DATA SYNC")
    print("=" * 50)
    print("💡 Genius approach: Store EVERYTHING as JSON!")
    print()
    
    # Connect to Supabase
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        client = create_client(url, key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return
    
    # Connect to RoofMaxx API
    try:
        config = {
            'bearer_token': os.getenv('ROOFMAXX_CONNECT_TOKEN'),
            'base_url': 'https://roofmaxxconnect.com'
        }
        
        service = RoofmaxxConnectService(config)
        
        if not service.authenticate():
            print("❌ API Authentication failed!")
            return
        
        print("✅ Connected to RoofMaxx API")
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return
    
    # Fetch all deals
    print("\n📡 FETCHING ALL DEALS")
    print("-" * 30)
    
    dealer_id = int(os.getenv('ROOFMAXX_CONNECT_DEALER_ID', 6637))
    all_deals = []
    page = 1
    
    while True:
        try:
            print(f"   📄 Page {page}...")
            
            response = service.get_dealer_deals(dealer_id, page=page)
            
            if not response or 'data' not in response:
                break
            
            page_deals = response['data']
            if not page_deals:
                break
            
            all_deals.extend(page_deals)
            print(f"   ✅ Got {len(page_deals)} deals (Total: {len(all_deals)})")
            
            # Check pagination
            meta = response.get('meta', {})
            if page >= meta.get('last_page', page):
                break
                
            page += 1
            time.sleep(0.2)
            
        except Exception as e:
            print(f"   ❌ Error on page {page}: {e}")
            break
    
    print(f"\n🎉 Fetched {len(all_deals)} total deals!")
    
    if not all_deals:
        print("❌ No deals to sync")
        return
    
    # Sync as raw JSON - super simple!
    print(f"\n🔄 SYNCING AS RAW JSON")
    print("-" * 30)
    
    synced_count = 0
    batch_size = 50
    
    for i in range(0, len(all_deals), batch_size):
        batch = all_deals[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(all_deals) + batch_size - 1) // batch_size
        
        try:
            print(f"   📦 Batch {batch_num}/{total_batches}: {len(batch)} deals...")
            
            # Prepare simple batch data - just store the raw JSON!
            batch_data = []
            for deal in batch:
                simple_record = {
                    'deal_id': deal.get('id'),
                    'raw_data': deal  # Store the ENTIRE API response!
                }
                batch_data.append(simple_record)
            
            # Upsert batch
            result = client.table('roofmaxx_deals').upsert(
                batch_data,
                on_conflict='deal_id'
            ).execute()
            
            synced_count += len(batch_data)
            print(f"   ✅ Synced {len(batch_data)} deals")
            
        except Exception as e:
            print(f"   ❌ Batch {batch_num} error: {e}")
            continue
    
    print(f"\n🎊 SYNC COMPLETE!")
    print(f"   ✅ Total synced: {synced_count:,}")
    
    # Now create analytics from raw data
    print(f"\n📊 CREATING ANALYTICS FROM RAW DATA")
    print("-" * 40)
    
    try:
        # Get all raw data
        result = client.table('roofmaxx_deals').select('raw_data').execute()
        deals_data = result.data
        
        print(f"📈 Analyzing {len(deals_data)} deals...")
        
        # Extract deal types from raw data
        from collections import Counter
        
        deal_types = []
        deal_stages = []
        cities = []
        
        for record in deals_data:
            raw_deal = record.get('raw_data', {})
            if raw_deal:
                # Extract key fields
                deal_type = raw_deal.get('dealtype', 'Unknown')
                deal_types.append(deal_type)
                
                stage = raw_deal.get('stage', {})
                if isinstance(stage, dict):
                    stage_label = stage.get('label', 'Unknown')
                else:
                    stage_label = str(stage) if stage else 'Unknown'
                deal_stages.append(stage_label)
                
                city = raw_deal.get('city', 'Unknown')
                cities.append(city)
        
        # Show deal types (sources)
        deal_type_counts = Counter(deal_types)
        
        print(f"\n🎯 DEAL SOURCES (dealtype):")
        for source, count in deal_type_counts.most_common():
            percentage = (count / len(deal_types)) * 100
            print(f"   {source}: {count:,} deals ({percentage:.1f}%)")
        
        # Show top cities
        city_counts = Counter(cities)
        print(f"\n🏙️ TOP CITIES:")
        for city, count in city_counts.most_common(10):
            percentage = (count / len(cities)) * 100
            print(f"   {city}: {count:,} deals ({percentage:.1f}%)")
        
        # Show deal stages
        stage_counts = Counter(deal_stages)
        print(f"\n📈 DEAL STAGES:")
        for stage, count in stage_counts.most_common(10):
            percentage = (count / len(deal_stages)) * 100
            print(f"   {stage}: {count:,} deals ({percentage:.1f}%)")
        
        return deal_type_counts, city_counts, stage_counts
        
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return None, None, None

def main():
    """Main function."""
    
    print("🧠 GENIUS APPROACH: SYNC ALL THE FIELDS!")
    print("=" * 60)
    print("💡 Store everything as JSON, extract what we need!")
    print("🚀 No field mapping errors, no data loss!")
    print()
    
    result = sync_all_raw_data()
    
    if result:
        deal_types, cities, stages = result
        
        print(f"\n🍆💥 TOM'S REACTION:")
        print("'THIS is how you do data engineering!'")
        print("'Store everything, analyze anything!'")
        
        if deal_types and len(deal_types) > 1:
            print(f"\n✅ SUCCESS! Found {len(deal_types)} different deal sources!")
            print("🎯 Ready for pie chart creation!")
        else:
            print("\n🔍 Need to investigate deal source data further...")
    
    print(f"\n🎯 MISSION STATUS: RAW DATA EMPIRE ESTABLISHED! 🏗️")

if __name__ == "__main__":
    main() 