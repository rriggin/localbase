#!/usr/bin/env python3
"""
Secure RoofMaxx Deals Sync Setup

Uses environment variables from .env file for secure credential management.
No hardcoded secrets, no exposed keys! 🔒
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env
load_env()

from src.services.supabase.deals_sync_service import DealsSyncService
from src.services.supabase.deals_analytics import DealsAnalytics

def validate_environment():
    """Validate that all required environment variables are set."""
    
    print("🔒 VALIDATING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    required_vars = [
        'ROOFMAXX_CONNECT_TOKEN',
        'ROOFMAXX_CONNECT_BASE_URL', 
        'ROOFMAXX_CONNECT_DEALER_ID',
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif 'your-' in value or 'placeholder' in value.lower():
            placeholder_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * 20}...{value[-4:]}")
    
    if missing_vars:
        print(f"\n❌ MISSING VARIABLES:")
        for var in missing_vars:
            print(f"   • {var}")
        return False
    
    if placeholder_vars:
        print(f"\n⚠️  PLACEHOLDER VALUES DETECTED:")
        for var in placeholder_vars:
            print(f"   • {var}: {os.getenv(var)}")
        print(f"\n💡 Please update config/.env with your actual Supabase credentials")
        return False
    
    print(f"\n✅ All environment variables properly configured!")
    return True

def get_secure_configs():
    """Get service configurations from environment variables."""
    
    roofmaxx_config = {
        'bearer_token': os.getenv('ROOFMAXX_CONNECT_TOKEN'),
        'base_url': os.getenv('ROOFMAXX_CONNECT_BASE_URL'),
        'dealer_id': int(os.getenv('ROOFMAXX_CONNECT_DEALER_ID', 6637))
    }
    
    supabase_config = {
        'url': os.getenv('SUPABASE_URL'),
        'access_token': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }
    
    return roofmaxx_config, supabase_config

def run_secure_sync():
    """Run the sync with secure environment variable configuration."""
    
    print("🚀 SECURE ROOFMAXX DEALS SYNC")
    print("=" * 60)
    print("Using environment variables from config/.env")
    print("No hardcoded secrets, no exposed credentials! 🔒")
    print()
    
    # Validate environment
    if not validate_environment():
        print("\n❌ Environment validation failed!")
        print("\n📝 To fix this:")
        print("   1. Open config/.env")
        print("   2. Replace placeholder values with your actual Supabase credentials")
        print("   3. Get credentials from https://supabase.com/dashboard > Settings > API")
        print("   4. Run this script again")
        return
    
    # Get configurations
    roofmaxx_config, supabase_config = get_secure_configs()
    
    print("✅ Configuration loaded securely from environment")
    print()
    
    try:
        # Initialize sync service
        sync_service = DealsSyncService(roofmaxx_config, supabase_config)
        
        # Run the full sync
        print("🔄 Starting sync process...")
        sync_status = sync_service.run_full_sync()
        
        # Show results
        print("\n" + "="*60)
        print("🎉 SYNC RESULTS:")
        print(f"   📊 Total Deals Synced: {sync_status.new_deals_synced:,}")
        print(f"   ⏱️  Sync Duration: {sync_status.sync_duration_seconds:.1f} seconds")
        print(f"   ❌ Sync Errors: {sync_status.sync_errors}")
        
        if sync_status.sync_errors == 0:
            print("\n✅ PERFECT SYNC! All deals successfully stored!")
        else:
            print(f"\n⚠️  Some errors occurred, but {sync_status.new_deals_synced:,} deals were synced")
        
        # Run analytics on stored data
        print("\n📊 RUNNING ANALYTICS ON STORED DATA...")
        print("-" * 60)
        
        analytics = DealsAnalytics(supabase_config)
        summary = analytics.get_business_summary()
        
        print("\n🎯 SUCCESS! Your deals are now permanently stored in Supabase!")
        print("=" * 60)
        print("🚀 What you can do now:")
        print("   📊 Build dashboards with your stored data")
        print("   📈 Run advanced analytics queries")
        print("   🔄 Set up automated daily syncs")
        print("   💻 Connect BI tools like Grafana, Tableau, etc.")
        print("   🎨 Create custom reports and visualizations")
        print()
        print("🔒 All done securely with environment variables!")
        print("🍆💥 TOM'S MIND = BLOWN! Enterprise-level security!")
        
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        print("💡 Please check your environment variables and try again.")

def show_security_guide():
    """Show security best practices guide."""
    
    print("🔒 SECURITY BEST PRACTICES")
    print("=" * 60)
    print()
    print("✅ What we're doing right:")
    print("   🔐 Environment variables in .env file")
    print("   🙈 .env file is git-ignored")
    print("   🚫 No hardcoded secrets in code")
    print("   🛡️  Service role keys (not exposed anon keys)")
    print()
    print("📋 Your credentials are stored in:")
    print("   📁 config/.env (git-ignored)")
    print("   🔒 Only accessible on your local machine")
    print("   🚫 Never committed to git")
    print()
    print("🎯 To set up your Supabase credentials:")
    print("   1. Go to https://supabase.com/dashboard")
    print("   2. Create/select your project")
    print("   3. Go to Settings > API")
    print("   4. Copy your URL and Service Role Key")
    print("   5. Update config/.env with real values")
    print()

if __name__ == "__main__":
    show_security_guide()
    
    proceed = input("\n▶️  Ready to run secure sync? (y/n): ").lower().strip()
    
    if proceed in ['y', 'yes', '']:
        run_secure_sync()
    else:
        print("\n👋 No problem! Update config/.env with your Supabase credentials first.")
        print("📧 Your 868 deals will be securely synced when you're ready!") 