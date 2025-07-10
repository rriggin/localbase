#!/usr/bin/env python3
"""
Zapier Roofr Integration
Use Zapier to get data from Roofr without requiring Roofr API access.
This works with your existing CSV data and Zapier webhooks.
"""

import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ZapierRoofrIntegration:
    """Zapier integration to get Roofr data without API access"""
    
    def __init__(self):
        # Zapier credentials from environment variables
        self.zapier_api_key = os.getenv("ZAPIER_API_KEY")
        self.zapier_webhook_url = os.getenv("ZAPIER_WEBHOOK_URL")
        self.zapier_roofr_webhook_url = os.getenv("ZAPIER_ROOFR_WEBHOOK_URL")
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present"""
        if not self.zapier_webhook_url:
            print("⚠️  Warning: ZAPIER_WEBHOOK_URL not found in environment variables")
        
        if not self.zapier_roofr_webhook_url:
            print("⚠️  Warning: ZAPIER_ROOFR_WEBHOOK_URL not found in environment variables")
            print("   This is needed to trigger Roofr data extraction")
    
    def trigger_roofr_data_extraction(self, customer_email: str = None, customer_name: str = None) -> Dict:
        """
        Trigger Zapier to extract data from Roofr for a specific customer
        This uses Zapier's Roofr integration to pull data
        """
        try:
            if not self.zapier_roofr_webhook_url:
                print("❌ No Zapier Roofr webhook URL configured")
                return {}
            
            # Prepare data for Zapier to extract from Roofr
            extraction_data = {
                "action": "extract_roofr_data",
                "timestamp": datetime.now().isoformat(),
                "customer_email": customer_email,
                "customer_name": customer_name,
                "extract_financial_data": True,
                "extract_job_details": True
            }
            
            response = requests.post(
                self.zapier_roofr_webhook_url,
                headers={"Content-Type": "application/json"},
                json=extraction_data
            )
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Roofr data extraction triggered successfully")
                return response.json() if response.content else {}
            else:
                print(f"❌ Roofr data extraction failed: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error triggering Roofr data extraction: {e}")
            return {}
    
    def get_customer_from_existing_data(self, customer_email: str = None, customer_name: str = None) -> List[Dict]:
        """
        Get customer data from existing CSV files
        This is what you currently have access to
        """
        customers = []
        
        # Check Roofr CSV
        try:
            roofr_df = pd.read_csv("data/roofr.csv")
            
            if customer_email:
                mask = roofr_df['Customer Email'].str.contains(customer_email, case=False, na=False)
            elif customer_name:
                mask = roofr_df['Customer Name'].str.contains(customer_name, case=False, na=False)
            else:
                mask = pd.Series([True] * len(roofr_df))
            
            roofr_customers = roofr_df[mask].to_dict('records')
            for customer in roofr_customers:
                customer['source'] = 'roofr_csv'
                customers.append(customer)
                
        except Exception as e:
            print(f"Error reading Roofr CSV: {e}")
        
        # Check Dispatch CSV
        try:
            dispatch_df = pd.read_csv("data/843.csv")
            
            if customer_email:
                mask = dispatch_df['Email'].str.contains(customer_email, case=False, na=False)
            elif customer_name:
                mask = dispatch_df['Name'].str.contains(customer_name, case=False, na=False)
            else:
                mask = pd.Series([True] * len(dispatch_df))
            
            dispatch_customers = dispatch_df[mask].to_dict('records')
            for customer in dispatch_customers:
                customer['source'] = 'dispatch_csv'
                customers.append(customer)
                
        except Exception as e:
            print(f"Error reading Dispatch CSV: {e}")
        
        return customers
    
    def analyze_missing_financial_data(self, customer_email: str = None, customer_name: str = None) -> Dict:
        """
        Analyze what financial data is missing for a customer
        """
        print(f"🔍 Analyzing data for: {customer_email or customer_name}")
        
        # Get existing data
        existing_data = self.get_customer_from_existing_data(customer_email, customer_name)
        
        analysis = {
            "customer_email": customer_email,
            "customer_name": customer_name,
            "existing_records": len(existing_data),
            "missing_financial_data": True,
            "available_data": {},
            "missing_data": []
        }
        
        for record in existing_data:
            source = record.get('source', 'unknown')
            analysis["available_data"][source] = {
                "customer_name": record.get('Customer Name') or record.get('Name', ''),
                "customer_email": record.get('Customer Email') or record.get('Email', ''),
                "job_status": record.get('Job Status') or record.get('Status', ''),
                "lead_source": record.get('Lead Source', ''),
                "has_financial_data": False
            }
            
            # Check if any financial fields exist
            financial_fields = ['job_value', 'invoice_amount', 'total_amount', 'price', 'cost']
            for field in financial_fields:
                if field in record and record[field]:
                    analysis["available_data"][source]["has_financial_data"] = True
                    analysis["available_data"][source][field] = record[field]
                    break
        
        # Identify missing data
        if not any(data.get("has_financial_data", False) for data in analysis["available_data"].values()):
            analysis["missing_data"].append("Invoice Amount")
            analysis["missing_data"].append("Job Value")
            analysis["missing_data"].append("Payment Status")
        
        return analysis
    
    def create_zapier_roofr_zap_config(self) -> Dict:
        """
        Create configuration for a Zapier Zap that extracts Roofr data
        """
        zap_config = {
            "name": "Extract Roofr Financial Data",
            "description": "Extract financial data from Roofr for customers",
            "trigger": {
                "app": "Webhooks by Zapier",
                "event": "Catch Hook",
                "url": self.zapier_roofr_webhook_url,
                "method": "POST"
            },
            "actions": [
                {
                    "app": "Roofr",
                    "event": "Find Job",
                    "search_by": "Customer Email",
                    "search_value": "{{customer_email}}"
                },
                {
                    "app": "Roofr", 
                    "event": "Get Job Details",
                    "job_id": "{{job_id}}",
                    "include_financial": True
                },
                {
                    "app": "Airtable",
                    "event": "Create or Update Record",
                    "base_id": "app9Mj5rbIFvK9p9D",
                    "table": "Leads",
                    "fields": {
                        "Name": "{{customer_name}}",
                        "Email": "{{customer_email}}",
                        "Invoice Amount": "{{job_value}}",
                        "Payment Status": "{{payment_status}}",
                        "Source System": "Roofr",
                        "External Job ID": "{{job_id}}",
                        "Updated Date": "{{updated_at}}"
                    },
                    "match_field": "Email"
                }
            ]
        }
        
        # Save configuration
        with open("data/zapier_roofr_zap_config.json", "w") as f:
            json.dump(zap_config, f, indent=2)
        
        print("✅ Created Zapier Roofr Zap configuration")
        return zap_config
    
    def get_mary_menard_data(self) -> Dict:
        """
        Get all available data for Mary Menard
        """
        print("🔍 Getting Mary Menard's data...")
        
        # Get existing data
        existing_data = self.get_customer_from_existing_data(
            customer_email="mmenardkc@gmail.com",
            customer_name="Mary Menard"
        )
        
        # Analyze missing data
        analysis = self.analyze_missing_financial_data(
            customer_email="mmenardkc@gmail.com"
        )
        
        # Try to trigger Roofr data extraction
        if self.zapier_roofr_webhook_url:
            print("🔄 Triggering Roofr data extraction for Mary Menard...")
            roofr_data = self.trigger_roofr_data_extraction(
                customer_email="mmenardkc@gmail.com"
            )
        else:
            roofr_data = {}
        
        return {
            "existing_data": existing_data,
            "analysis": analysis,
            "roofr_extraction": roofr_data,
            "recommendations": self._get_recommendations(analysis)
        }
    
    def _get_recommendations(self, analysis: Dict) -> List[str]:
        """Get recommendations based on data analysis"""
        recommendations = []
        
        if analysis["missing_financial_data"]:
            recommendations.append("Set up Zapier Roofr integration to extract financial data")
            recommendations.append("Configure Roofr Zapier app to pull job values and invoice amounts")
            recommendations.append("Map Roofr financial fields to Airtable Invoice Amount field")
        
        if analysis["existing_records"] == 0:
            recommendations.append("Customer not found in existing data - check spelling/email")
        
        if analysis["existing_records"] > 1:
            recommendations.append("Multiple records found - consider data deduplication")
        
        return recommendations
    
    def create_setup_guide(self):
        """Create a setup guide for Zapier Roofr integration"""
        
        guide = """
# Zapier Roofr Integration Setup Guide

## Overview
This guide shows how to use Zapier to extract financial data from Roofr without requiring Roofr API access.

## Step 1: Set Up Zapier Roofr Integration

### Create a New Zap
1. Go to Zapier.com and create a new Zap
2. **Trigger**: Choose "Webhooks by Zapier" → "Catch Hook"
3. **Action 1**: Choose "Roofr" → "Find Job"
   - Search by: Customer Email
   - Search value: {{customer_email}}
4. **Action 2**: Choose "Roofr" → "Get Job Details"
   - Job ID: {{job_id}}
   - Include financial data: Yes
5. **Action 3**: Choose "Airtable" → "Create or Update Record"
   - Base: Your Localbase base
   - Table: Leads
   - Fields to map:
     - Name ← {{customer_name}}
     - Email ← {{customer_email}}
     - Invoice Amount ← {{job_value}}
     - Payment Status ← {{payment_status}}
     - Source System ← "Roofr"
     - External Job ID ← {{job_id}}

### Get Webhook URLs
1. Copy the webhook URL from the trigger step
2. Add it to your .env file as ZAPIER_ROOFR_WEBHOOK_URL

## Step 2: Environment Variables

Add to your .env file:
```
ZAPIER_ROOFR_WEBHOOK_URL=your_roofr_extraction_webhook_url
ZAPIER_WEBHOOK_URL=your_airtable_sync_webhook_url
```

## Step 3: Test the Integration

Run this script to test:
```python
from scripts.zapier_roofr_integration import ZapierRoofrIntegration

zapier = ZapierRoofrIntegration()
data = zapier.get_mary_menard_data()
print(data)
```

## Step 4: Extract Financial Data

To get Mary Menard's invoice amount:
```python
# Trigger Roofr data extraction
roofr_data = zapier.trigger_roofr_data_extraction(
    customer_email="mmenardkc@gmail.com"
)

# This will:
# 1. Find Mary Menard in Roofr
# 2. Extract her job value/invoice amount
# 3. Sync to Airtable
```

## Step 5: Automation

### Option A: Manual Extraction
Trigger extraction when needed:
```python
zapier.trigger_roofr_data_extraction(customer_email="customer@email.com")
```

### Option B: Batch Processing
Process multiple customers:
```python
customers = ["customer1@email.com", "customer2@email.com"]
for email in customers:
    zapier.trigger_roofr_data_extraction(customer_email=email)
```

## Troubleshooting

### Common Issues
1. **Roofr App Not Found**: Make sure Roofr has a Zapier integration
2. **Authentication**: Ensure Roofr account is connected in Zapier
3. **Field Mapping**: Verify Airtable field names match
4. **Rate Limiting**: Don't exceed Zapier task limits

### Alternative Approach
If Roofr doesn't have a Zapier app:
1. Use Zapier's "Web Scraper" to extract data from Roofr dashboard
2. Set up scheduled scraping of customer pages
3. Parse the HTML to extract financial data
"""
        
        # Save the guide
        with open("config/ZAPIER_INTEGRATION.md", "w") as f:
            f.write(guide)
        
        print("✅ Created config/ZAPIER_INTEGRATION.md")
        return guide

def main():
    """Main function to demonstrate Zapier Roofr integration"""
    
    print("🔧 Zapier Roofr Integration Setup")
    print("=" * 50)
    
    # Create integration instance
    zapier = ZapierRoofrIntegration()
    
    # Create setup guide
    print("\n📝 Creating setup guide...")
    zapier.create_setup_guide()
    
    # Create Zap configuration
    print("\n🔗 Creating Zap configuration...")
    zapier.create_zapier_roofr_zap_config()
    
    # Get Mary Menard's data
    print("\n🔍 Analyzing Mary Menard's data...")
    mary_data = zapier.get_mary_menard_data()
    
    print(f"\n📊 Analysis Results:")
    print(f"   Existing records: {mary_data['analysis']['existing_records']}")
    print(f"   Missing financial data: {mary_data['analysis']['missing_financial_data']}")
    
    if mary_data['analysis']['missing_data']:
        print(f"   Missing data: {', '.join(mary_data['analysis']['missing_data'])}")
    
    print(f"\n💡 Recommendations:")
    for rec in mary_data['recommendations']:
        print(f"   • {rec}")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
        print("1. Set up Zapier Roofr integration (see config/ZAPIER_INTEGRATION.md)")
    print("2. Add ZAPIER_ROOFR_WEBHOOK_URL to .env file")
    print("3. Test with get_mary_menard_data()")
    print("4. Use trigger_roofr_data_extraction() to get financial data")

if __name__ == "__main__":
    main() 