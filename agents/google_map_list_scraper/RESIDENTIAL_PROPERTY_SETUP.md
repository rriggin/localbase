# Residential Property Enrichment Agent Setup

## 🏠 Overview
This agent enriches your address data with comprehensive residential property information including:
- **Home value estimates** (AVM)
- **Year built**
- **Property characteristics** (beds, baths, sqft)
- **Owner information**
- **Sales history**
- **Tax assessment data**

## 🔑 API Setup (ATTOM Data)

### Step 1: Get Your Free API Key
1. Go to [ATTOM Data Developer Portal](https://api.developer.attomdata.com/home)
2. Click **"Get a free API key"**
3. Sign up for a free account
4. Get your API key from the dashboard

### Step 2: Add API Key to Environment
Add this line to your main project `.env` file:
```bash
# ATTOM Data API Key (for residential property data)
ATTOM_API_KEY=your_api_key_here
```

## 📊 What Data You'll Get

### Property Basics
- Year built
- Property type (Single Family, Condo, etc.)
- Building square footage
- Lot size
- Number of bedrooms/bathrooms

### Financial Information
- **Estimated home value** (AVM)
- Value range (high/low estimates)
- Assessed value (tax assessment)
- Last sale price and date
- Annual tax amount

### Additional Details
- Owner occupancy status
- Property condition
- Construction details
- Location coordinates

## 🚀 Usage

### Test Mode (3 records)
```bash
cd agents/google_map_list_scraper
python3 run_residential_enrichment.py --test
```

### Process Specific Number
```bash
python3 run_residential_enrichment.py --max-records 10
```

### Full Processing (All 166 addresses)
```bash
python3 run_residential_enrichment.py --full
```

## 📁 Output Files

### Test Output
- `data/addresses_enriched_residential_test.csv` - Test results (3 records)

### Full Output
- `data/addresses_enriched_residential_property_data.csv` - All enriched data

## 📋 Sample Output Data

Your enriched CSV will include all original columns plus:

| Column | Description | Example |
|--------|-------------|---------|
| `year_built` | Year property was built | 2006 |
| `estimated_value` | AVM home value estimate | 285000 |
| `bedrooms` | Number of bedrooms | 3 |
| `bathrooms_total` | Total bathrooms | 2 |
| `living_sqft` | Living area square feet | 1738 |
| `property_type` | Type of property | SINGLE FAMILY |
| `assessed_total_value` | Tax assessed value | 125000 |
| `last_sale_price` | Most recent sale price | 275000 |
| `last_sale_date` | Most recent sale date | 2020-05-15 |
| `tax_amount` | Annual property tax | 2850 |
| `owner_occupied` | Owner occupancy status | OWNER OCCUPIED |

## 💰 ATTOM Data Pricing

### Free Tier
- **Free trial** with limited requests
- Perfect for testing with your 166 addresses
- No credit card required for trial

### Paid Plans
- **Startup Plan**: ~$50-100/month for higher volume
- **Enterprise**: Custom pricing for large scale

## ⚡ Performance

### Processing Time
- **3 records**: ~30 seconds
- **166 records**: ~15-20 minutes
- Rate limited to ~1 request per second

### Success Rate
- ATTOM has 150+ million US properties
- Expect 80-95% match rate for residential addresses
- Rural/new construction may have lower coverage

## 🔧 Troubleshooting

### Common Issues
1. **No API key**: Add `ATTOM_API_KEY` to your `.env` file
2. **Rate limits**: Built-in delays handle this automatically
3. **No data found**: Some addresses may not be in database
4. **Free tier limits**: Contact ATTOM for higher quotas

### Debug Mode
Add more logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Next Steps

Once you have enriched data, you can:
1. **Import to Clay.com** - Use your existing workflow
2. **Analyze property values** - Find high/low value properties
3. **Target by age** - Focus on properties by year built
4. **Size filtering** - Target by square footage or bedrooms
5. **Market analysis** - Compare estimated vs assessed values

## 🔄 Integration with Clay Workflow

The enriched CSV maintains all your original columns, so it works seamlessly with your existing Clay automation:

```
Addresses → ATTOM Enrichment → Clay Import
```

Your Zapier workflow will now have property data for each address!

## 🆚 Why ATTOM vs Other APIs

| Feature | ATTOM | RentCast | Zillow |
|---------|-------|----------|--------|
| **Residential Focus** | ✅ Excellent | ❌ Rental focused | ⚠️ Limited API |
| **Year Built** | ✅ Yes | ✅ Yes | ⚠️ Limited |
| **Home Values** | ✅ AVM | ❌ Rental values | ✅ Zestimate |
| **Free Tier** | ✅ Trial available | ✅ 50/month | ❌ Very limited |
| **Coverage** | ✅ 150M+ properties | ✅ 140M+ | ✅ ~100M |
| **Data Quality** | ✅ Industry standard | ⚠️ Newer | ✅ Well known |

**Verdict**: ATTOM is the best choice for residential property enrichment! 