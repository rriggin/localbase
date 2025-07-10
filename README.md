# LocalBase

A comprehensive data management and analysis system for LocalBase business operations, featuring centralized configuration, data synchronization, and automated reporting.

## Overview

LocalBase provides tools for:
- **Data Synchronization**: Between Airtable, Roofr, and Dispatch systems
- **Business Intelligence**: Automated reporting and analytics
- **Configuration Management**: Centralized settings for all operations
- **Data Processing**: CSV analysis, field mapping, and data cleaning

## Quick Start

### Prerequisites
- Python 3.7+
- Required packages (see `requirements.txt`)
- Airtable API access
- RingCentral API access (for call analysis)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd localbase

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

#### Running Scripts
To avoid Python version issues, use the script runner:

```bash
# Using the shell script runner (recommended)
./run check_airtable_status_options.py

# Using the Python script runner
python3 scripts/run_script.py check_airtable_status_options.py

# Or set the Python executable in your environment
export PYTHON_EXECUTABLE=python3
./run check_airtable_status_options.py
```

#### Using the Configuration System

```python
from config import get_config, get_field_mapping

# Get the global config instance
config = get_config()

# Access Airtable configuration
airtable_url = config.AIRTABLE_URL
headers = config.AIRTABLE_HEADERS

# Get field mappings
email_field = get_field_mapping("airtable", "email")  # Returns "Email"
dispatch_email = get_field_mapping("dispatch", "customer_email")  # Returns "customer_email"
```

## Project Structure

```
localbase/
├── config.py              # Centralized configuration
├── load_env.py            # Environment variable loader
├── requirements.txt       # Python dependencies
├── data/                  # Data files (CSV, etc.)
├── graphs/                # Generated charts and visualizations
├── deck/                  # Presentation and documentation files
├── config/                # Configuration setup guides
│   ├── ZAPIER_INTEGRATION.md
│   └── RINGCENTRAL_SETUP.md
├── scripts/               # All Python scripts and utilities
│   ├── airtable_*.py     # Airtable integration scripts
│   ├── analyze_*.py      # Data analysis scripts
│   ├── update_*.py       # Data update scripts
│   └── ...
└── agents/                # AI agent configurations
```

## Configuration System

The `config.py` file provides centralized configuration for all LocalBase operations.

### Key Components

#### 1. Data Source Connections
```python
# Airtable
config.AIRTABLE_TOKEN
config.AIRTABLE_BASE_ID
config.AIRTABLE_TABLE_NAME
config.AIRTABLE_URL

# Data Files
config.DISPATCH_CSV_PATH  # "data/843.csv"
config.ROOFR_CSV_PATH     # "data/roofr.csv"
```

#### 2. Field Mappings
Field mappings translate between logical field names and actual field names in each system:

```python
# Instead of hardcoding "Email", use:
email_field = get_field_mapping("airtable", "email")

# Instead of hardcoding "customer_email", use:
dispatch_email = get_field_mapping("dispatch", "customer_email")
```

#### 3. Business Configuration
```python
business_config = config.get_business_config("roofmaxx_south_kc")
# Returns business-specific settings and mappings
```

## Best Practices

### 1. Always Use Field Mappings

❌ **Don't hardcode field names:**
```python
email = record["fields"]["Email"]  # Hardcoded
```

✅ **Use field mappings:**
```python
email_field = get_field_mapping("airtable", "email")
email = record["fields"][email_field]
```

### 2. Validate Configuration
```python
if not config.validate_config():
    print("Configuration validation failed")
    exit(1)
```

### 3. Use Data Source Paths

❌ **Don't hardcode file paths:**
```python
df = pd.read_csv("data/843.csv")
```

✅ **Use config paths:**
```python
df = pd.read_csv(config.DISPATCH_CSV_PATH)
```

## Common Scripts

### Data Analysis
- `scripts/analyze_aya_call_log.py` - Analyze call logs from CSV exports
- `scripts/ringcentral_api.py` - Fetch live call logs from RingCentral API
- `scripts/leads_by_source_pie_chart.py` - Generate lead source charts
- `scripts/metrics_qa.py` - Metrics Q&A system

### Data Synchronization
- `scripts/migrate_airtable_to_roofr_statuses.py` - Sync statuses between systems
- `scripts/update_blank_cities_from_sources.py` - Update city data

### Airtable Operations
- `scripts/airtable_overall_stats.py` - Generate Airtable statistics
- `scripts/check_airtable_records.py` - Validate Airtable data

## Environment Variables

For production, use environment variables for sensitive data:

```bash
# Airtable Configuration
AIRTABLE_TOKEN=your_airtable_token_here
AIRTABLE_BASE_ID=your_airtable_base_id_here
AIRTABLE_TABLE_NAME=Leads

# RingCentral Configuration (for call analysis)
RINGCENTRAL_CLIENT_ID=your_ringcentral_client_id_here
RINGCENTRAL_CLIENT_SECRET=your_ringcentral_client_secret_here
RINGCENTRAL_USERNAME=your_phone_number_or_extension
RINGCENTRAL_PASSWORD=your_ringcentral_password
RINGCENTRAL_ACCOUNT_ID=your_ringcentral_account_id

# Zapier Configuration
ZAPIER_API_KEY=your_zapier_api_key_here
ZAPIER_WEBHOOK_URL=your_zapier_webhook_url_here
ZAPIER_ROOFR_WEBHOOK_URL=your_roofr_extraction_webhook_url_here

# Python Configuration
PYTHON_EXECUTABLE=python3
```

### Quick Setup

1. **Copy the example**: `cp .env.example .env`
2. **Edit with your credentials**: Fill in your actual API keys and tokens
3. **Never commit .env**: It's already in `.gitignore`

For detailed setup instructions, see the documentation files below.

## Adding New Data Sources

To add a new data source:

1. **Add to FIELD_MAPPINGS in config.py:**
```python
"new_source": {
    "field_key": "actual_field_name",
    # ... more mappings
}
```

2. **Add to data source paths:**
```python
self.NEW_SOURCE_PATH = f"{self.DATA_DIR}/new_source.csv"
```

3. **Update get_data_source_path method:**
```python
elif source == "new_source":
    return self.NEW_SOURCE_PATH
```

## Documentation

- **Business Presentations**: See `/deck` folder for investor decks and executive summaries
- **Configuration Guides**: See `/config` folder for detailed setup instructions
  - `config/ZAPIER_INTEGRATION.md` - Complete Zapier setup and automation
  - `config/RINGCENTRAL_SETUP.md` - RingCentral API integration
- **Security**: See `SECURITY.md` for security guidelines

## Contributing

1. Follow the configuration best practices outlined above
2. Use the centralized config system for all new scripts
3. Add new field mappings to `config.py` as needed
4. Document any new data sources or business configurations

## Example Usage

See `scripts/example_config_usage.py` for complete examples of how to use the configuration system. 