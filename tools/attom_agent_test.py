#!/usr/bin/env python3
"""
ATTOM Property Agent Test

Tests the new professional ATTOM Property Agent with dependency injection
and service layers.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.services.attom import AttomPropertyAgent


def main():
    print("🧪 ATTOM Property Agent Architecture Test")
    print("This tests the new professional ATTOM Property Agent")
    print("with dependency injection and service layers.")
    print()
    
    # Check configuration
    print("🔍 Configuration Check:")
    print(f"  • Airtable configured: {config.airtable_token is not None}")
    print(f"  • ATTOM API configured: {config.attom_api_key is not None}")
    print(f"  • Config loaded: {config is not None}")
    print()
    
    if not config.attom_api_key:
        print("❌ ATTOM_API_KEY not found in environment variables")
        print("   Please add ATTOM_API_KEY to your .env file")
        print("   Sign up at https://api.developer.attomdata.com/home")
        return
    
    # Initialize services
    print("🚀 Testing ATTOM Property Agent (Professional Architecture)")
    print("=" * 60)
    print("📋 Initializing services...")
    
    try:
        # Get agent config
        agent_config = config.get_agent_config("attom_property_enrichment")
        print("🤖 Creating ATTOM Property Agent...")
        
        # Initialize services for agent
        services = config.initialize_services_for_agent("attom_property_enrichment")
        
        # Create agent
        agent = AttomPropertyAgent(agent_config, services)
        
        print(f"✅ Agent Status: {agent.get_status()}")
        print(f"📊 Version: {agent.VERSION}")
        print(f"🔧 Services: {list(agent.services.keys())}")
        print()
        
        # Test with sample addresses
        print("🎯 Testing with sample Missouri addresses...")
        print("📍 Sample addresses from Sedalia, MO")
        print("⚠️  Testing with 2 addresses only (API rate limits)...")
        print("⚠️  Will NOT save to Airtable for safety...")
        
        test_addresses = [
            "1234 Country Club Dr, Sedalia, MO, 65301",
            "5678 Fairway Dr, Sedalia, MO, 65301"
        ]
        
        result = agent.execute(
            addresses=test_addresses,
            save_to_airtable=False,  # Don't save during test
            business_name="ATTOM Test Data"
        )
        
        print("\n📊 Results:")
        print(f"✅ Success: {result.get('success', False)}")
        
        data = result.get('data', {})
        print(f"📍 Total addresses processed: {data.get('total_addresses', 0)}")
        print(f"✅ Successful enrichments: {data.get('successful_enrichments', 0)}")
        print(f"❌ Failed enrichments: {data.get('failed_enrichments', 0)}")
        print(f"💾 Saved to Airtable: {data.get('save_to_airtable', False)}")
        print()
        
        # Show sample enriched data if available
        enriched_records = data.get('enriched_records', [])
        if enriched_records:
            print("📋 Sample enriched data:")
            sample = enriched_records[0]['fields']
            for key, value in list(sample.items())[:10]:  # Show first 10 fields
                if value is not None:
                    print(f"  • {key}: {value}")
            if len(sample) > 10:
                print(f"     ... and {len(sample) - 10} more fields")
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 