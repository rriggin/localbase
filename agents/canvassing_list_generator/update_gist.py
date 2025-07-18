#!/usr/bin/env python3
"""
Update GitHub Gist with CSV Data
Update the existing GitHub Gist with fresh CSV data for Zapier integration.
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from main project directory
load_dotenv('../../.env')

# Your existing gist ID from the URL: https://gist.github.com/rriggin/1cb623ab465f4ebe6ddf3a934bacc5a7
GIST_ID = "1cb623ab465f4ebe6ddf3a934bacc5a7"

def update_github_gist():
    """Create a GitHub Gist with the CSV data"""
    
    # Check if GitHub token is available
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        print("❌ GITHUB_TOKEN not found in environment variables")
        print("   To create a GitHub Gist automatically, you need a GitHub token.")
        print("   Get one from: https://github.com/settings/tokens")
        print("   Add it to your .env file as: GITHUB_TOKEN=your_token_here")
        print("\n📝 Manual Gist Creation:")
        print("1. Go to https://gist.github.com")
        print("2. Create a new gist")
        print("3. Name it 'addresses.csv'")
        print("4. Paste the CSV content from data/addresses_formatted_for_gist.csv")
        print("5. Make it public")
        print("6. Copy the raw URL")
        return None
    
    # Read the CSV file
    csv_path = "data/addresses_formatted_for_gist.csv"
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return None
    
    with open(csv_path, 'r') as f:
        csv_content = f.read()
    
    # Update the existing gist
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "description": f"Canvassing Data - Winterset Longview, Lee's Summit MO - 1,020+ Addresses - Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "files": {
            "canvassing-data": {
                "content": csv_content
            }
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        gist_url = data["html_url"]
        raw_url = f"https://gist.githubusercontent.com/rriggin/{GIST_ID}/raw/canvassing-data"
        
        print("✅ GitHub Gist updated successfully!")
        print(f"   Gist URL: {gist_url}")
        print(f"   Raw CSV URL: {raw_url}")
        print(f"\n🔗 Your Zapier webhook should now receive this data")
        
        # Save the URL to a file for easy access
        with open("gist_url.txt", "w") as f:
            f.write(f"Gist URL: {gist_url}\n")
            f.write(f"Raw CSV URL: {raw_url}\n")
            f.write(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"   URL saved to: gist_url.txt")
        
        return raw_url
        
    except Exception as e:
        print(f"❌ Error creating GitHub Gist: {e}")
        if response.status_code == 401:
            print("   Authentication failed. Check your GitHub token.")
        elif response.status_code == 403:
            print("   Rate limit exceeded or insufficient permissions.")
        return None

def main():
    """Main function"""
    print("🚀 Updating GitHub Gist for Zapier Integration")
    print("=" * 50)
    print(f"📍 Gist ID: {GIST_ID}")
    
    url = update_github_gist()
    
    if url:
        print(f"\n🎉 Success! Your CSV is now available at:")
        print(f"   {url}")
        print(f"\n📋 Next steps:")
        print(f"   1. Copy the URL above")
        print(f"   2. Set up your Zapier Zap using this URL")
        print(f"   3. Test the integration")
    else:
        print(f"\n💡 Alternative: Create the gist manually")
        print(f"   1. Go to https://gist.github.com")
        print(f"   2. Upload data/addresses_formatted_for_gist.csv")
        print(f"   3. Make it public")
        print(f"   4. Copy the raw URL")

if __name__ == "__main__":
    main() 