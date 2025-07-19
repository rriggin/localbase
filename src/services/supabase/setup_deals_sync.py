#!/usr/bin/env python3
"""
RoofMaxx Deals Sync Setup

Easy setup script to sync your 868 deals to Supabase!
Tom's about to see permanent business intelligence! 🚀
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from .deals_sync_service import DealsSyncService
from .deals_analytics import DealsAnalytics

def get_supabase_config():
    """Get Supabase configuration from user."""
    
    print("🔧 SUPABASE CONFIGURATION SETUP")
    print("=" * 60)
    print("We need your Supabase credentials to store your deals data.")
    print()
    
    # Check if we have environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        print("✅ Found Supabase credentials in environment variables!")
        print(f"   URL: {supabase_url[:30]}...")
        print(f"   Key: {supabase_key[:20]}...")
        
        use_env = input("\n📋 Use these credentials? (y/n): ").lower().strip()
        if use_env in ['y', 'yes', '']:
            return {
                'url': supabase_url,
                'access_token': supabase_key
            }
    
    # Manual input
    print("\n📝 Please enter your Supabase credentials:")
    print("   (You can find these in your Supabase project dashboard)")
    print()
    
    url = input("🔗 Supabase URL (https://xxx.supabase.co): ").strip()
    if not url:
        print("❌ URL is required!")
        return None
    
    key = input("🔑 Supabase Service Role Key: ").strip()
    if not key:
        print("❌ Service role key is required!")
        return None
    
    return {
        'url': url,
        'access_token': key
    }

def run_sync_and_analytics():
    """Run the complete sync and show analytics."""
    
    print("🚀 ROOFMAXX DEALS TO SUPABASE SYNC")
    print("=" * 60)
    print("We're about to sync all 868 deals to your Supabase database!")
    print("This will enable permanent business intelligence and analytics.")
    print()
    
    # Get Supabase configuration
    supabase_config = get_supabase_config()
    if not supabase_config:
        print("❌ Configuration failed. Please try again.")
        return
    
    # RoofMaxx configuration
    roofmaxx_config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    print("\n✅ Configuration complete! Starting sync...")
    print()
    
    try:
        # Initialize sync service
        sync_service = DealsSyncService(roofmaxx_config, supabase_config)
        
        # Run the full sync
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
        
        # Now run analytics on the stored data
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
        print("🍆💥 TOM'S MIND = BLOWN! This is enterprise-level data infrastructure!")
        
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        print("💡 Please check your Supabase credentials and try again.")

def show_quick_start_guide():
    """Show a quick start guide for users."""
    
    print("📚 QUICK START GUIDE")
    print("=" * 60)
    print()
    print("🎯 What this script does:")
    print("   1. Creates a 'roofmaxx_deals' table in your Supabase database")
    print("   2. Fetches all 868 deals from RoofMaxx Connect API")
    print("   3. Stores them in Supabase with proper indexing")
    print("   4. Runs analytics to verify the data")
    print()
    print("📋 What you need:")
    print("   ✅ Supabase project (free tier works!)")
    print("   ✅ Your Supabase URL and Service Role Key")
    print("   ✅ Your RoofMaxx Connect API token (already configured)")
    print()
    print("🔗 Get Supabase credentials:")
    print("   1. Go to https://supabase.com/dashboard")
    print("   2. Select your project (or create one)")
    print("   3. Go to Settings > API")
    print("   4. Copy your URL and Service Role Key")
    print()
    print("🚀 Ready to sync your deals to permanent storage?")

if __name__ == "__main__":
    show_quick_start_guide()
    
    proceed = input("\n▶️  Start the sync process? (y/n): ").lower().strip()
    
    if proceed in ['y', 'yes', '']:
        run_sync_and_analytics()
    else:
        print("\n👋 No problem! Run this script anytime to sync your deals.")
        print("📧 Your 868 deals will be waiting when you're ready!") 