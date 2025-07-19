#!/usr/bin/env python3
"""
Check the actual API response to find source fields
"""

import sys
import os
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env
load_env()

from src.services.roofmaxxconnect.client import RoofmaxxConnectService

def check_api_response():
    """Check the actual API response structure."""
    
    print("🔍 CHECKING ACTUAL API RESPONSE STRUCTURE")
    print("=" * 60)
    
    try:
        # Connect to API
        config = {
            'bearer_token': os.getenv('ROOFMAXX_CONNECT_TOKEN'),
            'base_url': 'https://roofmaxxconnect.com'
        }
        
        service = RoofmaxxConnectService(config)
        
        print("🔐 Testing authentication...")
        if not service.authenticate():
            print("❌ Authentication failed!")
            return
        
        print("✅ Authentication successful!")
        
        # Get a small sample of deals
        print("📡 Fetching sample deals to examine structure...")
        dealer_id = int(os.getenv('ROOFMAXX_CONNECT_DEALER_ID', 6637))
        
        response = service.get_dealer_deals(dealer_id, page=1)
        
        if response and 'data' in response:
            deals = response['data']
            
            print(f"📊 Got {len(deals)} sample deals")
            print()
            
            if deals:
                # Examine the first deal structure
                first_deal = deals[0]
                
                print("🔍 FIRST DEAL STRUCTURE:")
                print("-" * 40)
                print(json.dumps(first_deal, indent=2, default=str))
                print()
                
                # Look for source-related fields
                print("🎯 LOOKING FOR SOURCE FIELDS:")
                print("-" * 40)
                
                source_candidates = []
                
                for key, value in first_deal.items():
                    if ('source' in key.lower() or 'type' in key.lower() or 
                        'origin' in key.lower() or 'lead' in key.lower() or
                        'channel' in key.lower()):
                        source_candidates.append((key, value))
                
                if source_candidates:
                    print("✅ Potential source fields found:")
                    for key, value in source_candidates:
                        print(f"   • {key}: {value}")
                else:
                    print("❌ No obvious source fields found")
                
                print()
                
                # Show all available fields
                print("📋 ALL AVAILABLE FIELDS:")
                print("-" * 30)
                for key in sorted(first_deal.keys()):
                    value = first_deal[key]
                    if isinstance(value, (str, int, float, bool)) and value is not None:
                        print(f"   • {key}: {value}")
                    elif isinstance(value, dict):
                        print(f"   • {key}: {dict} with keys: {list(value.keys())}")
                    elif isinstance(value, list):
                        print(f"   • {key}: {list} with {len(value)} items")
                    else:
                        print(f"   • {key}: {type(value).__name__}")
                
                print()
                
                # Check all deals for source diversity
                print("🔍 ANALYZING ALL SAMPLE DEALS FOR SOURCE PATTERNS:")
                print("-" * 60)
                
                from collections import Counter
                
                # Check all fields for diversity
                field_diversity = {}
                
                for deal in deals:
                    for key, value in deal.items():
                        if key not in field_diversity:
                            field_diversity[key] = []
                        field_diversity[key].append(value)
                
                # Show fields with multiple unique values (potential sources)
                diverse_fields = []
                for field_name, values in field_diversity.items():
                    unique_values = len(set(str(v) for v in values if v is not None))
                    if unique_values > 1 and unique_values < len(deals):  # Not all different, not all same
                        diverse_fields.append((field_name, unique_values, Counter(values)))
                
                print("📊 FIELDS WITH MULTIPLE VALUES (Potential Sources):")
                for field_name, unique_count, value_counts in diverse_fields:
                    print(f"\n🔑 {field_name}: {unique_count} unique values")
                    for value, count in value_counts.most_common(3):
                        print(f"     • {value}: {count} deals")
                
                return first_deal, diverse_fields
        
        else:
            print("❌ No deal data received")
            return None, None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def main():
    """Main function."""
    
    print("🕵️ API RESPONSE DETECTIVE WORK")
    print("=" * 60)
    print("Let's see what the API actually gives us!")
    print()
    
    deal_structure, diverse_fields = check_api_response()
    
    if deal_structure and diverse_fields:
        print(f"\n🎯 ANALYSIS COMPLETE!")
        print("-" * 30)
        
        # Find the most likely source field
        likely_sources = []
        for field_name, unique_count, value_counts in diverse_fields:
            if ('type' in field_name.lower() or 'source' in field_name.lower() or 
                'lead' in field_name.lower() or 'channel' in field_name.lower()):
                likely_sources.append((field_name, unique_count))
        
        if likely_sources:
            print("✅ Most likely source fields:")
            for field_name, unique_count in likely_sources:
                print(f"   • {field_name}: {unique_count} unique values")
        else:
            print("⚠️  No obvious source fields, but these have diversity:")
            for field_name, unique_count, _ in diverse_fields[:5]:
                print(f"   • {field_name}: {unique_count} unique values")
    
    print(f"\n🍆💥 Tom says: 'Now we know what we're working with!'")

if __name__ == "__main__":
    main() 