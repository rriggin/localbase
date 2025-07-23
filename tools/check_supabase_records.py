#!/usr/bin/env python3
"""
Check Supabase Records & Table Structure

Quick tool to check:
1. Total record count
2. Table structure and available fields
3. Whether create_date field exists and has data
"""

import sys
import os
from datetime import datetime
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Load environment variables
from config.env import load_env
load_env()

from src.services.supabase.client import SupabaseService

def main():
    """Check Supabase records and structure."""
    
    print("🔍 SUPABASE RECORDS & STRUCTURE CHECK")
    print("=" * 60)
    
    # Initialize Supabase service
    try:
        supabase_config = {
            'url': os.getenv('SUPABASE_URL'),
            'access_token': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        }
        
        supabase_service = SupabaseService(supabase_config)
        
        if not supabase_service.authenticate():
            print("❌ Failed to authenticate with Supabase")
            return
            
        print("✅ Connected to Supabase")
        
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return
    
    # 1. Get total record count
    print(f"\n📊 RECORD COUNT CHECK")
    print("=" * 30)
    
    try:
        # Use direct API call to get count
        response = supabase_service.session.get(
            f"{supabase_service.url}/rest/v1/roofmaxx_deals",
            params={'select': 'count'},
            headers={'Prefer': 'count=exact'}
        )
        
        if response.status_code == 200:
            # Extract count from Content-Range header
            content_range = response.headers.get('Content-Range', '0-0/0')
            total_count = int(content_range.split('/')[-1])
            print(f"📈 Total records in roofmaxx_deals: {total_count:,}")
        else:
            print(f"❌ Failed to get count: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Count check error: {e}")
    
    # 2. Get table structure by examining a sample record
    print(f"\n🏗️ TABLE STRUCTURE CHECK")
    print("=" * 30)
    
    try:
        # Get a sample record to see all available fields
        response = supabase_service.session.get(
            f"{supabase_service.url}/rest/v1/roofmaxx_deals",
            params={'limit': 1}
        )
        
        if response.status_code == 200:
            records = response.json()
            
            if records:
                sample_record = records[0]
                print(f"📋 Available fields ({len(sample_record)} total):")
                
                # Group fields by type for better readability
                id_fields = []
                customer_fields = []
                deal_fields = []
                location_fields = []
                date_fields = []
                other_fields = []
                
                for field_name, field_value in sample_record.items():
                    if 'id' in field_name.lower():
                        id_fields.append(field_name)
                    elif 'customer' in field_name.lower() or 'name' in field_name.lower() or 'email' in field_name.lower() or 'phone' in field_name.lower():
                        customer_fields.append(field_name)
                    elif 'deal' in field_name.lower() or 'stage' in field_name.lower() or 'lifecycle' in field_name.lower() or 'type' in field_name.lower():
                        deal_fields.append(field_name)
                    elif 'city' in field_name.lower() or 'state' in field_name.lower() or 'address' in field_name.lower() or 'postal' in field_name.lower():
                        location_fields.append(field_name)
                    elif 'date' in field_name.lower() or 'time' in field_name.lower() or 'created' in field_name.lower() or 'updated' in field_name.lower():
                        date_fields.append(field_name)
                    else:
                        other_fields.append(field_name)
                
                # Print organized fields
                if id_fields:
                    print(f"   🆔 ID Fields: {', '.join(id_fields)}")
                if deal_fields:
                    print(f"   💼 Deal Fields: {', '.join(deal_fields)}")
                if customer_fields:
                    print(f"   👤 Customer Fields: {', '.join(customer_fields)}")
                if location_fields:
                    print(f"   📍 Location Fields: {', '.join(location_fields)}")
                if date_fields:
                    print(f"   📅 Date Fields: {', '.join(date_fields)}")
                if other_fields:
                    print(f"   🔧 Other Fields: {', '.join(other_fields)}")
                
            else:
                print("❌ No records found to examine structure")
                
    except Exception as e:
        print(f"❌ Structure check error: {e}")
    
    # 3. Specifically check create_date field
    print(f"\n📅 CREATE_DATE FIELD CHECK")
    print("=" * 30)
    
    try:
        # Check if create_date exists and has data
        response = supabase_service.session.get(
            f"{supabase_service.url}/rest/v1/roofmaxx_deals",
            params={
                'select': 'deal_id,create_date',
                'limit': 10,
                'order': 'create_date.desc.nullslast'
            }
        )
        
        if response.status_code == 200:
            records = response.json()
            
            if records:
                print(f"📊 Sample create_date values:")
                
                # Count records with/without create_date
                has_create_date = 0
                no_create_date = 0
                
                for i, record in enumerate(records, 1):
                    deal_id = record.get('deal_id', 'N/A')
                    create_date = record.get('create_date')
                    
                    if create_date:
                        has_create_date += 1
                        # Format the date nicely
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
                        no_create_date += 1
                        print(f"   {i}. Deal #{deal_id}: ❌ No create_date")
                
                # Get total count of records with create_date
                count_response = supabase_service.session.get(
                    f"{supabase_service.url}/rest/v1/roofmaxx_deals",
                    params={
                        'select': 'count',
                        'create_date': 'not.is.null'
                    },
                    headers={'Prefer': 'count=exact'}
                )
                
                if count_response.status_code == 200:
                    content_range = count_response.headers.get('Content-Range', '0-0/0')
                    records_with_date = int(content_range.split('/')[-1])
                    
                    print(f"\n📈 Records with create_date: {records_with_date:,}")
                    
                    if total_count > 0:
                        percentage = (records_with_date / total_count) * 100
                        print(f"📊 Percentage with dates: {percentage:.1f}%")
                        
                        if records_with_date == total_count:
                            print("✅ All records have create_date!")
                        elif records_with_date > 0:
                            print("⚠️ Some records missing create_date")
                        else:
                            print("❌ No records have create_date")
                
            else:
                print("❌ No records found")
                
    except Exception as e:
        print(f"❌ create_date check error: {e}")
    
    print(f"\n✅ ANALYSIS COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main() 