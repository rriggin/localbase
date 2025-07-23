#!/usr/bin/env python3
"""
Format addresses for gist update
Transforms the simple addresses.csv into the format expected by the gist
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, Optional

def parse_address(full_address: str) -> Dict[str, str]:
    """
    Parse a full address into components.
    Expected format: "1234 SW Street Name, City, State ZIP"
    """
    # Clean up escape characters
    address = full_address.replace('\\,', ',').replace('\\"', '"').replace('\\', '').strip()
    
    # Default values
    result = {
        'street_address': '',
        'city': '',
        'state': '',
        'zip_code': '',
        'full_address': address
    }
    
    # Try to parse the address components
    # Pattern: "street_address, city, state zip_code"
    parts = [part.strip() for part in address.split(',')]
    
    if len(parts) >= 3:
        # Street address is the first part
        result['street_address'] = parts[0]
        
        # City is the second part
        result['city'] = parts[1]
        
        # State and ZIP are in the last part
        state_zip = parts[2].strip()
        state_zip_match = re.match(r'^([A-Z]{2})\s+(\d{5}(?:-\d{4})?).*$', state_zip)
        if state_zip_match:
            result['state'] = state_zip_match.group(1)
            result['zip_code'] = state_zip_match.group(2)
    elif len(parts) == 2:
        # Try to handle "street_address, city state zip" format
        result['street_address'] = parts[0]
        city_state_zip = parts[1].strip()
        
        # Look for pattern: "City ST ZIP"
        city_state_zip_match = re.match(r'^(.+?)\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?).*$', city_state_zip)
        if city_state_zip_match:
            result['city'] = city_state_zip_match.group(1).strip()
            result['state'] = city_state_zip_match.group(2)
            result['zip_code'] = city_state_zip_match.group(3)
    
    return result

def get_list_title_from_addresses():
    """Extract list title from the addresses.csv source field."""
    input_file = 'data/addresses.csv'
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = row.get('source', '')
                if source and 'Google Maps' in source:
                    # Try to extract list title from source
                    # Format might be "Google Maps Agent - List Title"
                    if ' - ' in source:
                        return source.split(' - ', 1)[1]
                    else:
                        return "Google Maps List"
                break
    except:
        pass
    
    return "Google Maps List"

def format_addresses_for_gist(list_title: str = None):
    """
    Read addresses.csv and format it for gist update
    """
    current_time = datetime.now()
    import_date = current_time.strftime('%Y-%m-%d')
    import_time = current_time.strftime('%H:%M:%S')
    
    input_file = 'data/addresses.csv'
    output_file = 'data/addresses_formatted_for_gist.csv'
    
    # Get list title if not provided
    if not list_title:
        list_title = get_list_title_from_addresses()
    
    # Required headers for gist format
    headers = [
        'name', 'address', 'street_address', 'city', 'state', 'zip_code', 
        'full_address', 'source', 'import_date', 'import_time'
    ]
    
    addresses_processed = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()
        
        for row in reader:
            # Skip empty rows or rows without address
            if not row.get('address', '').strip():
                continue
            
            # Parse the address into components
            address_parts = parse_address(row['address'])
            
            # Create the formatted row
            formatted_row = {
                'name': row.get('name', ''),  # Use name from CSV if available
                'address': address_parts['full_address'],
                'street_address': address_parts['street_address'],
                'city': address_parts['city'],
                'state': address_parts['state'],
                'zip_code': address_parts['zip_code'],
                'full_address': address_parts['full_address'],
                'source': f'Google Maps List Scraper - {list_title}',
                'import_date': import_date,
                'import_time': import_time
            }
            
            writer.writerow(formatted_row)
            addresses_processed += 1
    
    print(f"Successfully formatted {addresses_processed} addresses")
    print(f"List title: {list_title}")
    print(f"Output saved to: {output_file}")
    
    # Show first few rows as sample
    print("\nSample of formatted data:")
    with open(output_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 5:  # Show first 5 lines (header + 4 data rows)
                print(f"  {line.strip()}")
            else:
                break

if __name__ == "__main__":
    # Allow list title to be passed as command line argument
    list_title = sys.argv[1] if len(sys.argv) > 1 else None
    format_addresses_for_gist(list_title) 