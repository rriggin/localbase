#!/usr/bin/env python3
"""
Google Maps Agent Test Tool
Test the new professional GoogleMapsAgent with dependency injection.
"""

import sys
import os
from typing import Dict, Any

# Add parent directory to path for src imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from agents.canvassing_list_generator import GoogleMapsAgent

def test_google_maps_agent():
    """Test the GoogleMapsAgent with your known list."""
    
    print("🚀 Testing GoogleMapsAgent (Professional Architecture)")
    print("=" * 60)
    
    try:
        # Initialize services for the agent
        print("📋 Initializing services...")
        services = config.initialize_services_for_agent("google_maps_scraper")
        
        # Get agent configuration
        agent_config = config.get_agent_config("google_maps_scraper")
        
        # Create agent instance
        print("🤖 Creating GoogleMapsAgent...")
        agent = GoogleMapsAgent(config=agent_config, services=services)
        
        # Check agent status
        status = agent.get_status()
        print(f"✅ Agent Status: {status['status']}")
        print(f"📊 Version: {status['version']}")
        print(f"🔧 Services: {status['services']}")
        
        # Test with your known Google Maps list (Winterset-Longview)
        print("\n🎯 Testing with Winterset-Longview list...")
        
        # Note: Using a smaller test for safety - you can change this URL
        test_list_url = "https://maps.app.goo.gl/qr1Y6sFwU58MU4Sm7"  # Your known list
        
        print(f"📍 List URL: {test_list_url}")
        print("⚠️  Running in headless mode for safety...")
        print("⚠️  Will only extract first few addresses as test...")
        
        # Execute the agent (with safety limits)
        result = agent.execute(
            list_url=test_list_url,
            headless=True,  # Safe for testing
            timeout=30,     # Longer timeout for safety
            save_to_airtable=False,  # Don't save to Airtable during test
            business_name="Test Google Maps Import"
        )
        
        # Show results
        print("\n📊 Results:")
        print(f"✅ Success: {result['success']}")
        
        if result['success']:
            data = result['data']
            print(f"📍 Total addresses found: {data['total_count']}")
            print(f"🔗 List URL: {data['list_url']}")
            print(f"💾 Saved to Airtable: {data['saved_to_airtable']}")
            
            print("\n📋 Sample addresses:")
            for i, addr in enumerate(data['addresses'][:5], 1):  # Show first 5
                print(f"  {i}. {addr['address']}")
                if addr['name']:
                    print(f"     Name: {addr['name']}")
            
            if data['total_count'] > 5:
                print(f"     ... and {data['total_count'] - 5} more addresses")
                
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point."""
    print("🧪 GoogleMapsAgent Architecture Test")
    print("This tests the new professional GoogleMapsAgent")
    print("with dependency injection and service layers.\n")
    
    # Quick config check
    print("🔍 Configuration Check:")
    status = config.get_status()
    print(f"  • Airtable configured: {status['airtable_configured']}")
    print(f"  • Config loaded: {status['config_loaded']}")
    
    if not status['airtable_configured']:
        print("❌ Airtable not configured. Please set AIRTABLE_TOKEN in .env")
        return
    
    print()
    
    # Run the test
    test_google_maps_agent()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main() 