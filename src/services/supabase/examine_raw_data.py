#!/usr/bin/env python3
"""
Examine raw_data to find source information
"""

import sys
import os
import json
from collections import Counter

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env
load_env()

from supabase import create_client, Client

def examine_raw_data():
    """Examine the raw_data field to find source information."""
    
    print("🔍 EXAMINING RAW DATA FOR SOURCE INFO")
    print("=" * 50)
    
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        client = create_client(url, key)
        
        # Get sample raw_data to see structure
        print("📊 Fetching sample raw_data...")
        result = client.table('roofmaxx_deals').select('deal_id,raw_data').limit(5).execute()
        
        if result.data:
            print(f"🔍 Found {len(result.data)} sample records")
            print()
            
            for i, record in enumerate(result.data, 1):
                print(f"📋 Sample Record {i} (Deal ID: {record.get('deal_id')}):")
                print("-" * 40)
                
                raw_data = record.get('raw_data')
                if raw_data:
                    # Print the raw data structure
                    if isinstance(raw_data, dict):
                        print("🗂️  Raw data keys:")
                        for key in sorted(raw_data.keys()):
                            value = raw_data[key]
                            if isinstance(value, (str, int, float, bool)) and value is not None:
                                print(f"   • {key}: {value}")
                            elif isinstance(value, dict):
                                print(f"   • {key}: {dict} with keys: {list(value.keys())}")
                            elif isinstance(value, list):
                                print(f"   • {key}: {list} with {len(value)} items")
                            else:
                                print(f"   • {key}: {type(value).__name__}")
                    else:
                        print(f"Raw data type: {type(raw_data)}")
                        print(f"Raw data: {raw_data}")
                else:
                    print("❌ No raw_data found")
                print()
                
                # Look for potential source fields
                if isinstance(raw_data, dict):
                    potential_sources = []
                    for key, value in raw_data.items():
                        if 'source' in key.lower() or 'type' in key.lower() or 'origin' in key.lower():
                            potential_sources.append((key, value))
                    
                    if potential_sources:
                        print("🎯 Potential source fields:")
                        for key, value in potential_sources:
                            print(f"   • {key}: {value}")
                    print()
        
        # Now let's get all raw_data and analyze for sources
        print("🔍 ANALYZING ALL RAW DATA FOR SOURCE PATTERNS")
        print("-" * 50)
        
        result = client.table('roofmaxx_deals').select('raw_data').execute()
        
        # Collect all potential source values
        all_source_candidates = {}
        
        for record in result.data:
            raw_data = record.get('raw_data')
            if isinstance(raw_data, dict):
                for key, value in raw_data.items():
                    if ('source' in key.lower() or 'type' in key.lower() or 
                        'origin' in key.lower() or 'lead' in key.lower()):
                        if key not in all_source_candidates:
                            all_source_candidates[key] = []
                        all_source_candidates[key].append(value)
        
        # Show source candidates
        print("📊 SOURCE CANDIDATE ANALYSIS:")
        print("-" * 40)
        
        for field_name, values in all_source_candidates.items():
            unique_values = Counter(values)
            print(f"\n🔑 Field: '{field_name}'")
            print(f"   Total entries: {len(values)}")
            print(f"   Unique values: {len(unique_values)}")
            print("   Top values:")
            for value, count in unique_values.most_common(5):
                percentage = (count / len(values)) * 100
                print(f"     • {value}: {count:,} ({percentage:.1f}%)")
        
        return all_source_candidates
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def main():
    """Main examination function."""
    
    print("🕵️ RAW DATA DETECTIVE WORK")
    print("=" * 60)
    print("Let's find where the REAL source data is hiding!")
    print()
    
    source_candidates = examine_raw_data()
    
    if source_candidates:
        print(f"\n🎯 RECOMMENDATION:")
        print("-" * 20)
        
        # Find the best candidate field
        best_candidate = None
        max_diversity = 0
        
        for field_name, values in source_candidates.items():
            unique_count = len(set(values))
            if unique_count > max_diversity:
                max_diversity = unique_count
                best_candidate = field_name
        
        if best_candidate:
            print(f"✅ Best source field candidate: '{best_candidate}'")
            print(f"   Reason: Has {max_diversity} unique values")
            print()
            print("💡 We can extract this from raw_data for our analytics!")
        else:
            print("⚠️  No clear source field found in raw_data")
    else:
        print("❌ No source candidates found")
    
    print(f"\n🍆💥 Tom says: 'Now we're getting to the REAL data!'")

if __name__ == "__main__":
    main() 