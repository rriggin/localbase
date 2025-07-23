# 📊 D3.js Visualization Service

Professional service for generating dynamic D3.js charts and visualizations using your existing data sources.

## 🎯 What This Service Does

- ✅ **Dynamic Chart Generation** - Create interactive D3.js visualizations
- ✅ **Template-Based** - Uses Jinja2 templates for flexible chart rendering  
- ✅ **Multiple Chart Types** - Pie charts, bar charts, sunburst, icicle, etc.
- ✅ **Data Integration** - Works with your existing Supabase data
- ✅ **Professional Output** - Generates complete HTML files with D3.js

## 🚀 Quick Start

### Generate RoofMaxx Deals Pie Chart
```bash
python3 tools/generate_deals_pie_chart.py
```

### Using the Service Directly
```python
from src.services.d3.client import D3Service
from src.services.d3.models import ChartConfig, ChartData, ChartType, DataFormat

# Initialize service
d3_service = D3Service({
    'output_dir': 'data/visualizations',
    'save_files': True
})

# Create pie chart configuration
config = ChartConfig(
    chart_type=ChartType.PIE_CHART,
    title="My Pie Chart",
    data_format=DataFormat.TABULAR
)

# Prepare data
data = ChartData(
    data=[
        {'dealtype': 'NAP', 'count': 304},
        {'dealtype': 'NAP-L', 'count': 146},
        # ... more data
    ],
    format=DataFormat.TABULAR
)

# Generate chart
result = d3_service.create_chart(config, data)
```

## 📋 Supported Chart Types

| Chart Type | Description | Data Format | Status |
|------------|-------------|-------------|---------|
| **Pie Chart** | Circular segments showing proportions | Tabular | ✅ Ready |
| **Bar Chart** | Rectangular bars for comparisons | Tabular | 🔄 Planned |
| **Sunburst** | Hierarchical radial chart | Hierarchical | 🔄 Planned |
| **Icicle** | Hierarchical rectangular chart | Hierarchical | 🔄 Planned |

## 🏗️ Service Architecture

### File Structure
```
src/services/d3/
├── __init__.py              # Service package
├── client.py                # Main D3Service class
├── models.py                # Data models and configurations
├── exceptions.py            # Custom exceptions
├── templates/               # Chart templates
│   ├── __init__.py
│   ├── manager.py          # Template management
│   └── pie_chart.html      # Pie chart template
└── README.md               # This documentation
```

### Key Components

**`D3Service`** - Main service class
- Chart generation and rendering
- Template management
- File output handling

**`ChartConfig`** - Chart configuration model
- Dimensions, colors, interactions
- Animation settings
- Custom options

**`ChartData`** - Data container model  
- Multiple format support
- Metadata handling
- Validation

## 📊 Data Formats

### Tabular Data (Pie Charts, Bar Charts)
```python
data = [
    {'dealtype': 'NAP', 'count': 304},
    {'dealtype': 'RMCL', 'count': 95},
    {'dealtype': 'GRML', 'count': 74}
]
```

### Hierarchical Data (Sunburst, Icicle)
```python
data = {
    'name': 'root',
    'children': [
        {
            'name': 'Category A',
            'children': [
                {'name': 'Item 1', 'value': 100},
                {'name': 'Item 2', 'value': 200}
            ]
        }
    ]
}
```

## 🎨 Chart Features

### Interactive Elements
- **Hover Effects** - Tooltips with detailed information
- **Click Handlers** - Custom interactions per chart type
- **Animations** - Smooth transitions and loading effects
- **Responsive Design** - Scales to different screen sizes

### Visual Customization
- **Color Schemes** - D3 color scales and custom palettes
- **Dimensions** - Configurable width, height, margins
- **Typography** - Professional font stacks
- **Styling** - Modern CSS with hover states

## 🔧 Configuration Options

### Chart Dimensions
```python
dimensions = ChartDimensions(
    width=800,
    height=600,
    margin={"top": 20, "right": 20, "bottom": 40, "left": 40}
)
```

### Colors
```python
colors = ChartColors(
    scheme="d3.schemeSet3",
    background="#ffffff",
    text="#000000"
)
```

### Interactions
```python
interaction = ChartInteraction(
    hover_enabled=True,
    click_enabled=True,
    tooltip_enabled=True
)
```

## 📁 Output Files

Charts are saved to `data/visualizations/` with format:
```
chart_[id]_[timestamp].html
```

Each file is a complete, standalone HTML document with:
- ✅ D3.js library loaded from CDN
- ✅ Embedded data and configuration
- ✅ Interactive features enabled
- ✅ Professional styling

## 🔗 Integration with Existing Services

### Supabase Integration
```python
# Extract data from Supabase
from src.services.supabase.client import SupabaseService

supabase = SupabaseService(config)
# ... query data ...

# Generate chart
d3_service = D3Service(config)
result = d3_service.create_chart(chart_config, chart_data)
```

### Data Pipeline
```
Supabase Data → Data Processing → D3 Service → Interactive Chart
```

## 🎯 Use Cases

- **Business Dashboards** - RoofMaxx deal analysis
- **Data Exploration** - Interactive data visualization  
- **Reporting** - Professional chart generation
- **Analytics** - Visual data insights

## 🚀 Future Enhancements

- **More Chart Types** - Line charts, scatter plots, treemaps
- **Real-time Updates** - WebSocket integration for live data
- **Export Options** - PNG, SVG, PDF export capabilities
- **Dashboard Builder** - Multi-chart dashboard creation 