#!/usr/bin/env python3
"""
RoofMaxx Connect Service Demo

A demonstration of the RoofMaxx Connect service integration for Tom.
This shows how to use the service in agents and other parts of the system.
"""

import sys
import os
import json
from typing import Dict, Any, List

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.roofmaxxconnect.client import RoofmaxxConnectService
from src.services.roofmaxxconnect.config import get_roofmaxx_config
from src.services.roofmaxxconnect.models import DealerRecord
from src.services.roofmaxxconnect.exceptions import RoofmaxxError

def demo_roofmaxx_connect_service():
    """Demonstrate the RoofMaxx Connect service capabilities."""
    
    print("🏠 RoofMaxx Connect Service Demo for Tom")
    print("=" * 60)
    print("Demonstrating how to integrate RoofMaxx Connect into agents")
    print()
    
    try:
        # ===========================
        # 1. SERVICE INITIALIZATION
        # ===========================
        print("1️⃣  INITIALIZING SERVICE")
        print("-" * 30)
        
        # Configuration - in production this would come from environment variables
        config = {
            'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
            'base_url': 'https://roofmaxxconnect.com'
        }
        
        # Initialize service
        service = RoofmaxxConnectService(config)
        print("✅ Service initialized successfully")
        
        # Test authentication
        if service.authenticate():
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return
        
        print()
        
        # ===========================
        # 2. API STATISTICS
        # ===========================
        print("2️⃣  API OVERVIEW")
        print("-" * 30)
        
        stats = service.get_api_stats()
        print(f"📊 Total Dealers: {stats.get('total_dealers', 'Unknown'):,}")
        print(f"📄 Pages Available: {stats.get('total_pages', 'Unknown'):,}")
        print(f"🔢 Records per Page: {stats.get('dealers_per_page', 'Unknown')}")
        print(f"🔗 API Base URL: {stats.get('api_base_url')}")
        print()
        
        # ===========================
        # 3. GETTING DEALER DATA
        # ===========================
        print("3️⃣  FETCHING DEALER DATA")
        print("-" * 30)
        
        # Get first page of dealers
        print("📥 Fetching first page of dealers...")
        dealers_response = service.get_dealers(page=1, per_page=10)
        
        print(f"✅ Retrieved {len(dealers_response.data)} dealers from page {dealers_response.meta.current_page}")
        print(f"📈 Total available: {dealers_response.meta.total:,} dealers")
        print()
        
        # ===========================
        # 4. EXPLORING DEALER RECORDS
        # ===========================
        print("4️⃣  SAMPLE DEALER RECORDS")
        print("-" * 30)
        
        for i, dealer in enumerate(dealers_response.data[:3], 1):
            print(f"🏢 Dealer #{i}:")
            print(f"   ID: {dealer.id}")
            print(f"   Name: {dealer.name}")
            print(f"   Brand: {dealer.brand_name}")
            print(f"   HubSpot ID: {dealer.hubspot_company_id}")
            if dealer.microsite_url:
                print(f"   Website: {dealer.microsite_url}")
            print()
        
        # ===========================
        # 5. SEARCH FUNCTIONALITY
        # ===========================
        print("5️⃣  SEARCH CAPABILITIES")
        print("-" * 30)
        
        # Search for active dealers (non-retired)
        print("🔍 Searching for active dealers...")
        active_dealers = []
        retired_dealers = []
        
        for dealer in dealers_response.data:
            if dealer.name and "RETIRED" in dealer.name.upper():
                retired_dealers.append(dealer)
            else:
                active_dealers.append(dealer)
        
        print(f"✅ Found {len(active_dealers)} active dealers")
        print(f"🚫 Found {len(retired_dealers)} retired dealers")
        print()
        
        if active_dealers:
            print("🟢 Sample Active Dealers:")
            for dealer in active_dealers[:2]:
                print(f"   • {dealer.brand_name or dealer.name}")
        print()
        
        # ===========================
        # 6. PAGINATION EXAMPLE
        # ===========================
        print("6️⃣  PAGINATION DEMONSTRATION")
        print("-" * 30)
        
        print("📑 Fetching multiple pages...")
        total_dealers_fetched = 0
        
        for page in range(1, 4):  # Get first 3 pages
            page_response = service.get_dealers(page=page, per_page=5)
            total_dealers_fetched += len(page_response.data)
            print(f"   Page {page}: {len(page_response.data)} dealers")
        
        print(f"✅ Total dealers fetched: {total_dealers_fetched}")
        print()
        
        # ===========================
        # 7. AGENT INTEGRATION EXAMPLE
        # ===========================
        print("7️⃣  AGENT INTEGRATION EXAMPLE")
        print("-" * 30)
        
        print("🤖 This is how you'd use this service in an agent:")
        print()
        print("```python")
        print("# In your agent __init__ method:")
        print("self.roofmaxx_service = RoofmaxxConnectService(config)")
        print()
        print("# In your agent run method:")
        print("dealers = self.roofmaxx_service.get_dealers(per_page=50)")
        print("for dealer in dealers.data:")
        print("    # Process dealer data")
        print("    self.process_dealer(dealer)")
        print("```")
        print()
        
        # ===========================
        # 8. ERROR HANDLING DEMO
        # ===========================
        print("8️⃣  ERROR HANDLING")
        print("-" * 30)
        
        print("🛡️  Testing error handling...")
        try:
            # Try to access a non-existent dealer
            non_existent = service.get_dealer_by_id(999999)
            if non_existent is None:
                print("✅ Gracefully handled non-existent dealer (returned None)")
        except RoofmaxxError as e:
            print(f"✅ Caught and handled RoofmaxxError: {e}")
        
        print()
        
        # ===========================
        # 9. PERFORMANCE METRICS
        # ===========================
        print("9️⃣  PERFORMANCE METRICS")
        print("-" * 30)
        
        health = service.health_check()
        print(f"⚡ API Response Time: {health.get('response_time_seconds', 'Unknown'):.3f}s")
        print(f"🟢 Service Status: {health.get('status', 'Unknown').title()}")
        print(f"🔐 Authentication: {'✅ Valid' if health.get('authenticated') else '❌ Invalid'}")
        print()
        
        # ===========================
        # SUMMARY
        # ===========================
        print("🎯 DEMO SUMMARY")
        print("=" * 60)
        print("✅ Successfully demonstrated RoofMaxx Connect service")
        print("✅ Service follows BaseService architecture")
        print("✅ Proper error handling and type safety")
        print("✅ Pagination and search capabilities")
        print("✅ Ready for agent integration")
        print()
        print("🚀 Next Steps:")
        print("   1. Add service to environment variables")
        print("   2. Create agents that use this service")
        print("   3. Build workflows around dealer data")
        print("   4. Implement deal tracking (when dealer ID is available)")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

def demo_service_registry():
    """Demonstrate how the service fits into the service registry."""
    
    print("\n" + "=" * 60)
    print("🔧 SERVICE REGISTRY INTEGRATION")
    print("=" * 60)
    
    try:
        # Import the service registry
        from src.services import get_service, list_services
        
        print("📋 Available services in localbase:")
        services = list_services()
        for service_name in services:
            print(f"   • {service_name}")
        
        print(f"\n✅ Total services available: {len(services)}")
        
        # Show how to get the RoofMaxx Connect service
        if 'roofmaxxconnect' in services:
            print("\n🎯 Getting RoofMaxx Connect service from registry:")
            print("```python")
            print("from src.services import get_service")
            print("RoofmaxxService = get_service('roofmaxxconnect')")
            print("service = RoofmaxxService(config)")
            print("```")
        
    except Exception as e:
        print(f"⚠️  Service registry demo error: {e}")

if __name__ == "__main__":
    demo_roofmaxx_connect_service()
    demo_service_registry() 