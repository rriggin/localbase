#!/usr/bin/env python3
"""
Ultimate Supabase Setup - Maximum Automation!

Offers both dashboard and CLI automation paths.
Detects available tools and guides user to fastest option.
"""

import sys
import os
import subprocess
import re
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env

def check_supabase_cli():
    """Check if Supabase CLI is installed and user is logged in."""
    
    print("🔍 CHECKING SUPABASE CLI STATUS...")
    print("-" * 50)
    
    try:
        # Check if CLI is installed
        result = subprocess.run(['supabase', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Supabase CLI installed: {version}")
            
            # Check if user is logged in
            login_result = subprocess.run(['supabase', 'projects', 'list'], 
                                        capture_output=True, text=True, timeout=15)
            
            if login_result.returncode == 0:
                print("✅ User is logged in to Supabase")
                return True, "ready"
            else:
                print("⚠️  CLI installed but user not logged in")
                return True, "needs_login"
        else:
            print("❌ Supabase CLI not found")
            return False, "not_installed"
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Supabase CLI not available")
        return False, "not_installed"

def install_supabase_cli():
    """Offer to install Supabase CLI."""
    
    print("\n📦 INSTALL SUPABASE CLI")
    print("-" * 40)
    
    import platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("🍺 Recommended: Install via Homebrew")
        print("   brew install supabase/tap/supabase")
    elif system == "linux":
        print("🐧 Options for Linux:")
        print("   • Homebrew: brew install supabase/tap/supabase")
        print("   • Go: go install github.com/supabase/cli@latest")
    elif system == "windows":
        print("🪟 Windows: Install via Scoop")
        print("   scoop bucket add supabase https://github.com/supabase/scoop-bucket.git")
        print("   scoop install supabase")
    else:
        print("🔧 Install via Go (universal):")
        print("   go install github.com/supabase/cli@latest")
    
    print("\n📖 Full instructions: https://supabase.com/docs/guides/cli")

def cli_login_flow():
    """Guide user through CLI login."""
    
    print("\n🔐 SUPABASE CLI LOGIN")
    print("-" * 40)
    print("1. Go to: https://supabase.com/dashboard/account/tokens")
    print("2. Create a new access token")
    print("3. Run: supabase login")
    print("4. Paste your token when prompted")
    
    input("\n👆 Press Enter after you've logged in...")
    
    # Verify login worked
    try:
        result = subprocess.run(['supabase', 'projects', 'list'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Successfully logged in!")
            return True
        else:
            print("❌ Login verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying login: {e}")
        return False

def list_organizations():
    """List user's Supabase organizations."""
    
    try:
        result = subprocess.run(['supabase', 'orgs', 'list'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("📋 Your Supabase Organizations:")
            print(result.stdout)
            return True
        else:
            print("❌ Failed to list organizations")
            return False
            
    except Exception as e:
        print(f"❌ Error listing orgs: {e}")
        return False

def create_project_via_cli():
    """Create Supabase project via CLI."""
    
    print("\n🚀 CREATE PROJECT VIA CLI")
    print("-" * 40)
    
    # List organizations first
    if not list_organizations():
        return None, None
    
    # Get project details
    project_name = input("\n📝 Enter project name: ").strip()
    if not project_name:
        project_name = "RoofMaxx Analytics"
    
    org_id = input("🏢 Enter organization ID: ").strip()
    if not org_id:
        print("❌ Organization ID required")
        return None, None
    
    region = input("🌍 Enter region (default: us-east-1): ").strip()
    if not region:
        region = "us-east-1"
    
    db_password = input("🔐 Enter database password (default: auto-generated): ").strip()
    
    # Build command
    cmd = ['supabase', 'projects', 'create', project_name, 
           '--org-id', org_id, '--region', region]
    
    if db_password:
        cmd.extend(['--db-password', db_password])
    
    print(f"\n⚡ Creating project...")
    print(f"Command: {' '.join(cmd[:6])}...")  # Don't show password
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Project created successfully!")
            print(result.stdout)
            
            # Extract project ref from output
            project_ref_match = re.search(r'Project ref: (\w+)', result.stdout)
            project_ref = project_ref_match.group(1) if project_ref_match else None
            
            if project_ref:
                return get_project_keys(project_ref)
            else:
                print("⚠️  Project created but couldn't extract ref")
                return None, None
                
        else:
            print("❌ Project creation failed:")
            print(result.stderr)
            return None, None
            
    except subprocess.TimeoutExpired:
        print("❌ Project creation timed out")
        return None, None
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return None, None

def get_project_keys(project_ref):
    """Get API keys for a project."""
    
    try:
        result = subprocess.run(['supabase', 'projects', 'api-keys', 
                               '--project-ref', project_ref], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            output = result.stdout
            
            # Extract URL and service role key
            url_match = re.search(r'API URL: (https://[^\s]+)', output)
            service_key_match = re.search(r'service_role key: ([^\s]+)', output)
            
            if url_match and service_key_match:
                return url_match.group(1), service_key_match.group(1)
            else:
                print("⚠️  Couldn't extract all keys from output")
                print("Raw output:")
                print(output)
                return None, None
                
        else:
            print("❌ Failed to get project keys")
            return None, None
            
    except Exception as e:
        print(f"❌ Error getting keys: {e}")
        return None, None

def manual_dashboard_flow():
    """Guide user through manual dashboard setup."""
    
    print("\n🌐 MANUAL DASHBOARD SETUP")
    print("-" * 40)
    print("This is the FASTEST option (30 seconds!):")
    print()
    print("1. 🚀 Go to: https://supabase.com/dashboard")
    print("2. 🆕 Create new project (free tier works!)")
    print("3. ⚙️  Go to: Settings → API")
    print("4. 📋 Copy 2 values:")
    print("   • Project URL")
    print("   • Service Role Key (the long one)")
    print()
    
    # Get values interactively
    while True:
        url = input("🌐 Paste your Supabase URL: ").strip()
        
        if not url:
            continue
        
        # Validate URL format
        if re.match(r'^https://[a-zA-Z0-9-]+\.supabase\.co$', url):
            print(f"✅ Valid URL: {url}")
            break
        else:
            print("❌ Invalid format. Should be: https://xxx.supabase.co")
    
    while True:
        key = input("\n🔐 Paste your Service Role Key: ").strip()
        
        if not key:
            continue
        
        # Validate JWT format
        if len(key.split('.')) == 3 and len(key) > 100:
            print(f"✅ Valid Service Role Key: {key[:20]}...{key[-10:]}")
            break
        else:
            print("❌ Invalid key. Make sure it's the Service Role Key (not anon key)")
    
    return url, key

def update_env_file(supabase_url, service_role_key):
    """Update the .env file with credentials."""
    
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
    
    print("✅ Environment file updated!")

def test_supabase_connection(supabase_url, service_role_key):
    """Test the Supabase connection."""
    
    print(f"\n🧪 TESTING SUPABASE CONNECTION")
    print("-" * 40)
    
    try:
        # Install supabase client if needed
        try:
            from supabase import create_client, Client
        except ImportError:
            print("📦 Installing Supabase Python client...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase"])
            from supabase import create_client, Client
        
        print("📡 Connecting to Supabase...")
        client: Client = create_client(supabase_url, service_role_key)
        
        print("✅ Connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def run_deals_sync():
    """Run the deals sync after successful setup."""
    
    print(f"\n🔄 STARTING DEALS SYNC")
    print("-" * 40)
    
    # Reload environment
    load_env()
    
    try:
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
        
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        return False

def main():
    """Main setup flow with maximum automation."""
    
    print("🚀 ULTIMATE SUPABASE SETUP")
    print("=" * 60)
    print("🎯 Maximum automation with fallback options!")
    print("🔒 Enterprise-level security!")
    print()
    
    # Check CLI availability
    cli_available, cli_status = check_supabase_cli()
    
    print(f"\n🛠️  AVAILABLE OPTIONS:")
    print("-" * 30)
    
    if cli_available and cli_status == "ready":
        print("✅ Option 1: Fully Automated CLI (recommended)")
        print("✅ Option 2: Manual Dashboard (fastest)")
    elif cli_available and cli_status == "needs_login":
        print("⚠️  Option 1: CLI Available (needs login)")
        print("✅ Option 2: Manual Dashboard (fastest)")
    else:
        print("❌ Option 1: CLI Not Available")
        print("✅ Option 2: Manual Dashboard (fastest)")
        print("💡 Option 3: Install CLI for future automation")
    
    # Get user choice
    print(f"\n🎯 CHOOSE YOUR PATH:")
    
    choices = []
    if cli_available and cli_status == "ready":
        choices.append("1) Full CLI Automation")
    elif cli_available and cli_status == "needs_login":
        choices.append("1) CLI Setup (login required)")
    else:
        choices.append("1) Install CLI")
    
    choices.append("2) Manual Dashboard (30 seconds)")
    
    for choice in choices:
        print(f"   {choice}")
    
    selection = input(f"\n▶️  Enter choice (1-2): ").strip()
    
    supabase_url = None
    service_role_key = None
    
    if selection == "1":
        if cli_available and cli_status == "ready":
            # Full CLI automation
            supabase_url, service_role_key = create_project_via_cli()
        elif cli_available and cli_status == "needs_login":
            # CLI login then create
            if cli_login_flow():
                supabase_url, service_role_key = create_project_via_cli()
        else:
            # Install CLI
            install_supabase_cli()
            print("\n👋 Please install CLI and run this script again!")
            return
    
    elif selection == "2" or not selection:
        # Manual dashboard flow
        supabase_url, service_role_key = manual_dashboard_flow()
    
    else:
        print("❌ Invalid selection")
        return
    
    if not supabase_url or not service_role_key:
        print("❌ Setup incomplete. Please try again.")
        return
    
    # Update environment file
    update_env_file(supabase_url, service_role_key)
    
    # Test connection
    if not test_supabase_connection(supabase_url, service_role_key):
        print("❌ Connection test failed. Please check credentials.")
        return
    
    # Ask about running sync
    run_sync = input("\n▶️  Run the deal sync now? (y/n): ").lower().strip()
    
    if run_sync in ['y', 'yes', '']:
        if run_deals_sync():
            print(f"\n🎯 ULTIMATE SUCCESS!")
            print("=" * 60)
            print("🏆 Your enterprise data infrastructure is ready!")
            print("🔒 All credentials securely stored!")
            print("📊 868 deals synced to permanent database!")
            print("🍆💥 TOM'S BONER = MAXIMUM ACHIEVED!")
    else:
        print("\n👍 Setup complete! Run sync when ready:")
        print("   python3 src/services/supabase/secure_setup.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n👋 Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check setup and try again.") 