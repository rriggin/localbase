#!/usr/bin/env python3
"""
Clay.com Integration
Import scraped addresses to Clay.com table.
"""

import os
import requests
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClayIntegration:
    """Clay.com API integration for importing data"""
    
    def __init__(self):
        # Clay.com credentials from environment variables
        self.clay_api_key = os.getenv("CLAY_API_KEY")
        self.clay_base_url = "https://api.clay.com"
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present"""
        if not self.clay_api_key:
            print("⚠️  Warning: CLAY_API_KEY not found in environment variables")
            print("   Get your API key from: https://app.clay.com/settings/api")
    
    def _get_headers(self):
        """Get headers for Clay API requests"""
        return {
            "Authorization": f"Bearer {self.clay_api_key}",
            "Content-Type": "application/json"
        }
    
    def _get_graphql_headers(self):
        """Get headers for GraphQL requests"""
        return {
            "Authorization": f"Bearer {self.clay_api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> bool:
        """Test the Clay API connection by trying different endpoints"""
        print("🔍 Testing Clay.com API connection...")
        print("   Note: Clay.com may not have a public API for table operations")
        
        endpoints_to_try = [
            "/user",
            "/workspace", 
            "/workspaces",
            "/me",
            "/account",
            "/graphql",
            "/api/v1/user",
            "/api/v1/workspace",
            "/api/user",
            "/api/workspace"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                if endpoint == "/graphql":
                    # Try GraphQL endpoint
                    url = f"{self.clay_base_url}{endpoint}"
                    payload = {
                        "query": """
                        query {
                            viewer {
                                id
                                email
                            }
                        }
                        """
                    }
                    response = requests.post(url, headers=self._get_graphql_headers(), json=payload)
                else:
                    url = f"{self.clay_base_url}{endpoint}"
                    response = requests.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    print(f"✅ Clay API connection successful via {endpoint}")
                    if endpoint == "/graphql":
                        data = response.json()
                        if "errors" not in data:
                            print(f"   GraphQL response: {data}")
                    return True
                elif response.status_code == 401:
                    print(f"❌ Authentication failed - check your API key")
                    return False
                else:
                    print(f"⚠️  Endpoint {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️  Error testing {endpoint}: {e}")
        
        print("❌ Could not establish Clay API connection with any endpoint")
        print("\n💡 This confirms Clay.com does not have a public REST API for table operations.")
        print("   You'll need to use their UI or Zapier integration instead.")
        return False
    
    def prepare_csv_for_import(self, csv_path: str, output_path: str = None) -> str:
        """Prepare the CSV file for manual import to Clay"""
        try:
            # Read the original CSV
            df = pd.read_csv(csv_path)
            print(f"📊 Loaded {len(df)} addresses from {csv_path}")
            
            # Create a new CSV optimized for Clay import
            # Clay typically expects columns like: name, address, city, state, zip, etc.
            clay_df = df.copy()
            
            # If there's only one address column, split it into components
            if 'address' in clay_df.columns and len(clay_df.columns) == 2:  # name, address
                # Split address into components
                addresses = clay_df['address'].str.split(', ', expand=True)
                if len(addresses.columns) >= 3:
                    clay_df['street_address'] = addresses[0]
                    clay_df['city'] = addresses[1]
                    clay_df['state_zip'] = addresses[2]
                    
                    # Split state and zip
                    state_zip = clay_df['state_zip'].str.split(' ', expand=True)
                    if len(state_zip.columns) >= 2:
                        clay_df['state'] = state_zip[0]
                        clay_df['zip_code'] = state_zip[1]
                        clay_df = clay_df.drop('state_zip', axis=1)
                
                # Keep original address for reference
                clay_df['full_address'] = clay_df['address']
            
            # Add metadata columns
            clay_df['source'] = 'Google Maps List Scraper'
            clay_df['import_date'] = datetime.now().strftime('%Y-%m-%d')
            clay_df['import_time'] = datetime.now().strftime('%H:%M:%S')
            
            # Save the prepared CSV
            output_file = output_path or "data/addresses_for_clay.csv"
            clay_df.to_csv(output_file, index=False)
            
            print(f"✅ Prepared CSV for Clay import: {output_file}")
            print(f"   Columns: {list(clay_df.columns)}")
            print(f"   Records: {len(clay_df)}")
            
            return output_file
            
        except Exception as e:
            print(f"❌ Error preparing CSV: {e}")
            return csv_path
    
    def show_manual_import_instructions(self, csv_path: str):
        """Show instructions for manual import to Clay"""
        print("\n📋 Manual Import Instructions for Clay.com")
        print("=" * 50)
        print(f"1. Open your Clay.com dashboard")
        print(f"2. Navigate to your 'Canvassing Data' table")
        print(f"3. Look for an 'Import' or 'Upload CSV' button")
        print(f"4. Upload the file: {csv_path}")
        print(f"5. Map the columns as follows:")
        
        # Show column mapping
        df = pd.read_csv(csv_path)
        print(f"\n📊 Column Mapping:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        
        print(f"\n💡 Tips:")
        print(f"   - Make sure the CSV has headers")
        print(f"   - Clay may auto-detect column types")
        print(f"   - You can rename columns after import")
        print(f"   - Total records to import: {len(df)}")
        
        print(f"\n🔗 Quick Access:")
        print(f"   - Clay Dashboard: https://app.clay.com")
        print(f"   - CSV File: {os.path.abspath(csv_path)}")
    
    def create_zapier_setup_guide(self):
        """Create a guide for setting up Zapier integration"""
        guide = """
# Clay.com Zapier Integration Guide

## Overview
Since Clay.com doesn't have a public API, you can use Zapier to automate CSV imports.

## Step 1: Set Up Zapier Integration

1. Go to [Zapier.com](https://zapier.com)
2. Create a new Zap
3. Choose trigger: "Google Drive" → "New File in Folder"
4. Choose action: "Clay.com" → "Create Record" (if available)

## Step 2: Alternative Workflow

If Clay.com doesn't have a Zapier action:
1. Trigger: "Google Drive" → "New File in Folder"
2. Action: "Google Sheets" → "Create Spreadsheet Row"
3. Action: "Email" → "Send Email" (to notify you to import)

## Step 3: File Monitoring

1. Upload your CSV to a Google Drive folder
2. Zapier will detect the new file
3. Automatically trigger the import process

## Step 4: Testing

1. Upload a test CSV to your monitored folder
2. Check that the Zap triggers correctly
3. Verify data appears in Clay.com

## Alternative: Scheduled Imports

Set up a recurring Zap that:
1. Runs daily/weekly
2. Checks for new CSV files
3. Sends you a notification to import
"""
        
        with open("CLAY_ZAPIER_GUIDE.md", "w") as f:
            f.write(guide)
        
        print("✅ Created Zapier setup guide: CLAY_ZAPIER_GUIDE.md")

def main():
    """Main function to run the Clay integration"""
    print("🚀 Clay.com Integration for Google Maps Addresses")
    print("=" * 50)
    
    # Initialize Clay integration
    clay = ClayIntegration()
    
    # Test connection (will likely fail, but that's expected)
    clay.test_connection()
    
    # Import addresses from CSV
    csv_path = "data/addresses.csv"
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        print("   Please run the scraper first to generate addresses.csv")
        return
    
    # Prepare CSV for Clay import
    print(f"\n📋 Preparing data for Clay.com import...")
    prepared_csv = clay.prepare_csv_for_import(csv_path)
    
    # Show manual import instructions
    clay.show_manual_import_instructions(prepared_csv)
    
    # Create Zapier guide
    print(f"\n🔧 Creating automation guide...")
    clay.create_zapier_setup_guide()
    
    print(f"\n🎉 Setup complete!")
    print(f"   Next steps:")
    print(f"   1. Import {prepared_csv} to your 'Canvassing Data' table in Clay")
    print(f"   2. Review CLAY_ZAPIER_GUIDE.md for automation options")
    print(f"   3. Let me know if you need help with the import process!")

if __name__ == "__main__":
    main() 