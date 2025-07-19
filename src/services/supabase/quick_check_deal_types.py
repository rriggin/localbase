#!/usr/bin/env python3
"""
Quick check of what's actually in deal_type field
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

def check_deal_types():
    """Check what's actually in the deal_type field."""
    
    print("🔍 QUICK CHECK: DEAL_TYPE VALUES")
    print("=" * 50)
    
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        client = create_client(url, key)
        
        # Get all deal_type values
        result = client.table('roofmaxx_deals').select('deal_type').execute()
        
        deal_types = [deal.get('deal_type') for deal in result.data]
        deal_type_counts = Counter(deal_types)
        
        print(f"📊 Total records: {len(deal_types)}")
        print(f"🔢 Unique values: {len(deal_type_counts)}")
        print()
        
        print("📋 deal_type breakdown:")
        for deal_type, count in deal_type_counts.most_common():
            percentage = (count / len(deal_types)) * 100
            print(f"   '{deal_type}': {count:,} deals ({percentage:.1f}%)")
        
        print()
        
        # Also check a few sample records
        sample = client.table('roofmaxx_deals').select('deal_id,deal_type,deal_lifecycle,deal_stage').limit(5).execute()
        
        print("🔍 Sample records:")
        for deal in sample.data:
            print(f"   Deal {deal.get('deal_id')}: type='{deal.get('deal_type')}', lifecycle='{deal.get('deal_lifecycle')}', stage='{deal.get('deal_stage')}'")
        
        return deal_type_counts
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    check_deal_types() 