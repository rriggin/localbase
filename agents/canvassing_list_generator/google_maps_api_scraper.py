#!/usr/bin/env python3
"""
Google Maps API Address Scraper
Uses Google Places API to get all addresses in a geographic area.
"""

import os
import sys
import time
import csv
import logging
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.env import load_env

@dataclass
class AddressItem:
    """Data class for storing address information."""
    address: str
    name: Optional[str] = None
    place_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    types: Optional[List[str]] = None

class GoogleMapsAPIAddressScraper:
    """
    Scraper that uses Google Maps Places API to get all addresses in a geographic area.
    This should find ALL addresses, not just those visible in web scraping.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_geographic_bounds(self, area_description: str) -> Optional[Tuple[float, float, float, float]]:
        """
        Get geographic bounds for an area using Geocoding API.
        Returns (south, west, north, east) bounds.
        """
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': area_description,
            'key': self.api_key
        }
        
        try:
            response = requests.get(geocode_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    bounds = data['results'][0]['geometry']['bounds']
                    southwest = bounds['southwest']
                    northeast = bounds['northeast']
                    return (southwest['lat'], southwest['lng'], northeast['lat'], northeast['lng'])
            return None
        except Exception as e:
            self.logger.error(f"Error getting bounds: {e}")
            return None
    
    def search_places_in_bounds(self, bounds: Tuple[float, float, float, float], place_type: str = None) -> List[Dict]:
        """
        Search for places within geographic bounds using Places API.
        """
        south, west, north, east = bounds
        center_lat = (south + north) / 2
        center_lng = (west + east) / 2
        
        # Calculate radius (approximate - for circular search)
        import math
        radius = min(50000, int(math.sqrt((north - south)**2 + (east - west)**2) * 111000 / 2))  # Max 50km
        
        nearby_url = f"{self.base_url}/nearbysearch/json"
        all_places = []
        next_page_token = None
        
        while True:
            params = {
                'location': f"{center_lat},{center_lng}",
                'radius': radius,
                'key': self.api_key
            }
            
            if place_type:
                params['type'] = place_type
            
            if next_page_token:
                params['pagetoken'] = next_page_token
                time.sleep(2)  # Required delay for page tokens
            
            try:
                response = requests.get(nearby_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    places = data.get('results', [])
                    all_places.extend(places)
                    
                    self.logger.info(f"Found {len(places)} places (total: {len(all_places)})")
                    
                    next_page_token = data.get('next_page_token')
                    if not next_page_token:
                        break
                else:
                    self.logger.error(f"API error: {response.status_code} - {response.text}")
                    break
                    
            except Exception as e:
                self.logger.error(f"Error searching places: {e}")
                break
        
        return all_places
    
    def search_addresses_by_text(self, area: str, query_terms: List[str]) -> List[Dict]:
        """
        Search for addresses using text search with various terms.
        """
        text_search_url = f"{self.base_url}/textsearch/json"
        all_places = []
        
        for query in query_terms:
            next_page_token = None
            
            while True:
                params = {
                    'query': f"{query} in {area}",
                    'key': self.api_key
                }
                
                if next_page_token:
                    params['pagetoken'] = next_page_token
                    time.sleep(2)
                
                try:
                    response = requests.get(text_search_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        places = data.get('results', [])
                        all_places.extend(places)
                        
                        self.logger.info(f"Query '{query}': found {len(places)} places (total: {len(all_places)})")
                        
                        next_page_token = data.get('next_page_token')
                        if not next_page_token:
                            break
                    else:
                        self.logger.error(f"Text search error: {response.status_code}")
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error in text search: {e}")
                    break
        
        return all_places
    
    def get_comprehensive_addresses(self, area_description: str) -> List[AddressItem]:
        """
        Get comprehensive list of addresses using multiple API strategies.
        """
        self.logger.info(f"Getting comprehensive addresses for: {area_description}")
        all_places = []
        
        # Strategy 1: Get geographic bounds and search within them
        bounds = self.get_geographic_bounds(area_description)
        if bounds:
            self.logger.info(f"Found bounds: {bounds}")
            
            # Search for different types of places
            place_types = [
                'establishment',  # All businesses and points of interest
                'premise',        # Individual addresses
                'street_address', # Street addresses
                'subpremise',     # Apartment/unit numbers
            ]
            
            for place_type in place_types:
                self.logger.info(f"Searching for type: {place_type}")
                places = self.search_places_in_bounds(bounds, place_type)
                all_places.extend(places)
                time.sleep(1)  # Rate limiting
        
        # Strategy 2: Text-based searches for residential areas
        residential_queries = [
            "residential address",
            "house",
            "home",
            "residential property",
            "street address",
            "SW Longview",
            "SW Blazing Star",
            "SW Sunflower",
            "SW 10th",
            "SW 11th", 
            "SW 12th",
            "Lee's Summit MO 64081"
        ]
        
        self.logger.info("Running text-based searches...")
        text_places = self.search_addresses_by_text(area_description, residential_queries)
        all_places.extend(text_places)
        
        # Strategy 3: Comprehensive grid search within bounds
        if bounds:
            self.logger.info("Running comprehensive grid search...")
            grid_places = self.grid_search_area(bounds)
            all_places.extend(grid_places)
        
        # Remove duplicates and filter for addresses
        unique_places = self.deduplicate_places(all_places)
        address_items = self.convert_to_address_items(unique_places)
        
        # Filter for residential addresses in the target area
        filtered_addresses = self.filter_residential_addresses(address_items, area_description)
        
        self.logger.info(f"Found {len(filtered_addresses)} unique addresses")
        return filtered_addresses
    
    def grid_search_area(self, bounds: Tuple[float, float, float, float], grid_size: int = 4) -> List[Dict]:
        """
        Perform a grid search across the area to ensure comprehensive coverage.
        """
        south, west, north, east = bounds
        lat_step = (north - south) / grid_size
        lng_step = (east - west) / grid_size
        
        all_places = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                center_lat = south + (i + 0.5) * lat_step
                center_lng = west + (j + 0.5) * lng_step
                
                nearby_url = f"{self.base_url}/nearbysearch/json"
                params = {
                    'location': f"{center_lat},{center_lng}",
                    'radius': 1000,  # 1km radius for each grid cell
                    'key': self.api_key
                }
                
                try:
                    response = requests.get(nearby_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        places = data.get('results', [])
                        all_places.extend(places)
                        self.logger.info(f"Grid {i},{j}: found {len(places)} places")
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    self.logger.warning(f"Grid search error at {i},{j}: {e}")
        
        return all_places
    
    def deduplicate_places(self, places: List[Dict]) -> List[Dict]:
        """Remove duplicate places based on place_id."""
        seen_ids = set()
        unique_places = []
        
        for place in places:
            place_id = place.get('place_id')
            if place_id and place_id not in seen_ids:
                seen_ids.add(place_id)
                unique_places.append(place)
        
        self.logger.info(f"Deduplicated {len(places)} places to {len(unique_places)} unique places")
        return unique_places
    
    def convert_to_address_items(self, places: List[Dict]) -> List[AddressItem]:
        """Convert Places API results to AddressItem objects."""
        address_items = []
        
        for place in places:
            # Get formatted address or vicinity
            address = place.get('formatted_address') or place.get('vicinity', '')
            
            if address and ('Lee\'s Summit' in address or 'Lee's Summit' in address):
                # Get location coordinates
                location = place.get('geometry', {}).get('location', {})
                lat = location.get('lat')
                lng = location.get('lng')
                
                address_item = AddressItem(
                    address=address,
                    name=place.get('name'),
                    place_id=place.get('place_id'),
                    lat=lat,
                    lng=lng,
                    types=place.get('types', [])
                )
                address_items.append(address_item)
        
        return address_items
    
    def filter_residential_addresses(self, addresses: List[AddressItem], target_area: str) -> List[AddressItem]:
        """Filter for residential addresses in the target area."""
        filtered = []
        
        for addr in addresses:
            # Check if it's in the target area (Lee's Summit, MO 64081)
            if ('Lee\'s Summit' in addr.address or 'Lee's Summit' in addr.address) and '64081' in addr.address:
                # Check if it looks like a residential address (has street number)
                import re
                if re.match(r'^\d{3,5}\s+', addr.address.strip()):
                    filtered.append(addr)
        
        return filtered
    
    def save_addresses_to_csv(self, addresses: List[AddressItem], filename: str):
        """Save addresses to CSV file in the expected format."""
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'address', 'place_id', 'lat', 'lng', 'types'])
            
            for addr in addresses:
                types_str = ','.join(addr.types) if addr.types else ''
                writer.writerow([
                    addr.name or '',
                    addr.address,
                    addr.place_id or '',
                    addr.lat or '',
                    addr.lng or '',
                    types_str
                ])
        
        self.logger.info(f"Saved {len(addresses)} addresses to {filepath}")
        return filepath

def main():
    """Main function to run the Google Maps API scraper."""
    # Load environment variables
    load_env()
    
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_MAPS_API_KEY not found in environment variables")
        print("💡 Get your API key from: https://console.cloud.google.com/")
        print("💡 Enable: Places API, Geocoding API")
        print("💡 Add to .env file: GOOGLE_MAPS_API_KEY=your_key_here")
        return
    
    # Initialize scraper
    scraper = GoogleMapsAPIAddressScraper(api_key)
    
    # Target area (Lee's Summit, MO 64081 - Winterset/Longview area)
    area_description = "Lee's Summit, MO 64081"
    
    try:
        # Get comprehensive address list
        addresses = scraper.get_comprehensive_addresses(area_description)
        
        if addresses:
            print(f"\n🎉 SUCCESS! Found {len(addresses)} addresses using Google Maps API")
            print("=" * 60)
            
            # Show first 10 addresses
            for i, addr in enumerate(addresses[:10], 1):
                print(f"{i}. {addr.address}")
                if addr.name:
                    print(f"   Name: {addr.name}")
                print()
            
            if len(addresses) > 10:
                print(f"... and {len(addresses) - 10} more addresses")
            
            # Save to CSV
            csv_file = scraper.save_addresses_to_csv(addresses, "addresses_api.csv")
            
            print(f"\n📁 Results saved to: {csv_file}")
            print(f"🎯 Total addresses found: {len(addresses)}")
            
            # Check if we got close to the expected 1,192
            if len(addresses) >= 1000:
                print("✅ Excellent! Found 1,000+ addresses - this looks comprehensive!")
            elif len(addresses) >= 500:
                print("✅ Good coverage! Found 500+ addresses")
            else:
                print("⚠️  Found fewer addresses than expected. May need to adjust search strategy.")
                
        else:
            print("❌ No addresses found. Check API key and area description.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 