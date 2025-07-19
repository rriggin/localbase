#!/usr/bin/env python3
"""
Debug Deal Types - Let's see what's actually in our data!
"""

import sys
import os
from collections import Counter

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env
load_env()

from supabase import create_client, Client

def debug_deal_data():
    """Debug the deal data to see what we actually have."""
    
    print("🔍 DEBUGGING DEAL DATA")
    print("=" * 50)
    
    try:
        # Connect to Supabase
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        client = create_client(url, key)
        
        # Get a sample of all fields to see what we have
        print("📊 Fetching sample data...")
        result = client.table('roofmaxx_deals').select('*').limit(10).execute()
        
        if result.data:
            sample_deal = result.data[0]
            print(f"🔍 Sample deal fields:")
            for field, value in sample_deal.items():
                print(f"   {field}: {value}")
            print()
        
        # Now let's specifically check deal_type values
        print("🎯 CHECKING DEAL_TYPE VALUES:")
        print("-" * 40)
        
        # Get all deal_type values
        result = client.table('roofmaxx_deals').select('deal_type').execute()
        
        deal_types = [deal.get('deal_type') for deal in result.data]
        deal_type_counts = Counter(deal_types)
        
        print(f"📈 Total records: {len(deal_types)}")
        print(f"🔢 Unique deal types: {len(deal_type_counts)}")
        print()
        
        print("📋 Deal type breakdown:")
        for deal_type, count in deal_type_counts.most_common():
            percentage = (count / len(deal_types)) * 100
            print(f"   '{deal_type}': {count:,} deals ({percentage:.1f}%)")
        print()
        
        # Let's also check what other fields might indicate source
        print("🔍 CHECKING OTHER POTENTIAL SOURCE FIELDS:")
        print("-" * 50)
        
        # Check deal_lifecycle
        result = client.table('roofmaxx_deals').select('deal_lifecycle').execute()
        lifecycles = [deal.get('deal_lifecycle') for deal in result.data]
        lifecycle_counts = Counter(lifecycles)
        
        print("📋 Deal lifecycle breakdown:")
        for lifecycle, count in lifecycle_counts.most_common():
            percentage = (count / len(lifecycles)) * 100
            print(f"   '{lifecycle}': {count:,} deals ({percentage:.1f}%)")
        print()
        
        # Check deal_stage
        result = client.table('roofmaxx_deals').select('deal_stage').execute()
        stages = [deal.get('deal_stage') for deal in result.data]
        stage_counts = Counter(stages)
        
        print("📋 Deal stage breakdown (top 10):")
        for stage, count in stage_counts.most_common(10):
            percentage = (count / len(stages)) * 100
            print(f"   '{stage}': {count:,} deals ({percentage:.1f}%)")
        print()
        
        # Let's look at some raw data to understand the structure
        print("🔍 RAW DATA SAMPLE (first 5 deals):")
        print("-" * 40)
        
        result = client.table('roofmaxx_deals').select('deal_id,deal_type,deal_lifecycle,deal_stage').limit(5).execute()
        
        for i, deal in enumerate(result.data, 1):
            print(f"Deal {i}:")
            print(f"   ID: {deal.get('deal_id')}")
            print(f"   Type: '{deal.get('deal_type')}'")
            print(f"   Lifecycle: '{deal.get('deal_lifecycle')}'")
            print(f"   Stage: '{deal.get('deal_stage')}'")
            print()
        
        return deal_type_counts, lifecycle_counts, stage_counts
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return None, None, None

def main():
    """Main debug function."""
    
    print("🕵️ DEAL DATA DETECTIVE WORK")
    print("=" * 60)
    print("Let's figure out why we only see one source!")
    print()
    
    deal_types, lifecycles, stages = debug_deal_data()
    
    print("🎯 DIAGNOSIS:")
    print("-" * 20)
    
    if deal_types and len(deal_types) == 1:
        print("❌ ISSUE FOUND: All deal_type values are the same!")
        print("💡 SOLUTION: We need to use a different field for source analysis")
        print()
        
        if lifecycles and len(lifecycles) > 1:
            print("✅ Alternative: Use 'deal_lifecycle' for source analysis")
        elif stages and len(stages) > 1:
            print("✅ Alternative: Use 'deal_stage' for source analysis")
        else:
            print("⚠️  Need to investigate raw data more deeply")
    
    elif deal_types and len(deal_types) > 1:
        print("✅ Deal types look good - might be a visualization bug")
    
    else:
        print("❓ Need more investigation")
    
    print(f"\n🍆💥 Tom says: 'Let's get the REAL source data!'")

if __name__ == "__main__":
    main() 