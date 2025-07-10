#!/usr/bin/env python3
"""
Zapier Integration
Programmatically integrate with Zapier to sync Roofr job values to Airtable.
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

class ZapierIntegration:
    """Zapier integration for syncing data between Roofr and Airtable"""
    
    def __init__(self):
        # Zapier credentials from environment variables
        self.zapier_api_key = os.getenv("ZAPIER_API_KEY")
        self.zapier_webhook_url = os.getenv("ZAPIER_WEBHOOK_URL")
        self.roofr_api_key = os.getenv("ROOFR_API_KEY")
        self.roofr_team_id = os.getenv("ROOFR_TEAM_ID")
        
        # API endpoints
        self.roofr_base_url = "https://api.roofr.com/v1"
        self.zapier_base_url = "https://hooks.zapier.com"
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present"""
        if not self.zapier_api_key:
            print("⚠️  Warning: ZAPIER_API_KEY not found in environment variables")
        
        if not self.zapier_webhook_url:
            print("⚠️  Warning: ZAPIER_WEBHOOK_URL not found in environment variables")
        
        if not self.roofr_api_key:
            print("⚠️  Warning: ROOFR_API_KEY not found in environment variables")
        
        if not self.roofr_team_id:
            print("⚠️  Warning: ROOFR_TEAM_ID not found in environment variables")
    
    def _get_roofr_headers(self):
        """Get headers for Roofr API requests"""
        return {
            "Authorization": f"Bearer {self.roofr_api_key}",
            "Content-Type": "application/json"
        }
    
    def _get_zapier_headers(self):
        """Get headers for Zapier API requests"""
        return {
            "Authorization": f"Bearer {self.zapier_api_key}",
            "Content-Type": "application/json"
        }
    
    def get_roofr_jobs_with_financial_data(self, limit: int = 100) -> List[Dict]:
        """Get jobs from Roofr API including financial data"""
        try:
            url = f"{self.roofr_base_url}/teams/{self.roofr_team_id}/jobs"
            params = {"limit": limit, "include": "financial_data"}
            
            response = requests.get(url, headers=self._get_roofr_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get("jobs", [])
            
            # Extract financial data for each job
            enriched_jobs = []
            for job in jobs:
                job_id = job.get("id")
                financial_data = self.get_roofr_job_financial_data(job_id)
                
                enriched_job = {
                    "job_id": job_id,
                    "customer_name": job.get("customer", {}).get("name", ""),
                    "customer_email": job.get("customer", {}).get("email", ""),
                    "job_address": job.get("address", ""),
                    "job_status": job.get("status", ""),
                    "created_date": job.get("created_at", ""),
                    "updated_date": job.get("updated_at", ""),
                    "lead_source": job.get("lead_source", ""),
                    **financial_data  # Include financial data
                }
                enriched_jobs.append(enriched_job)
            
            return enriched_jobs
            
        except Exception as e:
            print(f"Error fetching Roofr jobs: {e}")
            return []
    
    def get_roofr_job_financial_data(self, job_id: str) -> Dict:
        """Get financial data for a specific Roofr job"""
        try:
            url = f"{self.roofr_base_url}/teams/{self.roofr_team_id}/jobs/{job_id}/financial"
            
            response = requests.get(url, headers=self._get_roofr_headers())
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "job_value": data.get("total_amount", 0),
                "estimate_amount": data.get("estimate_amount", 0),
                "invoice_amount": data.get("invoice_amount", 0),
                "payment_status": data.get("payment_status", ""),
                "payment_method": data.get("payment_method", ""),
                "balance_due": data.get("balance_due", 0),
                "amount_paid": data.get("amount_paid", 0)
            }
            
        except Exception as e:
            print(f"Error fetching financial data for job {job_id}: {e}")
            return {
                "job_value": 0,
                "estimate_amount": 0,
                "invoice_amount": 0,
                "payment_status": "",
                "payment_method": "",
                "balance_due": 0,
                "amount_paid": 0
            }
    
    def trigger_zapier_webhook(self, data: Dict) -> bool:
        """Trigger a Zapier webhook with data"""
        try:
            if not self.zapier_webhook_url:
                print("❌ No Zapier webhook URL configured")
                return False
            
            response = requests.post(
                self.zapier_webhook_url,
                headers={"Content-Type": "application/json"},
                json=data
            )
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Zapier webhook triggered successfully")
                return True
            else:
                print(f"❌ Zapier webhook failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error triggering Zapier webhook: {e}")
            return False
    
    def sync_roofr_to_airtable_via_zapier(self, job_data: Dict) -> bool:
        """Sync a single job from Roofr to Airtable via Zapier"""
        
        # Format data for Airtable
        airtable_data = {
            "action": "create_or_update_record",
            "table": "Leads",
            "data": {
                "Name": job_data.get("customer_name", ""),
                "Email": job_data.get("customer_email", ""),
                "Phone": job_data.get("customer_phone", ""),
                "Address": job_data.get("job_address", ""),
                "Status": job_data.get("job_status", ""),
                "Business": "Bud Roofing",
                "Source System": "Roofr",
                "External Job ID": job_data.get("job_id", ""),
                "Invoice Amount": job_data.get("job_value", 0),
                "Payment Status": job_data.get("payment_status", ""),
                "Lead Source": job_data.get("lead_source", ""),
                "Created Date": job_data.get("created_date", ""),
                "Updated Date": job_data.get("updated_date", "")
            },
            "match_field": "Email"  # Use email to match existing records
        }
        
        return self.trigger_zapier_webhook(airtable_data)
    
    def batch_sync_roofr_to_airtable(self, limit: int = 50) -> Dict:
        """Batch sync multiple jobs from Roofr to Airtable"""
        
        print(f"🔄 Starting batch sync of up to {limit} jobs...")
        
        # Get jobs from Roofr
        jobs = self.get_roofr_jobs_with_financial_data(limit)
        
        if not jobs:
            print("❌ No jobs found in Roofr")
            return {"success": 0, "failed": 0, "total": 0}
        
        print(f"📊 Found {len(jobs)} jobs to sync")
        
        success_count = 0
        failed_count = 0
        
        for i, job in enumerate(jobs, 1):
            print(f"🔄 Syncing job {i}/{len(jobs)}: {job.get('customer_name', 'Unknown')}")
            
            if self.sync_roofr_to_airtable_via_zapier(job):
                success_count += 1
            else:
                failed_count += 1
            
            # Rate limiting - don't overwhelm Zapier
            if i < len(jobs):
                import time
                time.sleep(1)
        
        result = {
            "success": success_count,
            "failed": failed_count,
            "total": len(jobs)
        }
        
        print(f"\n✅ Batch sync complete!")
        print(f"   Success: {success_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Total: {len(jobs)}")
        
        return result
    
    def create_zapier_webhook_zap(self) -> Dict:
        """Create a Zapier webhook configuration for this integration"""
        
        webhook_config = {
            "name": "Roofr to Airtable Sync",
            "trigger": {
                "type": "webhook",
                "url": self.zapier_webhook_url,
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "action": {
                "type": "airtable",
                "operation": "create_or_update_record",
                "base_id": "app9Mj5rbIFvK9p9D",
                "table_name": "Leads",
                "field_mapping": {
                    "Name": "{{customer_name}}",
                    "Email": "{{customer_email}}",
                    "Phone": "{{customer_phone}}",
                    "Address": "{{job_address}}",
                    "Status": "{{job_status}}",
                    "Business": "Bud Roofing",
                    "Source System": "Roofr",
                    "External Job ID": "{{job_id}}",
                    "Invoice Amount": "{{job_value}}",
                    "Payment Status": "{{payment_status}}",
                    "Lead Source": "{{lead_source}}",
                    "Created Date": "{{created_date}}",
                    "Updated Date": "{{updated_date}}"
                },
                "match_field": "Email"
            }
        }
        
        # Save webhook configuration
        with open("data/zapier_webhook_config.json", "w") as f:
            json.dump(webhook_config, f, indent=2)
        
        print("✅ Created Zapier webhook configuration")
        return webhook_config
    
    def test_integration(self) -> bool:
        """Test the entire integration flow"""
        
        print("🧪 Testing Roofr to Airtable integration...")
        
        # Test 1: Get Roofr data
        print("\n1. Testing Roofr API connection...")
        jobs = self.get_roofr_jobs_with_financial_data(limit=1)
        
        if not jobs:
            print("❌ Failed to get Roofr data")
            return False
        
        print(f"✅ Successfully got {len(jobs)} job(s) from Roofr")
        
        # Test 2: Test Zapier webhook
        print("\n2. Testing Zapier webhook...")
        test_data = {
            "action": "test",
            "message": "Integration test from Localbase",
            "timestamp": datetime.now().isoformat()
        }
        
        if self.trigger_zapier_webhook(test_data):
            print("✅ Zapier webhook test successful")
        else:
            print("❌ Zapier webhook test failed")
            return False
        
        # Test 3: Test full sync
        print("\n3. Testing full sync...")
        result = self.batch_sync_roofr_to_airtable(limit=1)
        
        if result["success"] > 0:
            print("✅ Full sync test successful")
            return True
        else:
            print("❌ Full sync test failed")
            return False

def create_zapier_setup_guide():
    """Create a comprehensive guide for setting up Zapier integration"""
    
    guide = """
# Zapier Integration Setup Guide

## Overview
This guide shows how to programmatically integrate Roofr with Airtable using Zapier webhooks.

## Step 1: Get API Credentials

### Roofr API
1. Log into your Roofr account
2. Go to Settings > API Keys
3. Generate a new API key
4. Note your Team ID (found in dashboard URL)

### Zapier Webhook
1. Go to Zapier.com
2. Create a new Zap
3. Choose "Webhooks by Zapier" as trigger
4. Choose "Catch Hook" as trigger event
5. Copy the webhook URL

## Step 2: Environment Variables

Add these to your .env file:
```
ROOFR_API_KEY=your_roofr_api_key
ROOFR_TEAM_ID=your_roofr_team_id
ZAPIER_WEBHOOK_URL=your_zapier_webhook_url
ZAPIER_API_KEY=your_zapier_api_key (optional)
```

## Step 3: Zapier Zap Configuration

### Trigger Setup
- App: Webhooks by Zapier
- Event: Catch Hook
- Method: POST
- URL: Copy the generated webhook URL

### Action Setup
- App: Airtable
- Event: Create or Update Record
- Base: Your Localbase base
- Table: Leads
- Field Mapping:
  - Name ← customer_name
  - Email ← customer_email
  - Phone ← customer_phone
  - Address ← job_address
  - Status ← job_status
  - Business ← "Bud Roofing"
  - Source System ← "Roofr"
  - External Job ID ← job_id
  - Invoice Amount ← job_value
  - Payment Status ← payment_status
  - Lead Source ← lead_source

## Step 4: Testing

Run the test_integration() function to verify everything works:
```python
from scripts.zapier_integration import ZapierIntegration

zapier = ZapierIntegration()
zapier.test_integration()
```

## Step 5: Automation

### Option A: Scheduled Sync
Set up a cron job or scheduled task to run:
```python
zapier.batch_sync_roofr_to_airtable(limit=100)
```

### Option B: Real-time Sync
Trigger sync when jobs are updated in Roofr:
```python
# When a job is updated in Roofr
zapier.sync_roofr_to_airtable_via_zapier(job_data)
```

## Step 6: Monitoring

Monitor the sync process:
- Check Zapier task history
- Review Airtable for new/updated records
- Monitor error logs

## Troubleshooting

### Common Issues
1. **API Key Issues**: Verify Roofr API key is valid
2. **Webhook URL**: Ensure Zapier webhook URL is correct
3. **Rate Limiting**: Don't exceed API rate limits
4. **Field Mapping**: Verify Airtable field names match

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
"""
    
    # Save the guide
    with open("config/ZAPIER_INTEGRATION.md", "w") as f:
        f.write(guide)
    
    print("✅ Created config/ZAPIER_INTEGRATION.md")
    return guide

def main():
    """Main function to demonstrate Zapier integration"""
    
    print("🔧 Zapier Integration Setup")
    print("=" * 50)
    
    # Create integration instance
    zapier = ZapierIntegration()
    
    # Create setup guide
    print("\n📝 Creating setup guide...")
    create_zapier_setup_guide()
    
    # Create webhook configuration
    print("\n🔗 Creating webhook configuration...")
    zapier.create_zapier_webhook_zap()
    
    # Test integration if credentials are available
    if zapier.roofr_api_key and zapier.zapier_webhook_url:
        print("\n🧪 Testing integration...")
        zapier.test_integration()
    else:
        print("\n⚠️  Missing credentials - skipping integration test")
        print("   Add your API credentials to .env file and run test_integration()")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Get your Roofr API credentials")
    print("2. Set up your Zapier webhook")
    print("3. Add credentials to .env file")
    print("4. Run test_integration() to verify setup")
    print("5. Use batch_sync_roofr_to_airtable() for automation")

if __name__ == "__main__":
    main() 