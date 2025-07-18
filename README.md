# 🤖 LocalBase - AI MCP Agent Platform

**Professional service business automation platform with AI agents.**

## What is LocalBase?

LocalBase is a collection of **AI MCP (Model Context Protocol) agents** that automate business operations for service companies. Each agent integrates with different tools and APIs to streamline workflows.

## 🎯 Current Agents

| Agent | Purpose | Status |
|-------|---------|--------|
| **Airtable Viewer** | View, search, and export Airtable data | ✅ Working |
| **Google Maps Scraper** | Extract addresses from Google Maps lists | 🔄 Migrating |
| **Call Log Analyzer** | Analyze RingCentral call logs (90+ seconds) | 🚧 Building |
| **Property Enrichment** | Enrich addresses with property data | 🔄 Migrating |

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file with your API credentials:
```bash
# Airtable
AIRTABLE_TOKEN=your_token_here
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME="Leads and Opportunities"

# Supabase (for call logs)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ACCESS_TOKEN=your_access_token
SUPABASE_ANON_KEY=your_anon_key
```

### 3. Run Tools
```bash
# View Airtable data
python3 tools/airtable_viewer.py

# Check service health
python3 -c "from src.config import config; print(config.health_check())"
```

## 🏗️ Architecture

**Simple, professional structure:**

```
localbase/
├── agents/          # AI MCP agents
├── src/            
│   ├── services/    # External API integrations (Airtable, Supabase, etc.)
│   └── config.py    # Configuration with dependency injection
├── tools/           # CLI tools and utilities
└── data/            # Data files and outputs
```

### Service Layer Pattern
- **Services** handle external APIs (Airtable, Supabase, RingCentral)
- **Agents** use services through dependency injection
- **Tools** provide CLI interfaces for agents

## 🔒 Security

- **Environment variables**: All API tokens stored in `.env` (never committed)
- **Git ignore**: `.env` files are properly ignored
- **Service layer**: Handles authentication and rate limiting

## 📊 Current Use Cases

### Lead Management
- View and search Airtable leads
- Export data for analysis
- Track business breakdown

### Call Analysis  
- Monitor RingCentral call logs via Zapier
- Identify calls longer than 90 seconds
- Store data in Supabase for analytics

### Address Enrichment
- Scrape Google Maps addresses
- Enrich with property data
- Store results in Airtable

## 🛠️ Development

Built with **open-source quality standards**:
- Type-safe service interfaces
- Proper error handling  
- Dependency injection
- Professional logging
- Clean abstractions

## 📝 Examples

### Airtable Integration
```python
from src.config import config

# Get service (auto-configured)
airtable = config.get_service("airtable")

# Search records
records = airtable.search_records("roofing")
print(f"Found {len(records)} records")
```

### Call Log Analysis
```python
from src.config import config

# Get Supabase service
supabase = config.get_service("supabase")

# Find long calls
long_calls = supabase.get_calls_over_threshold(90)
print(f"Found {len(long_calls)} calls over 90 seconds")
```

---

**LocalBase** - Automating service businesses with AI agents. 🚀 