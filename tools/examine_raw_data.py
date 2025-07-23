#!/usr/bin/env python3
"""
Examine Raw Data Structure

Look at the raw_data field to find date fields and understand the structure.
"""

import sys
import os
import json
from datetime import datetime
from collections import Counter

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Load environment variables
from config.env import load_env
load_env()

from src.services.supabase.client import SupabaseService

def convert_timestamp(timestamp):
    """Convert various timestamp formats to readable date."""
    if not timestamp:
        return None
    
    try:
        # Try Unix timestamp (milliseconds)
        if isinstance(timestamp, (int, float)) and timestamp > 1000000000:
            if timestamp > 10000000000:  # Milliseconds
                dt = datetime.fromtimestamp(timestamp / 1000)
            else:  # Seconds
                dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    
    try:
        # Try ISO format
        if isinstance(timestamp, str):
            if 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    
    return str(timestamp)

def main():
    """Examine raw data structure."""
    
    print("🔍 EXAMINING RAW DATA STRUCTURE")
    print("=" * 60)
    
    # Connect to Supabase
    supabase_config = {
        'url': os.getenv('SUPABASE_URL'),
        'access_token': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }
    
    try:
        service = SupabaseService(supabase_config)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return
    
    # Get sample raw data
    print(f"\n📊 FETCHING SAMPLE RAW DATA")
    print("-" * 40)
    
    try:
        url = f"{service.url}/rest/v1/roofmaxx_deals"
        params = {'select': 'deal_id,raw_data', 'limit': 10}
        
        response = service.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            print("❌ No data found")
            return
        
        print(f"📥 Retrieved {len(data)} sample records")
        
        # Analyze raw data structure
        all_fields = set()
        date_like_fields = []
        
        print(f"\n🔍 ANALYZING RAW DATA FIELDS")
        print("-" * 40)
        
        for i, record in enumerate(data[:3], 1):  # Look at first 3 records
            raw_data = record.get('raw_data', {})
            deal_id = record.get('deal_id')
            
            if isinstance(raw_data, dict):
                print(f"\n📋 Record {i} (Deal #{deal_id}):")
                
                # Collect all fields
                all_fields.update(raw_data.keys())
                
                # Look for date-like fields
                for field_name, field_value in raw_data.items():
                    if any(word in field_name.lower() for word in ['date', 'time', 'created', 'updated', 'modified']):
                        date_like_fields.append((field_name, field_value))
                        converted = convert_timestamp(field_value)
                        print(f"   📅 {field_name}: {field_value} → {converted}")
                    elif isinstance(field_value, (int, float)) and field_value > 1000000000:
                        # Might be a Unix timestamp
                        converted = convert_timestamp(field_value)
                        if converted and converted != str(field_value):
                            date_like_fields.append((field_name, field_value))
                            print(f"   🕐 {field_name}: {field_value} → {converted}")
        
        # Summary of all fields found
        print(f"\n📋 ALL FIELDS IN RAW DATA ({len(all_fields)} total):")
        print("-" * 50)
        
        # Group fields by type
        id_fields = [f for f in all_fields if 'id' in f.lower()]
        date_fields = [f for f in all_fields if any(word in f.lower() for word in ['date', 'time', 'created', 'updated', 'modified'])]
        contact_fields = [f for f in all_fields if any(word in f.lower() for word in ['contact', 'customer', 'name', 'email', 'phone'])]
        deal_fields = [f for f in all_fields if any(word in f.lower() for word in ['deal', 'stage', 'lifecycle', 'type'])]
        location_fields = [f for f in all_fields if any(word in f.lower() for word in ['address', 'city', 'state', 'postal', 'zip'])]
        other_fields = [f for f in all_fields if f not in id_fields + date_fields + contact_fields + deal_fields + location_fields]
        
        if id_fields:
            print(f"🆔 ID Fields: {', '.join(sorted(id_fields))}")
        if date_fields:
            print(f"📅 Date Fields: {', '.join(sorted(date_fields))}")
        if deal_fields:
            print(f"💼 Deal Fields: {', '.join(sorted(deal_fields))}")
        if contact_fields:
            print(f"👤 Contact Fields: {', '.join(sorted(contact_fields))}")
        if location_fields:
            print(f"📍 Location Fields: {', '.join(sorted(location_fields))}")
        if other_fields:
            print(f"🔧 Other Fields: {', '.join(sorted(other_fields))}")
        
        # Focus on date fields
        if date_like_fields:
            print(f"\n🎯 DATE FIELD ANALYSIS")
            print("-" * 30)
            
            # Count occurrences of each date field
            date_field_counts = Counter([field for field, value in date_like_fields])
            
            for field_name, count in date_field_counts.most_common():
                print(f"📊 {field_name}: appears in {count} records")
                
                # Show sample values for this field
                sample_values = [value for field, value in date_like_fields if field == field_name][:3]
                for value in sample_values:
                    converted = convert_timestamp(value)
                    print(f"   • {value} → {converted}")
        
        # Get a more comprehensive analysis
        print(f"\n🔬 COMPREHENSIVE DATE FIELD SCAN")
        print("-" * 40)
        
        # Get more records to find all date patterns
        url = f"{service.url}/rest/v1/roofmaxx_deals"
        params = {'select': 'raw_data', 'limit': 50}
        
        response = service.session.get(url, params=params)
        response.raise_for_status()
        
        all_data = response.json()
        
        all_date_fields = Counter()
        
        for record in all_data:
            raw_data = record.get('raw_data', {})
            if isinstance(raw_data, dict):
                for field_name, field_value in raw_data.items():
                    # Check for date-like field names
                    if any(word in field_name.lower() for word in ['date', 'time', 'created', 'updated', 'modified']):
                        all_date_fields[field_name] += 1
                    # Check for Unix timestamps
                    elif isinstance(field_value, (int, float)) and 1000000000 < field_value < 9999999999999:
                        converted = convert_timestamp(field_value)
                        if converted and converted != str(field_value):
                            all_date_fields[field_name] += 1
        
        print(f"📈 Date fields found across {len(all_data)} records:")
        for field_name, count in all_date_fields.most_common():
            percentage = (count / len(all_data)) * 100
            print(f"   {field_name}: {count}/{len(all_data)} records ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ ANALYSIS COMPLETE!")

if __name__ == "__main__":
    main() 