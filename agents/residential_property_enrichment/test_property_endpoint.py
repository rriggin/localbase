import requests
import os
from dotenv import load_dotenv

load_dotenv('../../.env')
api_key = os.getenv('ATTOM_API_KEY')

# Test property/detail endpoint 
url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail"
headers = {"Accept": "application/json", "apikey": api_key}
params = {"address1": "2325 W Country Club Dr", "address2": "Sedalia MO"}

print("Testing property/detail endpoint:")
response = requests.get(url, headers=headers, params=params)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:300]}...")
