#!/usr/bin/env python3
"""
Trigger Zapier Webhook for CSV Import
Manually kick off the Zapier workflow to import new data to Clay.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from main project directory
load_dotenv('../../.env')

ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_CLAY_WEBHOOK_URL")
CSV_URL = "https://gist.githubusercontent.com/rriggin/1cb623ab465f4ebe6ddf3a934bacc5a7/raw/canvassing-data"

if not ZAPIER_WEBHOOK_URL:
    print("❌ ZAPIER_CLAY_WEBHOOK_URL not found in .env file.")
    print("   Please add your Clay webhook URL to the .env file as ZAPIER_CLAY_WEBHOOK_URL=...")
    exit(1)

payload = {
    "csv_url": CSV_URL
}

print(f"🚀 Triggering Zapier webhook at: {ZAPIER_WEBHOOK_URL}")
print(f"   Payload: {payload}")

try:
    response = requests.post(ZAPIER_WEBHOOK_URL, json=payload)
    print(f"✅ Webhook triggered! Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Error triggering webhook: {e}") 