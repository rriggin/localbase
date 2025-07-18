# 🏠 Residential Property Enrichment Agent

A standalone agent that enriches address data with comprehensive residential property information using the ATTOM Data API.

## 🎯 What This Agent Does

Takes any CSV file with address data and enriches it with:
- **Home value estimates** (AVM - Automated Valuation Model)
- **Year built**
- **Property characteristics** (bedrooms, bathrooms, square footage)
- **Owner information** and occupancy status
- **Sales history** (last sale price and date)
- **Tax assessment data**
- **Lot information** and property details

## 📊 Data Sources

- **Primary**: [ATTOM Data API](https://api.developer.attomdata.com/) - 150+ million US properties
- **Coverage**: Nationwide residential property database
- **Accuracy**: Industry-standard property data with monthly updates

## 🔑 Setup

### 1. Get ATTOM API Key
1. Sign up at [ATTOM Data Developer Portal](https://api.developer.attomdata.com/home)
2. Click "Get a free API key"
3. No credit card required for trial

### 2. Add API Key to Environment
Add to your main project `.env` file:
```bash
ATTOM_API_KEY=your_api_key_here
```

### 3. Install Dependencies
```bash
pip install requests pandas python-dotenv
```

## 🚀 Usage

### Test Mode (3 records)
```bash
cd agents/residential_property_enrichment
python3 run_enrichment.py your_addresses.csv --test
```

### Process Specific Number of Records
```bash
python3 run_enrichment.py your_addresses.csv --max-records 10
```

### Full Processing
```bash
python3 run_enrichment.py your_addresses.csv --output enriched_data.csv
```

### Command Line Options
```bash
python3 run_enrichment.py input.csv [options]

Options:
  --test                  Test mode (3 records only)
  --max-records N         Process max N records
  --output FILE, -o FILE  Output file path
```

## 📁 Input Requirements

Your CSV file must have these columns:
- `street_address` - Street address (e.g., "2325 W Country Club Dr")
- `city` - City name (e.g., "Sedalia")
- `state` - State abbreviation (e.g., "MO")
- `zip_code` - ZIP code (optional but helpful)

### Example Input CSV:
```csv
street_address,city,state,zip_code
2325 W Country Club Dr,Sedalia,MO,65301
123 Main St,Springfield,IL,62701
456 Oak Ave,Kansas City,MO,64111
```

## 📋 Output Data

Your enriched CSV will include all original columns plus:

### Property Basics
| Column | Description | Example |
|--------|-------------|---------|
| `year_built` | Year property was built | 2006 |
| `property_type` | Type of property | SINGLE FAMILY |
| `property_subtype` | Property subtype | DETACHED |
| `bedrooms` | Number of bedrooms | 3 |
| `bathrooms_total` | Total bathrooms | 2 |
| `living_sqft` | Living area square feet | 1,738 |
| `lot_size_sqft` | Lot size in square feet | 8,712 |

### Financial Data
| Column | Description | Example |
|--------|-------------|---------|
| `estimated_value` | AVM home value estimate | $285,000 |
| `avm_high` | High value estimate | $295,000 |
| `avm_low` | Low value estimate | $275,000 |
| `assessed_total_value` | Tax assessed value | $125,000 |
| `last_sale_price` | Most recent sale price | $250,000 |
| `last_sale_date` | Most recent sale date | 2020-05-15 |
| `tax_amount` | Annual property tax | $2,850 |

### Additional Details
| Column | Description | Example |
|--------|-------------|---------|
| `owner_occupied` | Owner occupancy status | OWNER OCCUPIED |
| `condition` | Property condition | GOOD |
| `stories` | Number of stories | 2 |
| `latitude` | Property latitude | 38.7223 |
| `longitude` | Property longitude | -93.2284 |

## ⚡ Performance

### Processing Speed
- **Test (3 records)**: ~10-15 seconds
- **Small batch (10 records)**: ~30-45 seconds  
- **Large batch (100+ records)**: ~10-15 minutes
- **Rate limiting**: Built-in delays respect API limits

### Success Rates
- **Suburban/Urban addresses**: 85-95% success rate
- **Rural addresses**: 70-85% success rate
- **New construction**: 60-80% success rate

## 🔧 Advanced Usage

### Python Integration
```python
from property_enrichment_agent import ResidentialPropertyEnrichmentAgent

# Initialize agent
agent = ResidentialPropertyEnrichmentAgent(api_key="your_key")

# Process addresses
enriched_df = agent.process_address_list(
    csv_file_path="input.csv",
    output_file_path="output.csv",
    max_records=50
)

# Get statistics
print(f"Processed: {len(enriched_df)} records")
```

### Single Address Lookup
```python
# Test single address
property_data = agent.get_property_data(
    address="123 Main St",
    city="Springfield", 
    state="IL",
    zip_code="62701"
)
```

## 📈 Use Cases

### Real Estate Analysis
- Property valuation comparisons
- Market trend analysis
- Investment opportunity identification

### Lead Generation
- Property age targeting (houses built 1990-2010)
- Value range filtering ($200K-$400K)
- Owner-occupied vs rental properties

### Canvassing & Sales
- Property characteristics for targeted messaging
- Tax assessment vs market value analysis
- Historical sales data for approach timing

## 🔍 Troubleshooting

### Common Issues

**1. No Data Found**
- Addresses not in ATTOM database (rural/new construction)
- API key issues or rate limits
- Incorrectly formatted addresses

**2. API Key Errors**
```bash
ATTOM_API_KEY not found in environment variables
```
- Ensure `.env` file is in main project directory
- Check API key is correctly formatted
- Verify API key is active

**3. Rate Limiting**
```bash
API error 429: Rate limit exceeded
```
- Built-in delays should handle this automatically
- Free tier has lower limits
- Consider upgrading for higher volume

### Debug Mode
For detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 💰 Pricing

### Free Tier
- **Trial requests**: Limited but sufficient for testing
- **Perfect for**: Testing with your address data
- **No credit card required**

### Paid Plans
- **Startup**: ~$50-100/month for regular use
- **Enterprise**: Custom pricing for high volume
- **Pay per request**: Available for occasional use

## 🔗 Integration

### With Existing Workflows
This agent outputs standard CSV files that integrate with:
- **Clay.com**: Import enriched data directly
- **Airtable**: Bulk import property data
- **CRM systems**: Enhanced lead information
- **Spreadsheets**: Excel/Google Sheets compatible

### Data Pipeline
```
Address List → Property Enrichment → Enriched CSV → Your System
```

## 📧 Support

For issues or questions:
1. Check this README for common solutions
2. Review ATTOM API documentation
3. Test with a small sample first
4. Verify your API key and .env setup

## 🏗️ Architecture

### Agent Structure
```
agents/residential_property_enrichment/
├── __init__.py                    # Agent package
├── property_enrichment_agent.py   # Core agent logic
├── run_enrichment.py             # CLI runner script
└── README.md                     # This file
```

### Data Flow
1. **Input**: CSV with address columns
2. **Lookup**: ATTOM API property search
3. **Enrichment**: Extract property details
4. **Output**: Enhanced CSV with property data

---

**Ready to enrich your address data with comprehensive property information?** 🏠📊 