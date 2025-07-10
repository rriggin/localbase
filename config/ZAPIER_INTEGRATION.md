# Zapier Integration Guide

## Overview
This guide covers all Zapier integrations for LocalBase, including Roofr API integration, webhook automation, and data synchronization with Airtable.

## Environment Variables

Create a `.env` file in the project root with these variables:

```bash
# Airtable Configuration
AIRTABLE_TOKEN=your_airtable_token_here
AIRTABLE_BASE_ID=your_airtable_base_id_here
AIRTABLE_TABLE_NAME=Leads

# Zapier Configuration
ZAPIER_API_KEY=your_zapier_api_key_here
ZAPIER_WEBHOOK_URL=your_zapier_webhook_url_here
ZAPIER_ROOFR_WEBHOOK_URL=your_roofr_extraction_webhook_url_here

# Python Configuration
PYTHON_EXECUTABLE=python3
```

## Integration Options

### Option 1: Zapier Roofr App Integration

**Use Case**: When you want to extract data from Roofr via Zapier without direct API access.

#### Step 1: Set Up Zapier Roofr Integration
1. Go to Zapier.com and create a new Zap
2. **Trigger**: Choose "Webhooks by Zapier" → "Catch Hook"
3. **Action 1**: Choose "Roofr" → "Find Job"
   - Search by: Customer Email
   - Search value: {{customer_email}}
4. **Action 2**: Choose "Roofr" → "Get Job Details"
   - Job ID: {{job_id}}
   - Include financial data: Yes
5. **Action 3**: Choose "Airtable" → "Create or Update Record"

#### Step 2: Test Data Extraction
```python
from scripts.zapier_roofr_integration import ZapierRoofrIntegration

zapier = ZapierRoofrIntegration()
data = zapier.get_mary_menard_data()
print(data)
```

### Option 2: Manual CSV Processing

**Use Case**: When you have CSV exports from Roofr and want to process them.

#### Step 1: Prepare CSV Data
Place your Roofr CSV export in `data/roofr.csv`

#### Step 2: Run Processing Scripts
```python
# Analyze existing data
python scripts/analyze_roofmaxx_roofr_mapping.py

# Update Airtable with Roofr data
python scripts/migrate_airtable_to_roofr_statuses.py
```



## Available Data Fields

### Job Information
- Job ID
- Customer Name
- Customer Email
- Job Address
- Job Status
- Created Date

### Financial Information
- Job Value (Total Amount)
- Estimate Amount
- Invoice Amount
- Payment Status
- Payment Method

### Workflow Information
- Current Stage
- Assigned To
- Lead Source
- Notes/Comments

## Automation Workflows

### Real-time Sync
1. **Trigger**: New job created in Roofr
2. **Action**: Create/update record in Airtable
3. **Trigger**: Job status changed in Roofr
4. **Action**: Update status in Airtable
5. **Trigger**: Payment received in Roofr
6. **Action**: Update payment status in Airtable

### Batch Processing
```python
# Process specific customers
customers = ["customer1@email.com", "customer2@email.com"]
for email in customers:
    zapier.trigger_roofr_data_extraction(customer_email=email)
```

## Monitoring and Troubleshooting

### Check Integration Status
```python
# Test Zapier connections
zapier = ZapierRoofrIntegration()
data = zapier.get_mary_menard_data()

# Check Zapier task history
# Review Airtable for new/updated records
# Monitor error logs
```

### Common Issues

1. **Zapier Authentication**: Ensure Roofr account is connected in Zapier
2. **Webhook URL**: Ensure Zapier webhook URL is correct
3. **Rate Limiting**: Don't exceed Zapier task limits
4. **Field Mapping**: Verify Airtable field names match

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- Never commit `.env` files to version control
- Use environment variables for all sensitive data
- Regularly rotate API keys
- Monitor API usage and rate limits

## Next Steps

1. Set up your `.env` file with actual credentials
2. Choose the integration option that fits your needs
3. Test the integration with a small dataset
4. Monitor the sync process and adjust as needed
5. Set up automated monitoring and alerts 