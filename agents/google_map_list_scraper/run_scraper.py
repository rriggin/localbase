#!/usr/bin/env python3
"""
Simple script to run the Google Maps List Scraper with a specific URL.
"""

import sys
import os

# Add the parent directory to the path so we can import the scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_map_list_scraper.scraper import GoogleMapsListScraper


def main():
    """Run the scraper with the specific Google Maps list URL."""
    
    # Your specific Google Maps list URL - Winterset-Longview (1,192 places)
    list_url = "https://maps.app.goo.gl/bT85WjFbSkNDmRYH9"
    
    # Create scraper instance (set headless=False to see the browser in action)
    scraper = GoogleMapsListScraper(headless=False, timeout=15)
    
    try:
        print("Starting Google Maps List Scraper...")
        scraper.start()
        
        print(f"Scraping addresses from: {list_url}")
        addresses = scraper.scrape_addresses(list_url)
        
        if addresses:
            print(f"\nFound {len(addresses)} addresses:")
            print("-" * 50)
            
            for i, item in enumerate(addresses, 1):
                print(f"{i}. {item.address}")
                if item.name:
                    print(f"   Name: {item.name}")
                print()
            
            # Save results to agent's data folder
            output_dir = "data"
            os.makedirs(output_dir, exist_ok=True)
            
            csv_file = os.path.join(output_dir, "addresses.csv")
            scraper.save_to_csv(addresses, csv_file)
            
            print(f"Results saved to: {csv_file}")
            
        else:
            print("No addresses found in the list.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.stop()
        print("Scraper stopped.")


if __name__ == "__main__":
    main() 