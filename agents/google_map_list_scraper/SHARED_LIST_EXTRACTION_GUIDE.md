# Google Maps Shared List Extraction Guide

## Overview

This new method extracts **ALL** addresses from shared Google Maps lists by accessing the raw API data, not just what's visible on the page. This should work for your 1,192 address list in Lee's Summit, MO.

## Why This Method Works Better

- **Web scraping limitation**: Only captures ~500 addresses that are initially loaded
- **Shared list extraction**: Accesses the complete raw data containing all 1,192 addresses
- **No pagination issues**: Gets everything in one request

## How to Use

### Step 1: Get Your Shared List URL

1. Open your "Winterset - Longview" list in Google Maps
2. Click the **Share** button 
3. Make sure sharing is set to "Anyone with the link"
4. Copy the shared URL

The URL should look like:
```
https://www.google.com/maps/@39.095963,-94.382426,12z/data=!4m3!11m2!2s...
```

### Step 2: Run the Extractor

```bash
cd /Users/ryanriggin/Code/localbase/agents/google_map_list_scraper
python run_shared_list_extractor.py
```

### Step 3: Paste Your URL

When prompted, paste your shared list URL and press Enter.

### Step 4: Review Results

The tool will:
- Extract all places from your list
- Save results to `data/extracted_places.csv`
- Show you a preview of the extracted data

## Output Format

The CSV file will contain:
- **name**: Place name or address
- **latitude**: GPS latitude 
- **longitude**: GPS longitude
- **address**: Full address (if available)

## Next Steps

1. **Review the CSV**: Check that you got all ~1,192 addresses
2. **Reverse geocoding**: If you need full street addresses, we can add reverse geocoding
3. **Clay integration**: Use the CSV with your existing Clay workflow
4. **GitHub Gist upload**: Continue with your existing Zapier → Clay process

## Troubleshooting

**If you get fewer than 1,192 results:**
- Make sure the list is shared with "Anyone with the link"
- Try copying the URL again
- Check that the URL contains the `data=` parameter

**If the extraction fails:**
- Verify the URL format is correct
- Make sure you have internet connectivity
- The list might have changed since you shared it

## Technical Details

This method:
1. Converts your shared URL to a raw data URL
2. Fetches the complete JSON response from Google
3. Extracts coordinates and names using regex patterns
4. Saves everything to CSV format

Based on: https://gist.github.com/ByteSizedMarius/8c9df821ebb69b07f2d82de01e68387d 