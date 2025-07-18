
#!/usr/bin/env python3
"""
Automated CSV to Clay Workflow
This script can be run on a schedule to automatically update your CSV
and trigger Zapier imports to Clay.com
"""

import os
import subprocess
import requests
from datetime import datetime

def run_scraper():
    """Run the Google Maps scraper"""
    print("🔄 Running Google Maps scraper...")
    subprocess.run(["python3", "run_scraper.py"])
    
def prepare_csv():
    """Prepare CSV for Clay import"""
    print("📋 Preparing CSV for Clay...")
    subprocess.run(["python3", "clay_integration.py"])
    
def upload_to_public_url():
    """Upload CSV to public URL"""
    print("📤 Uploading to public URL...")
    # Add your upload logic here
    # This could be Google Drive API, GitHub API, etc.
    
def trigger_zapier_webhook():
    """Trigger Zapier webhook for import"""
    webhook_url = os.getenv("ZAPIER_WEBHOOK_URL")
    if webhook_url:
        print("🔗 Triggering Zapier webhook...")
        payload = {
            "timestamp": datetime.now().isoformat(),
            "action": "import_to_clay",
            "csv_url": "YOUR_CSV_URL_HERE"
        }
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✅ Webhook triggered successfully")
        else:
            print(f"❌ Webhook failed: {response.status_code}")
    
def main():
    """Main workflow"""
    print("🚀 Starting automated CSV to Clay workflow...")
    
    # Step 1: Run scraper
    run_scraper()
    
    # Step 2: Prepare CSV
    prepare_csv()
    
    # Step 3: Upload to public URL
    upload_to_public_url()
    
    # Step 4: Trigger Zapier
    trigger_zapier_webhook()
    
    print("✅ Workflow completed!")

if __name__ == "__main__":
    main()
