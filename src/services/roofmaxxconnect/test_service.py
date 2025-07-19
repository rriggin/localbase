#!/usr/bin/env python3
"""
RoofMaxx Connect Service Test Script

Test the RoofMaxx Connect API integration with the provided bearer token.
This script will help us understand the actual API structure and endpoints.
"""

import sys
import os
import json
from typing import Dict, Any

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.roofmaxxconnect.client import RoofmaxxConnectService
from src.services.roofmaxxconnect.exceptions import RoofmaxxError

def test_roofmaxx_connect_service():
    """Test the RoofMaxx Connect service with the provided API token."""
    
    # Configuration with the provided bearer token
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    print("🏠 RoofMaxx Connect Service Test")
    print("=" * 50)
    
    try:
        # Initialize the service
        print("\n1. Initializing RoofMaxx Connect service...")
        service = RoofmaxxConnectService(config)
        print("✅ Service initialized successfully")
        
        # Test authentication
        print("\n2. Testing authentication...")
        auth_result = service.authenticate()
        print(f"{'✅' if auth_result else '❌'} Authentication: {auth_result}")
        
        # Health check
        print("\n3. Running health check...")
        health = service.health_check()
        print(f"📊 Health Status: {health['status']}")
        print(f"🔗 Base URL: {health['base_url']}")
        if 'response_time_seconds' in health:
            print(f"⏱️  Response Time: {health['response_time_seconds']:.3f}s")
        
        # API endpoint discovery
        print("\n4. Discovering API endpoints...")
        discovery = service.discover_api_endpoints()
        print(f"🔍 Endpoints tested: {len(discovery['endpoints_tested'])}")
        print(f"✅ Available endpoints: {len(discovery['available_endpoints'])}")
        
        for endpoint_test in discovery['endpoints_tested']:
            status_icon = "✅" if endpoint_test['accessible'] else "❌"
            print(f"  {status_icon} {endpoint_test['endpoint']} - Status: {endpoint_test['status_code']}")
        
        # Try to discover dealer ID or test common endpoints
        print("\n5. Testing common dealer endpoints...")
        test_dealer_endpoints(service)
        
        print("\n" + "=" * 50)
        print("🎉 RoofMaxx Connect service test completed!")
        
        # Summary
        print(f"\n📋 SUMMARY:")
        print(f"   Service Status: {'Operational' if auth_result else 'Authentication Failed'}")
        print(f"   Available Endpoints: {len(discovery['available_endpoints'])}")
        print(f"   Base URL: {config['base_url']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

def test_dealer_endpoints(service: RoofmaxxConnectService):
    """Test dealer-specific endpoints to understand the API structure."""
    
    # Common dealer IDs to test (these are usually numeric or alphanumeric)
    test_dealer_ids = ['1', '100', 'demo', 'test', 'rmc001']
    
    for dealer_id in test_dealer_ids:
        try:
            print(f"  🔍 Testing dealer ID: {dealer_id}")
            
            # Try to get deals for this dealer
            response = service.get_dealer_deals(dealer_id, page=1, per_page=5)
            print(f"    ✅ Got response for dealer {dealer_id}: {type(response).__name__}")
            
            if isinstance(response, dict):
                # Print structure of response to understand the API
                keys = list(response.keys())
                print(f"    📄 Response keys: {keys[:5]}{'...' if len(keys) > 5 else ''}")
                
                # Look for pagination info
                if 'total' in response:
                    print(f"    📊 Total records: {response['total']}")
                if 'data' in response and isinstance(response['data'], list):
                    print(f"    📋 Data records: {len(response['data'])}")
            
            break  # If we found a working dealer ID, stop testing
            
        except RoofmaxxError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                print(f"    ❌ Dealer {dealer_id} not found")
            else:
                print(f"    ⚠️  Error for dealer {dealer_id}: {e}")
        except Exception as e:
            print(f"    💥 Unexpected error for dealer {dealer_id}: {e}")

def print_api_response_structure(data: Any, max_depth: int = 3, current_depth: int = 0):
    """Helper function to print the structure of API responses."""
    
    if current_depth >= max_depth:
        print("  " * current_depth + "...")
        return
    
    if isinstance(data, dict):
        for key, value in data.items():
            value_type = type(value).__name__
            if isinstance(value, (dict, list)) and value:
                print("  " * current_depth + f"{key}: {value_type}")
                print_api_response_structure(value, max_depth, current_depth + 1)
            else:
                sample = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print("  " * current_depth + f"{key}: {value_type} = {sample}")
    
    elif isinstance(data, list) and data:
        print("  " * current_depth + f"[{len(data)} items]")
        if data:
            print("  " * current_depth + "Sample item:")
            print_api_response_structure(data[0], max_depth, current_depth + 1)

if __name__ == "__main__":
    test_roofmaxx_connect_service() 