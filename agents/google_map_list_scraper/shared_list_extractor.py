"""
Google Maps Shared List Extractor

This module extracts addresses from shared Google Maps lists by accessing the raw API data.
Based on the method from: https://gist.github.com/ByteSizedMarius/8c9df821ebb69b07f2d82de01e68387d

This approach should extract ALL addresses from a list, not just what's initially loaded on the page.
"""

import html
import re
import requests
import csv
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs


@dataclass
class ExtractedPlace:
    """Data class for storing extracted place information."""
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None


class SharedListExtractor:
    """
    Extracts places from shared Google Maps lists using raw API data.
    
    This method works by:
    1. Taking a shared Google Maps list URL
    2. Converting it to the raw data URL format
    3. Extracting coordinates and names from the raw response
    4. Optionally reverse geocoding to get full addresses
    """
    
    def __init__(self):
        """Initialize the extractor."""
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the extractor."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def convert_url_to_raw_data_url(self, shared_url: str) -> str:
        """
        Convert a shared Google Maps list URL to the raw data URL format.
        
        Args:
            shared_url: The shared Google Maps list URL (can be shortened)
            
        Returns:
            The raw data URL that can be used to extract place data
        """
        self.logger.info(f"Processing URL: {shared_url}")
        
        # If it's a shortened URL, follow redirects to get the full URL
        if "maps.app.goo.gl" in shared_url or "goo.gl" in shared_url:
            self.logger.info("Shortened URL detected, following redirects...")
            try:
                response = requests.head(shared_url, allow_redirects=True)
                shared_url = response.url
                self.logger.info(f"Redirect resolved to: {shared_url}")
            except Exception as e:
                self.logger.warning(f"Could not follow redirect: {e}")
        
        # Parse the URL to extract the data parameter
        parsed = urlparse(shared_url)
        
        # Check if this is already a maps URL with data parameter
        if 'data=' in parsed.query:
            # Extract the data portion
            query_params = parse_qs(parsed.query)
            data_param = query_params.get('data', [''])[0]
        elif '/data=' in shared_url:
            # Extract data from the path
            data_param = shared_url.split('/data=')[1].split('?')[0].split('&')[0]
        else:
            # Try alternative extraction methods for different URL formats
            self.logger.info("Standard data parameter not found, trying alternative methods...")
            
            # Look for list ID in different URL patterns
            if "/maps/list/" in shared_url:
                # Format: https://www.google.com/maps/list/[ID]
                list_id = shared_url.split("/maps/list/")[1].split("?")[0].split("/")[0]
                self.logger.info(f"Found list ID: {list_id}")
                # Convert to data format (this might need adjustment)
                data_param = f"!4m6!1m2!10m1!1e1!11m2!2s{list_id}!3e3"
            elif "/@" in shared_url and "data=" not in shared_url:
                # This might be a regular map view, not a list
                raise ValueError("This appears to be a regular map view, not a saved list. Please make sure you're sharing a saved list from Google Maps.")
            else:
                raise ValueError("Could not find data parameter in URL. Make sure this is a shared Google Maps list URL.")
        
        if not data_param:
            raise ValueError("Could not extract data parameter from URL")
        
        # Construct the raw data URL
        raw_url = f"https://google.com/maps/@/data={data_param}?ucbcb=1"
        
        self.logger.info(f"Converted URL to raw data format: {raw_url}")
        return raw_url
    
    def extract_places_from_raw_data(self, raw_url: str) -> List[ExtractedPlace]:
        """
        Extract places from the raw Google Maps data URL.
        
        Args:
            raw_url: The raw data URL obtained from convert_url_to_raw_data_url
            
        Returns:
            List of ExtractedPlace objects with coordinates and names
        """
        self.logger.info(f"Fetching raw data from: {raw_url}")
        
        try:
            # Fetch the raw data
            response = requests.get(raw_url)
            response.raise_for_status()
            
            # Process the response text
            txt = response.text
            
            # Split and extract the relevant data section
            # Based on the GitHub gist pattern
            if r")]}'" in txt:
                txt = txt.split(r")]}'")[1]
            
            # Unescape HTML entities
            txt = html.unescape(txt)
            
            # Debug logging only (raw response file removed for cleanup)
            self.logger.debug(f"Raw response length: {len(txt)} characters")
            
            # Check if this is a list metadata response rather than place data
            if '0CZ2l33STKGzwfM2FE_Ayg' in txt and len(txt) < 1000:
                self.logger.info("Detected list metadata response, trying alternative URL format...")
                
                # Extract the list ID for alternative approach
                list_id = "0CZ2l33STKGzwfM2FE_Ayg"
                
                # Try different URL formats that might give us the actual places
                alternative_urls = [
                    f"https://www.google.com/maps/preview/entitylist/getlist?listId={list_id}&hl=en",
                    f"https://www.google.com/maps/@/data=!4m6!1m2!10m1!1e1!11m2!2s{list_id}!3e3?ucbcb=1",
                    f"https://www.google.com/maps/list/{list_id}?ucbcb=1",
                ]
                
                for alt_url in alternative_urls:
                    self.logger.info(f"Trying alternative URL: {alt_url}")
                    try:
                        alt_response = requests.get(alt_url)
                        if alt_response.status_code == 200 and len(alt_response.text) > 100:
                            alt_txt = alt_response.text
                            
                            # Debug logging only (alternative response file removed for cleanup)
                            self.logger.debug(f"Alternative response {alternative_urls.index(alt_url)} length: {len(alt_txt)} characters")
                            
                            # Try to extract coordinates from this response
                            coordinates = self._extract_coordinates_from_text(alt_txt)
                            if coordinates:
                                self.logger.info(f"Found {len(coordinates)} coordinates in alternative response")
                                return self._convert_coordinates_to_places(coordinates, alt_txt)
                    except Exception as e:
                        self.logger.warning(f"Alternative URL failed: {e}")
                        continue
            
            # Try to extract coordinates using original method
            coordinates = self._extract_coordinates_from_text(txt)
            if coordinates:
                return self._convert_coordinates_to_places(coordinates, txt)
            
            self.logger.warning("No coordinates found in any response format")
            return []
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching raw data: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error processing raw data: {e}")
            raise
    
    def _extract_coordinates_from_text(self, txt: str) -> List[Tuple[str, str]]:
        """Extract coordinate pairs from text using multiple patterns."""
        
        # Try multiple regex patterns for coordinates
        patterns = [
            # Original pattern
            r'\[null,null,(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\]',
            # Alternative patterns for different formats
            r'"lat":(-?[0-9]+\.[0-9]+),"lng":(-?[0-9]+\.[0-9]+)',
            r'"latitude":(-?[0-9]+\.[0-9]+),"longitude":(-?[0-9]+\.[0-9]+)',
            r'\[(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\]',
            # Look for coordinate arrays
            r'(-?[0-9]{2}\.[0-9]{4,}),(-?[0-9]{2,3}\.[0-9]{4,})',
        ]
        
        for i, pattern in enumerate(patterns):
            results = re.findall(pattern, txt)
            if results:
                self.logger.info(f"Found {len(results)} coordinate pairs using pattern {i+1}")
                return results
        
        return []
    
    def _convert_coordinates_to_places(self, coordinates: List[Tuple[str, str]], txt: str) -> List[ExtractedPlace]:
        """Convert coordinate tuples to ExtractedPlace objects with names."""
        
        places = []
        
        for i, (lat, lng) in enumerate(coordinates):
            try:
                lat_float = float(lat)
                lng_float = float(lng)
                
                # Find the coordinate pattern in the text
                coord_pattern = f'{lat},{lng}'
                
                # Find the name associated with this coordinate
                # The name typically appears near the coordinates in the data structure
                coord_index = txt.find(coord_pattern)
                name = f"Place {i+1}"  # Default name
                
                if coord_index != -1:
                    # Look around the coordinates for quoted strings that could be names
                    search_area = txt[max(0, coord_index-500):coord_index+500]
                    
                    # Find quoted strings that could be names
                    name_matches = re.findall(r'"([^"]{3,100})"', search_area)
                    
                    # Filter for likely place names (not URLs, coordinates, etc.)
                    for potential_name in name_matches[:20]:  # Check first 20 matches
                        # Skip if it looks like a URL, coordinate, or technical data
                        if (not any(skip in potential_name.lower() for skip in 
                                   ['http', 'maps.google', 'data:', 'null', 'true', 'false']) and
                            not re.match(r'^[-0-9.,\s]+$', potential_name) and
                            len(potential_name.strip()) > 2 and
                            not potential_name.replace('.', '').replace('-', '').isdigit()):
                            name = potential_name.strip()
                            break
                
                place = ExtractedPlace(
                    name=name,
                    latitude=lat_float,
                    longitude=lng_float
                )
                places.append(place)
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"Error processing coordinate pair {lat}, {lng}: {e}")
                continue
        
        self.logger.info(f"Successfully extracted {len(places)} places")
        return places
    
    def reverse_geocode_addresses(self, places: List[ExtractedPlace]) -> List[ExtractedPlace]:
        """
        Use reverse geocoding to get full addresses for the places.
        
        Note: This would require a geocoding service API key.
        For now, this is a placeholder that could be implemented with:
        - Google Geocoding API
        - OpenStreetMap Nominatim
        - Other geocoding services
        
        Args:
            places: List of places with coordinates
            
        Returns:
            List of places with addresses filled in
        """
        self.logger.info("Reverse geocoding not implemented yet - would need API key")
        
        # For now, just construct basic addresses from coordinates
        # In a real implementation, you'd use a geocoding service here
        for place in places:
            place.address = f"Lat: {place.latitude}, Lng: {place.longitude}"
        
        return places
    
    def extract_from_shared_list(self, shared_url: str, output_file: str = "data/extracted_places.csv") -> List[ExtractedPlace]:
        """
        Main method to extract all places from a shared Google Maps list.
        
        Args:
            shared_url: The shared Google Maps list URL
            output_file: Path to save the extracted data as CSV
            
        Returns:
            List of extracted places
        """
        try:
            # Convert URL to raw data format
            raw_url = self.convert_url_to_raw_data_url(shared_url)
            
            # Extract places from raw data
            places = self.extract_places_from_raw_data(raw_url)
            
            # Optionally add full addresses (would need geocoding API)
            places = self.reverse_geocode_addresses(places)
            
            # Save to CSV
            self._save_to_csv(places, output_file)
            
            return places
            
        except Exception as e:
            self.logger.error(f"Error extracting from shared list: {e}")
            raise
    
    def _save_to_csv(self, places: List[ExtractedPlace], output_file: str) -> None:
        """Save extracted places to CSV file."""
        self.logger.info(f"Saving {len(places)} places to {output_file}")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'latitude', 'longitude', 'address']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for place in places:
                writer.writerow({
                    'name': place.name,
                    'latitude': place.latitude,
                    'longitude': place.longitude,
                    'address': place.address or ''
                })
        
        self.logger.info(f"Successfully saved data to {output_file}")


def main():
    """
    Example usage of the SharedListExtractor.
    
    To use this:
    1. Get your shared Google Maps list URL
    2. Modify the URL as instructed in the convert_url_to_raw_data_url method
    3. Run this script
    """
    
    # Example URL - replace with your actual shared list URL
    # The URL should look something like:
    # https://www.google.com/maps/@39.095963,-94.382426,12z/data=!4m3!11m2!2s...
    shared_url = "PASTE_YOUR_SHARED_LIST_URL_HERE"
    
    if shared_url == "PASTE_YOUR_SHARED_LIST_URL_HERE":
        print("Please replace the shared_url variable with your actual Google Maps shared list URL")
        return
    
    extractor = SharedListExtractor()
    
    try:
        places = extractor.extract_from_shared_list(shared_url)
        print(f"Successfully extracted {len(places)} places!")
        print("Data saved to data/extracted_places.csv")
        
        # Show first few places as preview
        for i, place in enumerate(places[:5]):
            print(f"{i+1}. {place.name} - {place.latitude}, {place.longitude}")
        
        if len(places) > 5:
            print(f"... and {len(places) - 5} more places")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 