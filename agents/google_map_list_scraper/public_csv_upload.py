#!/usr/bin/env python3
"""
Public CSV Upload for Zapier Integration
Upload CSV to a public URL that Zapier can monitor for changes.
"""

import os
import requests
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PublicCSVUploader:
    """Upload CSV to public URL for Zapier monitoring"""
    
    def __init__(self):
        self.csv_path = "data/addresses_for_clay.csv"
        self.public_url = None
        
    def upload_to_github_gist(self, csv_content: str, filename: str = "addresses.csv") -> Optional[str]:
        """Upload CSV to GitHub Gist for public access"""
        try:
            # GitHub Gist API endpoint
            url = "https://api.github.com/gists"
            
            # Create gist with CSV content
            payload = {
                "description": f"Canvassing Data - Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "public": True,
                "files": {
                    filename: {
                        "content": csv_content
                    }
                }
            }
            
            # Note: This requires a GitHub token for authenticated requests
            # For now, we'll provide instructions for manual upload
            print("📝 GitHub Gist Upload Instructions:")
            print("1. Go to https://gist.github.com")
            print("2. Create a new gist")
            print("3. Name it 'addresses.csv'")
            print("4. Paste the CSV content")
            print("5. Make it public")
            print("6. Copy the raw URL")
            
            return None
            
        except Exception as e:
            print(f"❌ Error uploading to GitHub Gist: {e}")
            return None
    
    def upload_to_google_drive(self) -> Optional[str]:
        """Upload CSV to Google Drive for public access"""
        print("📝 Google Drive Upload Instructions:")
        print("1. Go to https://drive.google.com")
        print("2. Upload the CSV file")
        print("3. Right-click → Share → Copy link")
        print("4. Make sure it's set to 'Anyone with link can view'")
        
        return None
    
    def create_webhook_endpoint(self) -> str:
        """Create a simple webhook endpoint for CSV updates"""
        print("🔧 Webhook Setup Instructions:")
        print("1. Use a service like webhook.site or ngrok")
        print("2. Set up a webhook endpoint")
        print("3. Configure Zapier to monitor the webhook")
        
        return "https://webhook.site/your-unique-url"
    
    def create_zapier_setup_guide(self, csv_url: str = None):
        """Create comprehensive Zapier setup guide"""
        
        guide = f"""
# Zapier CSV to Clay.com Integration Guide

## Overview
This guide shows how to automatically import CSV data to Clay.com using Zapier.

## Step 1: Public CSV Setup

### Option A: Google Drive (Recommended)
1. Upload your CSV to Google Drive
2. Right-click → Share → Copy link
3. Set permissions to "Anyone with link can view"
4. Your CSV URL will be: https://drive.google.com/file/d/YOUR_FILE_ID/view

### Option B: GitHub Gist
1. Go to https://gist.github.com
2. Create new gist with your CSV content
3. Make it public
4. Copy the raw URL: https://gist.githubusercontent.com/USERNAME/GIST_ID/raw/filename.csv

### Option C: Dropbox
1. Upload CSV to Dropbox
2. Right-click → Share → Copy link
3. Replace '?dl=0' with '?dl=1' for direct download

## Step 2: Zapier Zap Setup

### Trigger: Google Drive (Recommended)
1. **App**: Google Drive
2. **Event**: New File in Folder
3. **Folder**: Choose your CSV folder
4. **File Types**: CSV files only

### Alternative Trigger: Webhook
1. **App**: Webhooks by Zapier
2. **Event**: Catch Hook
3. **URL**: Your webhook URL
4. **Method**: POST

### Action: Clay.com Import
1. **App**: Clay.com (if available)
2. **Event**: Create Record
3. **Table**: Canvassing Data
4. **Field Mapping**: Map CSV columns to Clay fields

### Alternative Action: Manual Import
If Clay.com doesn't have a Zapier action:
1. **App**: Email by Zapier
2. **Event**: Send Email
3. **To**: Your email
4. **Subject**: "New CSV Data Ready for Clay Import"
5. **Body**: Include CSV URL and instructions

## Step 3: CSV Monitoring Setup

### File Change Detection
1. Set up a scheduled Zap (every 15 minutes)
2. Check if CSV file has been modified
3. Trigger import if changes detected

### Data Validation
1. Add a filter step to validate CSV format
2. Check for required columns
3. Validate data types

## Step 4: Testing

### Test the Integration
1. Upload a new CSV file
2. Verify Zapier detects the change
3. Check that Clay.com receives the data
4. Monitor for any errors

### Error Handling
1. Set up error notifications
2. Log failed imports
3. Retry mechanism for failed uploads

## Step 5: Automation

### Scheduled Updates
1. Run scraper on schedule
2. Upload new CSV automatically
3. Trigger Zapier import
4. Send confirmation email

### Data Sync
1. Keep track of imported records
2. Avoid duplicate imports
3. Update existing records if needed

## Troubleshooting

### Common Issues
1. **CSV not accessible**: Check file permissions
2. **Zapier not triggering**: Verify trigger settings
3. **Clay import failing**: Check field mappings
4. **Duplicate records**: Implement deduplication logic

### Debug Steps
1. Check Zapier task history
2. Verify CSV format and content
3. Test webhook endpoints
4. Monitor error logs

## CSV Format Requirements

Your CSV should have these columns:
- name
- address
- street_address
- city
- state
- zip_code
- full_address
- source
- import_date
- import_time

## Next Steps

1. Choose your public CSV hosting method
2. Set up the Zapier Zap
3. Test the integration
4. Monitor and optimize

For help with specific steps, refer to the individual setup guides below.
"""
        
        with open("ZAPIER_CSV_TO_CLAY_GUIDE.md", "w") as f:
            f.write(guide)
        
        print("✅ Created comprehensive Zapier guide: ZAPIER_CSV_TO_CLAY_GUIDE.md")
    
    def create_automated_workflow(self):
        """Create an automated workflow script"""
        
        workflow = f"""
#!/usr/bin/env python3
\"\"\"
Automated CSV to Clay Workflow
This script can be run on a schedule to automatically update your CSV
and trigger Zapier imports to Clay.com
\"\"\"

import os
import subprocess
import requests
from datetime import datetime

def run_scraper():
    \"\"\"Run the Google Maps scraper\"\"\"
    print("🔄 Running Google Maps scraper...")
    subprocess.run(["python3", "run_scraper.py"])
    
def prepare_csv():
    \"\"\"Prepare CSV for Clay import\"\"\"
    print("📋 Preparing CSV for Clay...")
    subprocess.run(["python3", "clay_integration.py"])
    
def upload_to_public_url():
    \"\"\"Upload CSV to public URL\"\"\"
    print("📤 Uploading to public URL...")
    # Add your upload logic here
    # This could be Google Drive API, GitHub API, etc.
    
def trigger_zapier_webhook():
    \"\"\"Trigger Zapier webhook for import\"\"\"
    webhook_url = os.getenv("ZAPIER_WEBHOOK_URL")
    if webhook_url:
        print("🔗 Triggering Zapier webhook...")
        payload = {{
            "timestamp": datetime.now().isoformat(),
            "action": "import_to_clay",
            "csv_url": "YOUR_CSV_URL_HERE"
        }}
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✅ Webhook triggered successfully")
        else:
            print(f"❌ Webhook failed: {{response.status_code}}")
    
def main():
    \"\"\"Main workflow\"\"\"
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
"""
        
        with open("automated_workflow.py", "w") as f:
            f.write(workflow)
        
        print("✅ Created automated workflow script: automated_workflow.py")
    
    def main(self):
        """Main function to set up public CSV and Zapier integration"""
        print("🚀 Public CSV Upload for Zapier Integration")
        print("=" * 50)
        
        # Check if CSV exists
        if not os.path.exists(self.csv_path):
            print(f"❌ CSV file not found: {self.csv_path}")
            print("   Please run clay_integration.py first to prepare the CSV")
            return
        
        # Read CSV content
        with open(self.csv_path, 'r') as f:
            csv_content = f.read()
        
        print(f"📊 CSV file ready: {self.csv_path}")
        print(f"   Records: {len(csv_content.splitlines()) - 1}")  # Subtract header
        
        # Show upload options
        print(f"\n📤 Upload Options:")
        print(f"1. Google Drive (Recommended)")
        print(f"2. GitHub Gist")
        print(f"3. Dropbox")
        print(f"4. Webhook endpoint")
        
        # Create guides
        print(f"\n📋 Creating setup guides...")
        self.create_zapier_setup_guide()
        self.create_automated_workflow()
        
        print(f"\n🎉 Setup complete!")
        print(f"   Next steps:")
        print(f"   1. Choose your public CSV hosting method")
        print(f"   2. Upload {self.csv_path} to your chosen platform")
        print(f"   3. Follow ZAPIER_CSV_TO_CLAY_GUIDE.md for Zapier setup")
        print(f"   4. Test the integration")
        print(f"   5. Set up automated_workflow.py for recurring updates")

if __name__ == "__main__":
    uploader = PublicCSVUploader()
    uploader.main() 