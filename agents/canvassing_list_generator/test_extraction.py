#!/usr/bin/env python3
"""
Test script to extract places from the user's specific Google Maps list.
"""

from shared_list_extractor import SharedListExtractor


def main():
    # User's shared list URL for "Winterset - Longview" with 1,192 addresses
    # Updated to use the shortened Google Maps URL
    shared_url = "https://maps.app.goo.gl/bT85WjFbSkNDmRYH9"
    
    print("=== Google Maps Shared List Extractor ===")
    print(f"Processing URL: {shared_url}")
    print("\nExtracting places from your 'Winterset - Longview' list...")
    print("This should capture all 1,192 addresses (not just the 498 from web scraping)")
    print()
    
    try:
        extractor = SharedListExtractor()
        places = extractor.extract_from_shared_list(shared_url, "data/winterset_longview_all_addresses.csv")
        
        print(f"\n✅ SUCCESS! Extracted {len(places)} places from your list!")
        print(f"\nExpected: ~1,192 addresses")
        print(f"Actually got: {len(places)} addresses")
        
        if len(places) >= 1000:
            print("🎉 Excellent! We got the large dataset that web scraping couldn't capture!")
        elif len(places) > 500:
            print("✅ Good! This is more than web scraping could get (498 addresses)")
        else:
            print("⚠️  This is similar to web scraping results. Let's try a different approach.")
        
        print(f"\nData saved to: data/winterset_longview_all_addresses.csv")
        
        # Show a preview of the first few places
        if places:
            print("\nPreview of extracted places:")
            print("-" * 60)
            for i, place in enumerate(places[:10]):  # Show first 10
                print(f"{i+1:2d}. {place.name}")
                print(f"    Coordinates: {place.latitude}, {place.longitude}")
                if place.address and "Lat:" not in place.address:
                    print(f"    Address: {place.address}")
                print()
            
            if len(places) > 10:
                print(f"... and {len(places) - 10} more places")
        
        print("\nNext steps:")
        print("1. Review the CSV file: data/winterset_longview_all_addresses.csv")
        print("2. If you got ~1,192 addresses, this worked perfectly!")
        print("3. You can now use this complete dataset with your Clay workflow")
        print("4. Upload to GitHub Gist → Zapier → Clay as before")
        
        return len(places)
        
    except Exception as e:
        print(f"\n❌ Error extracting places: {e}")
        print(f"Error type: {type(e).__name__}")
        print("\nThis shortened URL format might need a different extraction approach...")
        print("Let's try following the redirect first to get the full URL.")
        return 0


if __name__ == "__main__":
    result_count = main() 