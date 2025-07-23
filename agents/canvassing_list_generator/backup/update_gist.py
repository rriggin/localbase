#!/usr/bin/env python3
"""
Update GitHub Gist with CSV Data
Update the existing GitHub Gist by APPENDING fresh CSV data for Zapier integration.
This maintains a running record of all canvassing addresses.
"""

import os
import requests
import json
import csv
import io
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from main project directory
load_dotenv('../../.env')

# Your existing gist ID from the URL: https://gist.github.com/rriggin/1cb623ab465f4ebe6ddf3a934bacc5a7
GIST_ID = "1cb623ab465f4ebe6ddf3a934bacc5a7"

def get_existing_gist_content():
    """Download the current content of the Gist"""
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        return None
    
    try:
        # Get the current gist content
        url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Get the content of the canvassing-data file
        if "canvassing-data" in data["files"]:
            return data["files"]["canvassing-data"]["content"]
        else:
            return None
            
    except Exception as e:
        print(f"⚠️  Could not fetch existing Gist content: {e}")
        return None

def append_new_data_to_gist(new_csv_path: str):
    """Append new CSV data to existing Gist content"""
    
    # Read new data
    if not os.path.exists(new_csv_path):
        print(f"❌ New CSV file not found: {new_csv_path}")
        return None
    
    with open(new_csv_path, 'r', encoding='utf-8') as f:
        new_content = f.read().strip()
    
    # Get existing Gist content
    existing_content = get_existing_gist_content()
    
    if existing_content:
        print(f"📥 Found existing Gist content, appending new data...")
        
        # Parse existing content to get existing addresses
        existing_lines = existing_content.strip().split('\n')
        header_line = existing_lines[0] if existing_lines else ""
        existing_data_lines = existing_lines[1:] if len(existing_lines) > 1 else []
        
        # Parse new content
        new_lines = new_content.strip().split('\n')
        new_data_lines = new_lines[1:] if len(new_lines) > 1 else []  # Skip header
        
        # Create set of existing addresses to avoid duplicates
        existing_addresses = set()
        for line in existing_data_lines:
            if line.strip():
                # Extract address from the CSV line (assuming address is in the second column)
                try:
                    reader = csv.reader([line])
                    row = next(reader)
                    if len(row) > 1:
                        existing_addresses.add(row[1].strip())  # address column
                except:
                    continue
        
        # Filter out duplicate addresses from new data
        new_unique_lines = []
        duplicates_count = 0
        for line in new_data_lines:
            if line.strip():
                try:
                    reader = csv.reader([line])
                    row = next(reader)
                    if len(row) > 1:
                        address = row[1].strip()
                        if address not in existing_addresses:
                            new_unique_lines.append(line)
                            existing_addresses.add(address)
                        else:
                            duplicates_count += 1
                except:
                    continue
        
        if duplicates_count > 0:
            print(f"🔄 Skipped {duplicates_count} duplicate addresses")
        
        if new_unique_lines:
            # Combine existing and new data
            combined_content = header_line + '\n' + '\n'.join(existing_data_lines + new_unique_lines)
            total_addresses = len(existing_data_lines) + len(new_unique_lines)
            print(f"✅ Adding {len(new_unique_lines)} new addresses to existing {len(existing_data_lines)} addresses")
            print(f"📊 Total addresses in Gist: {total_addresses}")
        else:
            print("ℹ️  No new unique addresses to add")
            combined_content = existing_content
            total_addresses = len(existing_data_lines)
    else:
        print(f"📝 No existing Gist content found, creating new...")
        combined_content = new_content
        new_lines = new_content.strip().split('\n')
        total_addresses = len(new_lines) - 1 if len(new_lines) > 1 else 0
    
    return combined_content, total_addresses

def update_github_gist():
    """Update the GitHub Gist with new data appended to existing data"""
    
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
    
    # Append new data to existing gist content
    csv_path = "data/addresses_formatted_for_gist.csv"
    result = append_new_data_to_gist(csv_path)
    
    if result is None:
        return None
    
    combined_content, total_addresses = result
    
    # Update the existing gist
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "description": f"Canvassing Data - Running Record - {total_addresses} Total Addresses - Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "files": {
            "canvassing-data": {
                "content": combined_content
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
        print(f"   Total addresses: {total_addresses}")
        print(f"\n🔗 Your Zapier webhook should now receive this data")
        
        # Save the URL to a file for easy access
        with open("gist_url.txt", "w") as f:
            f.write(f"Gist URL: {gist_url}\n")
            f.write(f"Raw CSV URL: {raw_url}\n")
            f.write(f"Total Addresses: {total_addresses}\n")
            f.write(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"   URL saved to: gist_url.txt")
        
        return raw_url
        
    except Exception as e:
        print(f"❌ Error updating GitHub Gist: {e}")
        if hasattr(e, 'response') and e.response:
            if e.response.status_code == 401:
                print("   Authentication failed. Check your GitHub token.")
            elif e.response.status_code == 403:
                print("   Rate limit exceeded or insufficient permissions.")
        return None

def main():
    """Main function"""
    print("🚀 Updating GitHub Gist for Zapier Integration (Append Mode)")
    print("=" * 60)
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