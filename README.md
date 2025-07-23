# 🤖 LocalBase - AI MCP Agent Platform

**Professional service business automation platform with AI agents and external service integrations.**

## What is LocalBase?

LocalBase is a collection of **AI MCP (Model Context Protocol) agents** and **professional service integrations** that automate business operations for service companies. The platform uses a clean service layer architecture where agents leverage external APIs through well-designed service interfaces.

## 🎯 Current Services & Agents

### 🔗 Service Integrations

| Service              | Purpose                                  | Status        | API Coverage                               |
|----------------------|------------------------------------------|---------------|--------------------------------------------|
| **Airtable**         | CRM data management and lead tracking   | ✅ Full       | Complete CRUD operations                   |
| **Supabase**         | Call log storage and analytics          | ✅ Full       | Real-time data sync                        |
| **RoofMaxx Connect** | Dealer management and lead tracking     | ✅ Full       | 4,852 dealers, pagination, search         |
| **ATTOM Data**       | Property data enrichment and valuation  | ✅ Full       | Property details, AVM, tax records        |
| **RingCentral**      | Business communications and call logs   | ✅ Core       | Call data, SMS, voicemail                 |
| **Zapier**           | Workflow automation and webhooks        | ✅ Core       | Webhook triggers, batch processing        |
| **Clay.com**         | Data enrichment workflows               | 🔄 Migrating  | Import/export, field mapping              |

### 🤖 AI Agents  

| Agent                   | Purpose                                   | Status       | Uses Services              |
|-------------------------|-------------------------------------------|--------------|----------------------------|
| **Google Maps Agent**   | Extract addresses from Google Maps lists | ✅ Working   | GitHub Gist, Zapier       |
| **RoofMaxx Data Agent** | Conversational business intelligence     | ✅ Working   | Supabase, Analytics        |

## 🤖 How Agents Work

### Agent Architecture

LocalBase agents follow a **professional, standardized architecture** built on the `BaseAgent` interface:

```python
from agents.base_agent import BaseAgent, AgentResult, AgentError

class MyAgent(BaseAgent):
    VERSION = "1.0.0"
    
    def __init__(self, config, services=None):
        super().__init__(config, services)
        # Agent-specific initialization
    
    def validate_input(self, **kwargs) -> bool:
        # Validate input parameters
        pass
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        # Main agent logic
        pass
```

### Key Agent Features

- **🔧 Dependency Injection**: Agents receive services through constructor injection
- **✅ Input Validation**: Built-in parameter validation with clear error messages
- **📊 Standardized Results**: All agents return `AgentResult` objects
- **🛡️ Error Handling**: Professional exception handling with error codes
- **📝 Logging**: Automatic logging with agent-specific loggers
- **📈 Monitoring**: Built-in status and metadata tracking

### Agent Usage Patterns

#### 1. Programmatic Agent Execution

```python
from agents.canvassing_list_generator.agent import GoogleMapsAgent
from src.config import config

# Get required services
airtable_service = config.get_service("airtable")

# Initialize agent with services
agent = GoogleMapsAgent(
    config={"timeout": 30},
    services={"airtable": airtable_service}
)

# Execute agent
result = agent.execute(
    list_url="https://maps.app.goo.gl/qr1Y6sFwU58MU4Sm7",
    headless=True,
    save_to_airtable=True,
    business_name="Winterset - Longview"
)

if result.success:
    print(f"✅ Extracted {len(result.data)} addresses")
    print(f"📊 Saved to Airtable: {result.metadata.get('airtable_records', 0)} records")
else:
    print(f"❌ Error: {result.error}")
```

#### 2. Conversational Agent Interface

```python
from agents.roofmaxx_data_agent.agent import RoofMaxxDataAgent

# Initialize conversational agent
agent = RoofMaxxDataAgent()

# Chat with your business data
response = agent.chat("Show me deals by source for this month")
print(response)

# Generate reports
agent.chat("Create a pie chart of deal sources")
# Saves report to data/outputs/reports/
```

#### 3. Agent Status & Monitoring

```python
# Check agent status
status = agent.get_status()
print(f"Agent: {status['metadata']['agent_name']}")
print(f"Version: {status['metadata']['version']}")
print(f"Services: {status['services']}")
print(f"Config: {status['config_keys']}")
```

### Agent-Specific Examples

#### Google Maps Agent

**Purpose**: Extract addresses from Google Maps lists for canvassing campaigns

```python
from agents.canvassing_list_generator.agent import GoogleMapsAgent

agent = GoogleMapsAgent(config={}, services={"airtable": airtable_service})

# Extract addresses from a Google Maps list
result = agent.execute(
    list_url="https://maps.app.goo.gl/qr1Y6sFwU58MU4Sm7",
    headless=True,
    timeout=30,
    save_to_airtable=True,
    business_name="Winterset - Longview"
)

# Result contains:
# - success: bool
# - data: List of extracted addresses
# - metadata: Processing stats, Airtable records created
# - error: Error message if failed
```

**Features**:
- 🕷️ **Web Scraping**: Uses Selenium for reliable address extraction
- 📍 **Address Processing**: Cleans and validates extracted addresses
- 🗄️ **Airtable Integration**: Automatically saves to CRM
- 📊 **Progress Tracking**: Real-time extraction progress
- 🔄 **Error Recovery**: Handles network issues and timeouts

#### RoofMaxx Data Agent

**Purpose**: Conversational business intelligence for deal analysis

```python
from agents.roofmaxx_data_agent.agent import RoofMaxxDataAgent

agent = RoofMaxxDataAgent()

# Natural language queries
agent.chat("What's my total revenue this month?")
agent.chat("Show me deals by city")
agent.chat("Which sources are performing best?")

# Generate visual reports
agent.chat("Create a pie chart of deal sources")
agent.chat("Show me a weekly revenue trend")
```

**Features**:
- 💬 **Natural Language**: Chat with your data using plain English
- 📊 **Visual Reports**: Automatic chart and graph generation
- 📈 **Real-time Analytics**: Live data from Supabase
- 🎯 **Business Insights**: Performance metrics and trends
- 📄 **Report Export**: HTML dashboards and charts

#### Property Enrichment Service

**Purpose**: Enrich addresses with property data from ATTOM

```python
from src.services.attom import AttomService

# Initialize ATTOM service
attom_service = AttomService(config={"api_key": "your_key"})

# Enrich addresses with property data
enriched_data = attom_service.enrich_addresses(
    addresses=["123 Main St, City, State"],
    include_valuation=True,
    include_characteristics=True
)

# Enriched data includes:
# - Property valuations
# - Square footage
# - Year built
# - Property characteristics
# - Market data
```

### Agent Development Guide

#### Creating a New Agent

1. **Extend BaseAgent**:
```python
from agents.base_agent import BaseAgent, AgentResult, AgentError

class MyNewAgent(BaseAgent):
    VERSION = "1.0.0"
    
    def __init__(self, config, services=None):
        super().__init__(config, services)
        # Validate required services
        if 'required_service' not in self.services:
            raise AgentError("Missing required service", "missing_service")
    
    def validate_input(self, **kwargs) -> bool:
        if 'required_param' not in kwargs:
            raise ValueError("'required_param' is required")
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        self.validate_input(**kwargs)
        
        try:
            # Agent logic here
            result_data = self._process_data(kwargs['required_param'])
            
            return AgentResult(
                success=True,
                data=result_data,
                metadata={"processed_items": len(result_data)}
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"error_type": type(e).__name__}
            )
```

2. **Add to Agent Registry**:
```python
# In agents/__init__.py
from .my_new_agent import MyNewAgent

__all__ = ['MyNewAgent']
```

3. **Create Run Script**:
```python
# agents/my_new_agent/run.py
from .agent import MyNewAgent
from src.config import config

def main():
    # Get services
    services = {
        "airtable": config.get_service("airtable"),
        "supabase": config.get_service("supabase")
    }
    
    # Initialize agent
    agent = MyNewAgent(config={}, services=services)
    
    # Execute
    result = agent.execute(required_param="value")
    print(f"Result: {result.to_dict()}")

if __name__ == "__main__":
    main()
```

#### Agent Testing

```python
import unittest
from agents.my_new_agent import MyNewAgent

class TestMyNewAgent(unittest.TestCase):
    def setUp(self):
        self.agent = MyNewAgent(config={}, services={})
    
    def test_validate_input(self):
        # Test valid input
        self.assertTrue(self.agent.validate_input(required_param="test"))
        
        # Test invalid input
        with self.assertRaises(ValueError):
            self.agent.validate_input()
    
    def test_execute(self):
        result = self.agent.execute(required_param="test")
        self.assertIsInstance(result, AgentResult)
        self.assertTrue(result.success)
```

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

### 3. Run Agents

#### Google Maps Agent
```bash
# Extract addresses from Google Maps list
python3 agents/canvassing_list_generator/run.py
```

#### RoofMaxx Data Agent
```bash
# Start conversational business intelligence
python3 agents/roofmaxx_data_agent/run.py
```

#### Property Enrichment Service
```bash
# Enrich addresses with property data
python3 src/services/attom/run_enrichment.py addresses.csv
```

### 4. Run Tools & Demos
```bash
# View Airtable data
python3 tools/airtable_viewer.py

# Demo RoofMaxx Connect service
python3 src/services/roofmaxxconnect/demo.py

# Test service integrations
python3 src/services/roofmaxxconnect/test_service.py
```

## 🏗️ Architecture

**Professional service-oriented architecture:**

```
localbase/
├── agents/                    # 🤖 AI MCP agents
│   ├── base_agent.py         # Base agent interface & standards
│   ├── canvassing_list_generator/  # Google Maps address extraction
│   │   ├── agent.py          # Main agent implementation
│   │   ├── run.py            # CLI execution script
│   │   └── README.md         # Agent-specific documentation
│   └── roofmaxx_data_agent/  # Conversational business intelligence
│       ├── agent.py          # Main agent implementation
│       ├── run.py            # CLI execution script
│       └── README.md         # Agent-specific documentation
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

### 🤖 Agent Standardization
- **BaseAgent Interface**: All agents now follow standardized patterns
- **Dependency Injection**: Clean service integration
- **Error Handling**: Professional exception management
- **Monitoring**: Built-in status and metadata tracking
- **Documentation**: Comprehensive agent usage guides

---

**LocalBase** - Automating service businesses with professional AI agents and service integrations. 🚀 