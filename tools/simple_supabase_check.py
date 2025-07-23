#!/usr/bin/env python3
"""
Simple Supabase Check

Uses the same connection method as the working pie chart tool.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Load environment variables
from config.env import load_env
load_env()

from src.services.supabase.client import SupabaseService

def main():
    """Check Supabase records and structure."""
    
    print("🔍 SIMPLE SUPABASE CHECK")
    print("=" * 50)
    
    # Initialize Supabase service (same as pie chart tool)
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
    
    # 1. Get total record count
    print(f"\n📊 RECORD COUNT")
    print("-" * 30)
    
    try:
        url = f"{service.url}/rest/v1/roofmaxx_deals"
        response = service.session.get(url, headers={'Prefer': 'count=exact'})
        response.raise_for_status()
        
        # Extract count from Content-Range header
        content_range = response.headers.get('Content-Range', '0-0/0')
        total_count = int(content_range.split('/')[-1])
        print(f"📈 Total records: {total_count:,}")
        
    except Exception as e:
        print(f"❌ Count error: {e}")
        return
    
    # 2. Check table structure
    print(f"\n🏗️ TABLE STRUCTURE")
    print("-" * 30)
    
    try:
        url = f"{service.url}/rest/v1/roofmaxx_deals"
        params = {'limit': 1}
        
        response = service.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            sample_record = data[0]
            print(f"📋 Available fields ({len(sample_record)} total):")
            
            # Show all fields organized
            for field_name in sorted(sample_record.keys()):
                field_value = sample_record[field_name]
                if field_value is not None:
                    if isinstance(field_value, str) and len(field_value) > 50:
                        display_value = f"{field_value[:47]}..."
                    else:
                        display_value = str(field_value)
                    print(f"   {field_name}: {display_value}")
                else:
                    print(f"   {field_name}: null")
        
    except Exception as e:
        print(f"❌ Structure error: {e}")
        return
    
    # 3. Check create_date specifically
    print(f"\n📅 CREATE_DATE CHECK")
    print("-" * 30)
    
    try:
        url = f"{service.url}/rest/v1/roofmaxx_deals"
        params = {
            'select': 'deal_id,create_date',
            'limit': 5,
            'order': 'create_date.desc.nullslast'
        }
        
        response = service.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            print(f"📊 Sample create_date values:")
            
            for i, record in enumerate(data, 1):
                deal_id = record.get('deal_id', 'N/A')
                create_date = record.get('create_date')
                
                if create_date:
                    try:
                        if 'T' in str(create_date):
                            dt = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                            formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                        else:
                            formatted_date = str(create_date)
                    except:
                        formatted_date = str(create_date)
                    
                    print(f"   {i}. Deal #{deal_id}: {formatted_date}")
                else:
                    print(f"   {i}. Deal #{deal_id}: ❌ No create_date")
            
            # Count records with create_date
            url_count = f"{service.url}/rest/v1/roofmaxx_deals"
            params_count = {
                'select': 'count',
                'create_date': 'not.is.null'
            }
            
            response_count = service.session.get(url_count, params=params_count, headers={'Prefer': 'count=exact'})
            
            if response_count.status_code == 200:
                content_range = response_count.headers.get('Content-Range', '0-0/0')
                records_with_date = int(content_range.split('/')[-1])
                
                print(f"\n📈 Records with create_date: {records_with_date:,} of {total_count:,}")
                
                if records_with_date == total_count:
                    print("✅ All records have create_date!")
                elif records_with_date > 0:
                    percentage = (records_with_date / total_count) * 100
                    print(f"⚠️  {percentage:.1f}% of records have create_date")
                else:
                    print("❌ No records have create_date")
        
    except Exception as e:
        print(f"❌ create_date error: {e}")
    
    print(f"\n✅ CHECK COMPLETE!")

if __name__ == "__main__":
    main() 