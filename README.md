# 🤖 LocalBase - AI MCP Agent Platform

**Professional service business automation platform with AI agents and external service integrations.**

## What is LocalBase?

LocalBase is a collection of **AI MCP (Model Context Protocol) agents** and **professional service integrations** that automate business operations for service companies. The platform uses a clean service layer architecture where agents leverage external APIs through well-designed service interfaces.

## 🎯 Current Services & Agents

### 🔗 Service Integrations
| Service | Purpose | Status | API Coverage |
|---------|---------|--------|--------------|
| **Airtable** | CRM data management and lead tracking | ✅ Full | Complete CRUD operations |
| **Supabase** | Call log storage and analytics | ✅ Full | Real-time data sync |
| **RoofMaxx Connect** | Dealer management and lead tracking | ✅ Full | 4,852 dealers, pagination, search |
| **Zapier** | Workflow automation and webhooks | ✅ Core | Webhook triggers, batch processing |
| **Clay.com** | Data enrichment workflows | 🔄 Migrating | Import/export, field mapping |

### 🤖 AI Agents  
| Agent | Purpose | Status | Uses Services |
|-------|---------|--------|---------------|
| **Airtable Viewer** | View, search, and export Airtable data | ✅ Working | Airtable |
| **Google Maps Scraper** | Extract addresses from Google Maps lists | ✅ Working | File I/O |
| **Call Log Analyzer** | Analyze RingCentral call logs (90+ seconds) | ✅ Working | Supabase, Zapier |
| **Property Enrichment** | Enrich addresses with ATTOM property data | ✅ Working | Airtable, File I/O |

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

# RoofMaxx Connect
ROOFMAXX_CONNECT_TOKEN=your_bearer_token
ROOFMAXX_CONNECT_DEALER_ID=your_dealer_id

# ATTOM Data (for property enrichment)
ATTOM_API_KEY=your_api_key
```

### 3. Run Tools & Demos
```bash
# View Airtable data
python3 tools/airtable_viewer.py

# Demo RoofMaxx Connect service
python3 src/services/roofmaxxconnect/demo.py

# Test service integrations
python3 src/services/roofmaxxconnect/test_service.py

# Property enrichment
python3 src/services/attom/run_enrichment.py addresses.csv
```

## 🏗️ Architecture

**Professional service-oriented architecture:**

```
localbase/
├── agents/                    # AI MCP agents
│   ├── base_agent.py         # Base agent interface
│   └── canvassing_list_generator/  # Google Maps & address agents
├── src/
│   ├── services/             # 🔥 External API service integrations
│   │   ├── airtable/        # CRM & lead management  
│   │   ├── supabase/        # Call log analytics
│   │   ├── roofmaxxconnect/ # 🆕 Dealer management (4,852 dealers)
│   │   ├── attom/           # Property data enrichment
│   │   ├── clay/            # Data enrichment workflows  
│   │   └── zapier/          # Workflow automation
│   ├── utils/               # Shared utilities
│   └── config.py            # Service registry & dependency injection
├── tools/                   # CLI tools and utilities
└── data/                    # Data files and outputs
```

### Service Layer Pattern
- **Services** handle external APIs with professional error handling and type safety
- **Agents** use services through dependency injection for clean separation
- **Service Registry** provides automatic service discovery and configuration
- **Tools** provide CLI interfaces and demonstrations

## 🔒 Security & Best Practices

- **Environment variables**: All API tokens stored in `.env` (never committed)
- **Service authentication**: Bearer tokens, API keys properly managed
- **Rate limiting**: Built-in respect for API rate limits
- **Error handling**: Professional exception handling with retries
- **Type safety**: Full TypeScript-style type hints for Python
- **Logging**: Professional logging with service-specific loggers

## 📊 Current Use Cases

### Lead & Dealer Management
- **RoofMaxx Connect**: Access 4,852+ dealer records with full pagination
- **Airtable**: View, search, and export lead data
- **Integration**: Sync dealer data across platforms

### Call Analytics & Automation
- Monitor RingCentral call logs via Zapier webhooks
- Identify calls longer than 90 seconds for quality analysis
- Store analytics data in Supabase for real-time dashboards

### Address & Property Intelligence
- Scrape Google Maps address lists for canvassing
- Enrich addresses with ATTOM property data (valuations, characteristics)
- Store enriched data in Airtable for sales team usage

### Workflow Automation
- Zapier webhook triggers for real-time data sync
- Clay.com data enrichment pipelines
- Automated field mapping and data transformation

## 🛠️ Development

Built with **enterprise-quality standards**:
- 🏗️ **Clean Architecture**: Service layer pattern with dependency injection
- 🔒 **Type Safety**: Full type hints and dataclass models  
- 🛡️ **Error Handling**: Custom exceptions with proper error context
- 📊 **Monitoring**: Health checks and performance metrics
- 🔄 **Pagination**: Automatic handling of large datasets
- 🧪 **Testing**: Comprehensive test suites and demo scripts

## 📝 Service Examples

### RoofMaxx Connect Integration
```python
from src.services.roofmaxxconnect import RoofmaxxConnectService

# Initialize service
config = {'bearer_token': 'your_token'}
service = RoofmaxxConnectService(config)

# Get dealers with pagination
dealers = service.get_dealers(page=1, per_page=100)
print(f"Found {dealers.meta.total:,} total dealers")

# Search active dealers
active_dealers = service.search_dealers("active")
for dealer in active_dealers:
    print(f"{dealer.brand_name} - {dealer.microsite_url}")
```

### Airtable Integration
```python
from src.config import config

# Get service (auto-configured from environment)
airtable = config.get_service("airtable")

# Search records with type safety
records = airtable.search_records("roofing")
print(f"Found {len(records)} records")

# Get specific record
lead = airtable.get_record_by_id("rec123")
print(f"Lead: {lead.get_field('Customer Name')}")
```

### Call Log Analysis
```python
from src.config import config

# Get Supabase service
supabase = config.get_service("supabase")

# Find calls over threshold with analytics
long_calls = supabase.get_calls_over_threshold(90)
print(f"Found {len(long_calls)} calls over 90 seconds")

# Store new call log
call_record = CallLogRecord(
    call_id="call_123",
    duration=120,
    result="Connected"
)
supabase.insert_call_log(call_record)
```

### Service Registry Usage
```python
from src.services import get_service, list_services

# List all available services
services = list_services()
print(f"Available services: {services}")
# Output: ['airtable', 'supabase', 'roofmaxxconnect', 'zapier']

# Get service dynamically
RoofmaxxService = get_service('roofmaxxconnect')
service = RoofmaxxService(config)
```

## 🎯 Recent Updates

### ✨ New Service: RoofMaxx Connect
- **4,852 dealer records** with full API access
- **Professional pagination** handling large datasets  
- **Search and filtering** capabilities
- **Type-safe models** for dealer and deal data
- **Ready for agent integration** following BaseService patterns

### 🏗️ Service Architecture Migration
- Moved key functionality from standalone agents to reusable services
- Implemented service registry for dependency injection
- Added comprehensive error handling and logging
- Enhanced type safety across all service interfaces

---

**LocalBase** - Automating service businesses with professional AI agents and service integrations. 🚀 