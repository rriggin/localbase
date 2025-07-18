
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
