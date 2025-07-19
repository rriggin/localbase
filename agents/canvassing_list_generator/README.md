# 🗺️ Canvassing List Generator Agent

**Professional Google Maps list extraction and address processing for sales canvassing operations**

## Overview

The Canvassing List Generator Agent extracts addresses from Google Maps lists and processes them into actionable prospect lists for sales teams. It handles both public and shared Google Maps lists, with advanced extraction capabilities that can retrieve complete datasets (1,000+ addresses) that web scraping alone cannot access.

## Features

- 🗺️ **Google Maps Extraction** - Extract addresses from public and shared lists
- 📊 **Multiple Data Sources** - Support for different list types and sharing methods  
- 🎯 **Professional Architecture** - Built on BaseAgent with dependency injection
- 📝 **Multi-format Output** - CSV, Airtable, and Gist integration
- 🔗 **Service Integration** - Connects to Airtable for CRM storage
- ⚡ **Batch Processing** - Handle large lists efficiently

## Quick Start

```bash
# From the project root
python3 agents/canvassing_list_generator/run.py

# Or run specific extraction methods
python3 agents/canvassing_list_generator/run_scraper.py
python3 agents/canvassing_list_generator/run_shared_list_extractor.py
```

## Available Scripts

### **Core Scripts**
- `agent.py` - Main GoogleMapsAgent class (professional architecture)
- `run.py` - Convenience runner and usage examples

### **Extraction Methods**
- `run_scraper.py` - Extract from standard Google Maps lists (~500 addresses)
- `run_shared_list_extractor.py` - Extract from shared lists (1,000+ addresses)
- `scraper.py` - Core web scraping functionality
- `shared_list_extractor.py` - Advanced API-based extraction

### **Data Processing**  
- `kick_off_new_list.py` - Start new list processing workflow
- `format_for_gist.py` - Format data for GitHub Gist sharing
- `public_csv_upload.py` - Upload processed data to public repositories
- `update_gist.py` - Update existing Gist with new data

### **Testing & Utilities**
- `test_extraction.py` - Test extraction methods
- `dynamic_list_scraper.py` - Dynamic scraping capabilities
- `google_maps_api_scraper.py` - API-based scraping methods

## Data Processing Pipeline

```mermaid
graph LR
    A[Google Maps List] --> B[Extract Addresses]
    B --> C[Validate & Clean]
    C --> D[Enrich Data]
    D --> E[Output Format]
    E --> F[Airtable/CSV/Gist]
```

## Usage Examples

### **Professional Agent (Recommended)**
```python
from agents.canvassing_list_generator import GoogleMapsAgent

# Initialize with config and services
config = {
    'list_url': 'https://maps.app.goo.gl/your-list-url',
    'output_format': 'airtable'
}

services = {
    'airtable': AirtableService(config)
}

agent = GoogleMapsAgent(config, services)
result = agent.process_google_maps_list(config['list_url'])
```

### **Quick Extraction**
```bash
# Extract from a shared list (handles 1,000+ addresses)
python3 run_shared_list_extractor.py

# Extract from standard list (up to ~500 addresses)  
python3 run_scraper.py
```

## List Types Supported

### **1. Standard Google Maps Lists**
- Public lists created in Google Maps
- Limited to ~500 visible addresses
- Uses web scraping method

### **2. Shared Google Maps Lists** ⭐ **Recommended**
- Lists shared with "Anyone with the link" 
- Access to complete datasets (1,000+ addresses)
- Uses API extraction method
- See: `SHARED_LIST_EXTRACTION_GUIDE.md`

## Configuration

The agent requires:
- **Airtable credentials** (for CRM integration)
- **Google Maps list URLs**
- **Output preferences** (CSV, Airtable, Gist)

See main project `.env` file for configuration details.

## Output Data Structure

Extracted addresses include:
- **Address** - Full street address
- **Name** - Business/location name (if available)
- **Coordinates** - Latitude/longitude
- **Validation Status** - Address verification
- **Enrichment Data** - Additional property information

## Integration

- **Airtable** - Direct CRM storage via AirtableService
- **CSV Export** - Local file storage in `data/` folder
- **GitHub Gist** - Public list sharing and collaboration
- **Clay.com** - Data enrichment workflows (via separate service)

## Real-World Example

Successfully extracted **1,192 addresses** from "Winterset - Longview" shared list:
[[memory:3478737]]

> "This method extracts ALL addresses from shared Google Maps lists by accessing the raw API data, not just what's visible on the page."

## Dependencies

- Selenium (web scraping)
- BeautifulSoup (HTML parsing)  
- Pandas (data processing)
- Airtable API (CRM integration)
- Google Maps integration 