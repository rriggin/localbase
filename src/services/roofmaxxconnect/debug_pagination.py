#!/usr/bin/env python3
"""
Debug Pagination for Dealer 6637

Let's see what the API is REALLY returning and why we're only getting 10 deals!
"""

import sys
import os
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.roofmaxxconnect.client import RoofmaxxConnectService

def debug_pagination():
    """Debug what's really happening with the API pagination."""
    
    print("🔍 DEBUGGING DEAL PAGINATION FOR DEALER 6637")
    print("=" * 60)
    print("Let's see what the API is REALLY telling us! 🕵️")
    print()
    
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    service = RoofmaxxConnectService(config)
    
    if not service.authenticate():
        print("❌ Authentication failed!")
        return
    
    print("✅ Connected successfully!")
    print()
    
    # Let's examine the EXACT API response
    print("🔍 EXAMINING RAW API RESPONSE:")
    print("-" * 50)
    
    try:
        # Get the raw response
        response = service.get_dealer_deals(6637, page=1, per_page=100)
        
        print("📋 Complete API Response Structure:")
        print(json.dumps(response, indent=2))
        print()
        
        # Check for pagination metadata
        if 'meta' in response:
            meta = response['meta']
            print("📊 PAGINATION METADATA:")
            for key, value in meta.items():
                print(f"   {key}: {value}")
            print()
        
        if 'links' in response:
            links = response['links']
            print("🔗 PAGINATION LINKS:")
            for key, value in links.items():
                print(f"   {key}: {value}")
            print()
        
        # Check the data
        if 'data' in response:
            deals = response['data']
            print(f"📊 DEALS DATA:")
            print(f"   Total deals in response: {len(deals)}")
            
            if deals:
                print(f"   First deal ID: {deals[0].get('id', 'N/A')}")
                print(f"   Last deal ID: {deals[-1].get('id', 'N/A')}")
            print()
        
        # Try page 2 explicitly
        print("🔍 TRYING PAGE 2 EXPLICITLY:")
        print("-" * 50)
        
        try:
            response2 = service.get_dealer_deals(6637, page=2, per_page=100)
            print("📋 Page 2 Response:")
            print(json.dumps(response2, indent=2))
            
            if 'data' in response2:
                page2_deals = response2['data']
                print(f"📊 Page 2 deals count: {len(page2_deals)}")
        except Exception as e:
            print(f"❌ Page 2 error: {e}")
        
        print()
        
        # Try different per_page values
        print("🔍 TRYING DIFFERENT PER_PAGE VALUES:")
        print("-" * 50)
        
        for per_page in [10, 25, 50, 200]:
            try:
                test_response = service.get_dealer_deals(6637, page=1, per_page=per_page)
                if 'data' in test_response:
                    count = len(test_response['data'])
                    print(f"   per_page={per_page}: {count} deals returned")
                    
                    if 'meta' in test_response and 'total' in test_response['meta']:
                        total = test_response['meta']['total']
                        print(f"   per_page={per_page}: meta.total = {total}")
            except Exception as e:
                print(f"   per_page={per_page}: ERROR - {e}")
        
        print()
        
        # Try without pagination parameters
        print("🔍 TRYING WITHOUT PAGINATION PARAMS:")
        print("-" * 50)
        
        try:
            # Direct API call
            endpoint = f"/api/v2/dealers/6637/deals"
            raw_response = service._make_request('GET', endpoint)
            
            if raw_response.status_code == 200:
                raw_data = raw_response.json()
                print("📋 Raw response (no params):")
                print(json.dumps(raw_data, indent=2))
            else:
                print(f"❌ Raw request failed: {raw_response.status_code}")
                print(f"Response: {raw_response.text}")
        
        except Exception as e:
            print(f"❌ Raw request error: {e}")
    
    except Exception as e:
        print(f"❌ Main request failed: {e}")
        print("💡 This might indicate a permission or API structure issue")

def test_different_dealer_ids():
    """Test if other dealer IDs have more deals to understand the pattern."""
    
    print("\n🔍 TESTING OTHER DEALER IDS FOR COMPARISON:")
    print("=" * 60)
    
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    service = RoofmaxxConnectService(config)
    
    # Test a few other dealer IDs that we know exist
    test_dealer_ids = [1, 17, 100, 6637]
    
    for dealer_id in test_dealer_ids:
        try:
            print(f"🔍 Testing dealer {dealer_id}:")
            response = service.get_dealer_deals(dealer_id, page=1, per_page=10)
            
            if 'data' in response:
                deal_count = len(response['data'])
                print(f"   ✅ {deal_count} deals found")
                
                if 'meta' in response:
                    meta = response['meta']
                    if 'total' in meta:
                        print(f"   📊 Total available: {meta['total']}")
            else:
                print(f"   ❌ No data in response")
                
        except Exception as e:
            print(f"   🚫 Error: {str(e)[:50]}...")
        
        print()

if __name__ == "__main__":
    debug_pagination()
    test_different_dealer_ids()
    
    print("\n🎯 DEBUGGING COMPLETE!")
    print("=" * 60)
    print("Now we'll know exactly what's happening with the pagination! 🕵️") 