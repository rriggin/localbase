#!/usr/bin/env python3
"""
Runner script for the SharedListExtractor

This script makes it easy to extract all addresses from a shared Google Maps list.
This should work for large lists (like your 1,192 addresses) that the regular 
web scraping can't fully capture.
"""

from shared_list_extractor import SharedListExtractor


def main():
    print("=== Google Maps Shared List Extractor ===")
    print()
    print("This tool extracts ALL places from a shared Google Maps list,")
    print("even large lists with 1000+ addresses that web scraping can't capture.")
    print()
    
    # Get the shared list URL from user
    print("Please provide your shared Google Maps list URL.")
    print("It should look something like:")
    print("https://www.google.com/maps/@39.095963,-94.382426,12z/data=!4m3!11m2!2s...")
    print()
    
    shared_url = input("Enter your shared list URL: ").strip()
    
    if not shared_url:
        print("No URL provided. Exiting.")
        return
    
    # Validate URL format
    if not ("google.com/maps" in shared_url and "data=" in shared_url):
        print("Error: This doesn't look like a valid Google Maps shared list URL.")
        print("Make sure you're using the shared link from your Google Maps list.")
        return
    
    print(f"\nProcessing URL: {shared_url}")
    print("\nExtracting places... This may take a moment.")
    
    try:
        extractor = SharedListExtractor()
        places = extractor.extract_from_shared_list(shared_url)
        
        print(f"\n✅ SUCCESS! Extracted {len(places)} places from your list!")
        print("\nData saved to: data/extracted_places.csv")
        
        # Show a preview of the first few places
        if places:
            print("\nPreview of extracted places:")
            print("-" * 50)
            for i, place in enumerate(places[:10]):  # Show first 10
                print(f"{i+1:2d}. {place.name}")
                print(f"    Coordinates: {place.latitude}, {place.longitude}")
                if place.address and "Lat:" not in place.address:
                    print(f"    Address: {place.address}")
                print()
            
            if len(places) > 10:
                print(f"... and {len(places) - 10} more places")
        
        print("\nNext steps:")
        print("1. Check the CSV file: data/extracted_places.csv")
        print("2. The file contains name, latitude, longitude for each place")
        print("3. You can use these coordinates to reverse geocode full addresses if needed")
        print("4. This data can now be used with your existing Clay workflow!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error extracting places: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the list is shared publicly or with 'anyone with the link'")
        print("2. Try copying the URL again from Google Maps")
        print("3. Make sure the URL contains 'data=' parameter")
        return False


if __name__ == "__main__":
    main() 