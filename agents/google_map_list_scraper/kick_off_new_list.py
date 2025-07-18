#!/usr/bin/env python3
"""
Quick script to kick off the workflow for a new Google Maps list.
Just update the URL below and run this script.
"""

import sys
import os
import subprocess
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def kick_off_new_list(google_maps_url: str, list_name: str = None):
    """
    Kick off the complete workflow for a new Google Maps list.
    
    Args:
        google_maps_url: The Google Maps list URL to scrape
        list_name: Optional name for the list (used in logging)
    """
    
    print("🚀 Starting workflow for new Google Maps list...")
    print(f"📍 URL: {google_maps_url}")
    if list_name:
        print(f"🏷️  List Name: {list_name}")
    print("-" * 50)
    
    try:
        # Step 1: Update the scraper URL
        print("📝 Step 1: Updating scraper configuration...")
        update_scraper_url(google_maps_url)
        
        # Step 2: Run the scraper
        print("🔍 Step 2: Running Google Maps scraper...")
        run_scraper()
        
        # Step 3: Format data for Clay
        print("📊 Step 3: Formatting data for Clay...")
        format_for_clay()
        
        # Step 4: Upload to GitHub Gist
        print("☁️  Step 4: Uploading to GitHub Gist...")
        upload_to_gist()
        
        # Step 5: Trigger Zapier (optional - it runs every hour automatically)
        print("⚡ Step 5: Triggering Zapier workflow...")
        trigger_zapier()
        
        print("\n✅ Workflow completed successfully!")
        print("🔔 Check your Clay table for the imported addresses")
        print("⏰ If manual trigger doesn't work, Zapier runs automatically every hour")
        
    except Exception as e:
        print(f"\n❌ Error in workflow: {str(e)}")
        print("📝 Check the logs above for more details")

def update_scraper_url(new_url: str):
    """Update the URL in run_scraper.py"""
    scraper_file = "run_scraper.py"
    
    # Read current content
    with open(scraper_file, 'r') as f:
        content = f.read()
    
    # Replace the URL line (handle both shortened and full URLs)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'list_url = "https://' in line and ('google.com/maps' in line or 'maps.app.goo.gl' in line):
            lines[i] = f'    list_url = "{new_url}"'
            break
    
    # Write back
    with open(scraper_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Updated scraper URL")

def run_scraper():
    """Run the Google Maps scraper"""
    result = subprocess.run([sys.executable, "run_scraper.py"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Scraper completed successfully")
        # Count addresses found
        try:
            import pandas as pd
            df = pd.read_csv("data/addresses.csv")
            print(f"📊 Found {len(df)} addresses")
        except:
            print("📊 Addresses scraped (count unavailable)")
    else:
        print(f"❌ Scraper failed: {result.stderr}")
        raise Exception("Scraper failed")

def format_for_clay():
    """Format addresses for Clay import"""
    try:
        from scripts.prepare_clay_csv import prepare_addresses_for_clay
        prepare_addresses_for_clay()
        print("✅ Data formatted for Clay")
    except ImportError:
        # Manual formatting if script doesn't exist
        print("📝 Manual formatting - creating addresses_for_clay.csv")
        import pandas as pd
        from datetime import datetime
        
        # Read scraped addresses
        df = pd.read_csv("data/addresses.csv")
        
        # Format for Clay
        formatted_data = []
        for _, row in df.iterrows():
            address = row['address']
            # Parse address parts (basic parsing)
            parts = address.split(', ')
            if len(parts) >= 3:
                street = parts[0]
                city = parts[1]
                state_zip = parts[2].split(' ')
                state = state_zip[0] if len(state_zip) > 0 else ''
                zip_code = state_zip[1] if len(state_zip) > 1 else ''
                
                formatted_data.append({
                    'name': row.get('name', ''),
                    'address': address,
                    'street_address': street,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code,
                    'full_address': address,
                    'source': 'Google Maps List Scraper',
                    'import_date': datetime.now().strftime('%Y-%m-%d'),
                    'import_time': datetime.now().strftime('%H:%M:%S')
                })
        
        # Save formatted data
        clay_df = pd.DataFrame(formatted_data)
        clay_df.to_csv("data/addresses_for_clay.csv", index=False)
        print(f"✅ Formatted {len(clay_df)} addresses for Clay")

def upload_to_gist():
    """Upload CSV to GitHub Gist"""
    result = subprocess.run([sys.executable, "update_gist.py"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Uploaded to GitHub Gist")
        print("🔗 Gist updated with new addresses")
    else:
        print(f"❌ Gist upload failed: {result.stderr}")
        print("⚠️  You may need to run 'python3 update_gist.py' manually")

def trigger_zapier():
    """Trigger Zapier webhook (optional)"""
    try:
        result = subprocess.run([sys.executable, "trigger_zap.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Zapier webhook triggered")
        else:
            print("⚠️  Zapier manual trigger failed (that's OK - it runs every hour)")
    except:
        print("⚠️  Zapier manual trigger unavailable (that's OK - it runs every hour)")

def main():
    """Main function - Update the Google Maps URL here!"""
    
    # 🔥 CHANGE THIS URL FOR YOUR NEW GOOGLE MAPS LIST 🔥
    new_google_maps_url = "https://www.google.com/maps/@38.9013081,-94.4328395,1779m/data=!3m1!1e3!4m6!1m2!10m1!1e1!11m2!2s0CZ2l33STKGzwfM2FE_Ayg!3e3?authuser=1&entry=ttu&g_ep=EgoyMDI1MDcwOS4wIKXMDSoASAFQAw%3D%3D"
    
    # Optional: Give your list a name for tracking
    list_name = "Correct Google Maps List - Kansas City Area"
    
    # Validation
    valid_prefixes = ["https://www.google.com/maps/", "https://maps.app.goo.gl/", "https://goo.gl/maps/"]
    if not any(new_google_maps_url.startswith(prefix) for prefix in valid_prefixes):
        print("❌ Error: Please provide a valid Google Maps URL")
        print("📝 Supported formats: https://www.google.com/maps/... or https://maps.app.goo.gl/...")
        return
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run the workflow
    kick_off_new_list(new_google_maps_url, list_name)

if __name__ == "__main__":
    main() 