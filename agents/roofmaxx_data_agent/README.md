# 🤖 RoofMaxx Data Agent

**Conversational Business Intelligence Assistant for RoofMaxx Deal Data**

## Overview

The RoofMaxx Data Agent is an interactive AI assistant that provides real-time business intelligence for your RoofMaxx deal data. Chat with your data using natural language and get instant insights, reports, and visualizations.

## Features

- 🗣️ **Natural Language Interface** - Ask questions in plain English
- 📊 **Real-time Analytics** - Live data from your Supabase database
- 🎨 **Interactive HTML Reports** - Professional dashboards with charts
- 🏙️ **Geographic Analysis** - Performance by cities and regions
- 📈 **Pipeline Insights** - Deal stages and conversion metrics
- 🎯 **Source Analysis** - Lead source performance and ROI

## Quick Start

```bash
# From the project root
python3 agents/roofmaxx_data_agent/agent.py

# Or run the convenience script
python3 agents/roofmaxx_data_agent/run.py
```

## Sample Questions

- *"Where do most of our deals come from?"*
- *"How many deals do we have in Kansas City?"*
- *"What's our completion rate?"*
- *"Generate an HTML report"*
- *"Show me deals from NAP source"*
- *"What are our top performing cities?"*

## Data Access

Currently connected to **868 deals** with comprehensive data including:

- Deal sources and lead types
- Customer contact information
- Geographic data (address, city, state)
- Deal stages and lifecycle status
- Invoice amounts and warranty info
- HubSpot integration data

## Output

- **Console Reports** - Formatted text analysis
- **HTML Dashboards** - Interactive web reports saved to `data/outputs/reports/`
- **Real-time Insights** - Live data processing and analysis

## Dependencies

- Supabase (database connection)
- Matplotlib (visualizations)
- Pandas (data processing)
- JSON (data formatting) 