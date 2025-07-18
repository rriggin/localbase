
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
