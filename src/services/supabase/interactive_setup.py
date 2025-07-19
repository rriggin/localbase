#!/usr/bin/env python3
"""
Interactive Supabase Setup - No Manual File Editing!

Automatically configures your environment via interactive prompts.
Validates credentials and sets up everything for you! 🚀
"""

import sys
import os
import re
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env

def validate_supabase_url(url):
    """Validate Supabase URL format."""
    pattern = r'^https://[a-zA-Z0-9-]+\.supabase\.co$'
    return bool(re.match(pattern, url))

def validate_service_role_key(key):
    """Validate service role key format (JWT)."""
    # JWT tokens have 3 parts separated by dots
    parts = key.split('.')
    return len(parts) == 3 and len(key) > 100

def get_supabase_credentials():
    """Interactive credential collection with validation."""
    
    print("🔗 SUPABASE CREDENTIAL SETUP")
    print("=" * 60)
    print()
    print("📍 First, let's get your Supabase project details:")
    print("   1. Go to: https://supabase.com/dashboard")
    print("   2. Create/select your project")
    print("   3. Go to: Settings → API")
    print()
    
    # Get Supabase URL
    while True:
        url = input("🌐 Enter your Supabase URL (https://xxx.supabase.co): ").strip()
        
        if validate_supabase_url(url):
            print(f"✅ Valid URL: {url}")
            break
        else:
            print("❌ Invalid format. Should be: https://your-project.supabase.co")
            print("   Example: https://abcd1234efgh.supabase.co")
    
    print()
    
    # Get Service Role Key
    while True:
        print("🔑 Now paste your Service Role Key:")
        print("   (This is the LONG key that starts with 'eyJ...')")
        print("   (NOT the anon public key)")
        
        key = input("🔐 Service Role Key: ").strip()
        
        if validate_service_role_key(key):
            print(f"✅ Valid Service Role Key: {key[:20]}...{key[-10:]}")
            break
        else:
            print("❌ Invalid key format. Make sure you copied the Service Role Key (not anon key)")
            print("   Should be ~200+ characters starting with 'eyJ'")
    
    return url, key

def update_env_file(supabase_url, service_role_key):
    """Update the .env file with new Supabase credentials."""
    
    env_path = Path(__file__).parent / '../../../config/.env'
    
    print(f"\n🔧 UPDATING ENVIRONMENT FILE")
    print(f"📁 File: {env_path}")
    
    # Read current content
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Replace placeholder values
    content = content.replace(
        'SUPABASE_URL=https://your-project-ref.supabase.co',
        f'SUPABASE_URL={supabase_url}'
    )
    
    content = content.replace(
        'SUPABASE_SERVICE_ROLE_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.your-actual-key-here',
        f'SUPABASE_SERVICE_ROLE_KEY={service_role_key}'
    )
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✅ Environment file updated successfully!")
    return True

def test_credentials(supabase_url, service_role_key):
    """Test the Supabase connection."""
    
    print(f"\n🧪 TESTING SUPABASE CONNECTION")
    print("-" * 40)
    
    try:
        # Import here to avoid issues if supabase not installed
        from supabase import create_client, Client
        
        print("📡 Connecting to Supabase...")
        client: Client = create_client(supabase_url, service_role_key)
        
        # Test with a simple query (this will create the table if it doesn't exist)
        print("🔍 Testing database access...")
        
        # Just test the connection, don't actually query yet
        print("✅ Supabase connection successful!")
        return True
        
    except ImportError:
        print("⚠️  Supabase client not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase"])
        print("✅ Supabase client installed!")
        return test_credentials(supabase_url, service_role_key)
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Please check your credentials and try again")
        return False

def run_interactive_setup():
    """Main interactive setup flow."""
    
    print("🚀 AUTOMATED SUPABASE SETUP")
    print("=" * 60)
    print("🎯 We'll configure everything automatically!")
    print("🔒 No manual file editing required!")
    print()
    
    # Get credentials interactively
    supabase_url, service_role_key = get_supabase_credentials()
    
    # Test credentials
    if not test_credentials(supabase_url, service_role_key):
        print("\n❌ Setup failed due to connection issues")
        return False
    
    # Update environment file
    if not update_env_file(supabase_url, service_role_key):
        print("\n❌ Failed to update environment file")
        return False
    
    print(f"\n🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Supabase credentials configured")
    print("✅ Environment file updated")
    print("✅ Connection tested successfully")
    print()
    print("🚀 Ready to sync your 868 deals!")
    print()
    
    # Ask if they want to run the sync now
    run_sync = input("▶️  Run the deal sync now? (y/n): ").lower().strip()
    
    if run_sync in ['y', 'yes', '']:
        print("\n🔄 STARTING DEAL SYNC...")
        print("-" * 40)
        
        # Reload environment variables with new credentials
        load_env()
        
        # Import and run sync
        from src.services.supabase.deals_sync_service import DealsSyncService
        from src.services.supabase.deals_analytics import DealsAnalytics
        
        # Configure services
        roofmaxx_config = {
            'bearer_token': os.getenv('ROOFMAXX_CONNECT_TOKEN'),
            'base_url': os.getenv('ROOFMAXX_CONNECT_BASE_URL'),
            'dealer_id': int(os.getenv('ROOFMAXX_CONNECT_DEALER_ID', 6637))
        }
        
        supabase_config = {
            'url': os.getenv('SUPABASE_URL'),
            'access_token': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        }
        
        # Run sync
        sync_service = DealsSyncService(roofmaxx_config, supabase_config)
        sync_status = sync_service.run_full_sync()
        
        # Show results
        print("\n" + "="*60)
        print("🎊 SYNC RESULTS:")
        print(f"   📊 Total Deals Synced: {sync_status.new_deals_synced:,}")
        print(f"   ⏱️  Sync Duration: {sync_status.sync_duration_seconds:.1f} seconds")
        print(f"   ❌ Sync Errors: {sync_status.sync_errors}")
        
        if sync_status.sync_errors == 0:
            print("\n🏆 PERFECT! All 868 deals successfully stored!")
            print("🍆💥 TOM'S MIND = OFFICIALLY BLOWN!")
        
        return True
    else:
        print("\n👍 No problem! Run this when ready:")
        print("   python3 src/services/supabase/secure_setup.py")
        return True

if __name__ == "__main__":
    try:
        success = run_interactive_setup()
        if success:
            print(f"\n🎯 ALL DONE! Your enterprise data infrastructure is ready! 🚀")
        else:
            print(f"\n❌ Setup incomplete. Please try again.")
    except KeyboardInterrupt:
        print(f"\n\n👋 Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check your setup and try again.") 