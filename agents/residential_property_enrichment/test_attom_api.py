"""
Simple ATTOM API test based on official documentation
"""

import requests
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('../.env')
api_key = os.getenv('ATTOM_API_KEY')

if not api_key:
    print("No API key found")
    exit()

# Test the exact format from ATTOM docs
url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/avm/detail"
headers = {
    "Accept": "application/json",
    "apikey": api_key
}

# Try the format from their documentation
params = {
    "address1": "2325 W Country Club Dr",
    "address2": "Sedalia MO"
}

print(f"Testing ATTOM API with:")
print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Params: {params}")

response = requests.get(url, headers=headers, params=params)

print(f"\nResponse status: {response.status_code}")
print(f"Response: {response.text[:500]}...")

# Also try property/detail endpoint
print("\n" + "="*50)
print("Testing property/detail endpoint...")

url2 = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail"
response2 = requests.get(url2, headers=headers, params=params)

print(f"Response status: {response2.status_code}")
print(f"Response: {response2.text[:500]}...") 