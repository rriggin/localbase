#!/usr/bin/env python3
"""
RoofMaxx Data Agent - Your Conversational Business Intelligence Assistant

Chat with your deal data and generate reports on demand!
"""

import sys
import os
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from config.env import load_env
load_env()

from supabase import create_client, Client

class RoofMaxxDataAgent:
    """
    Your conversational business intelligence agent for RoofMaxx deal data.
    
    Can answer questions, generate reports, and provide insights about your 868 deals!
    """
    
    def __init__(self):
        """Initialize the data agent."""
        self.name = "RoofMaxx Data Agent"
        self.version = "1.0"
        self.client = None
        self.deals_data = None
        self.last_query_time = None
        
        print(f"🤖 {self.name} v{self.version} Initializing...")
        
        # Connect to Supabase
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            self.client = create_client(url, key)
            print("✅ Connected to Supabase database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return
        
        # Load deal data
        self._load_deal_data()
        
        print(f"🎯 Ready! I have access to {len(self.deals_data) if self.deals_data else 0} deals")
        print("💬 Ask me anything about your business data!")
    
    def _load_deal_data(self):
        """Load and process deal data from Supabase."""
        try:
            print("📊 Loading deal data...")
            result = self.client.table('roofmaxx_deals').select('raw_data').execute()
            
            self.deals_data = []
            for record in result.data:
                raw_deal = record.get('raw_data', {})
                if raw_deal:
                    # Process and flatten the deal data
                    processed_deal = {
                        'deal_id': raw_deal.get('id'),
                        'deal_name': raw_deal.get('deal_name', ''),
                        'source': raw_deal.get('dealtype', 'Unknown'),
                        'lifecycle': raw_deal.get('deal_lifecycle', 'Unknown'),
                        'stage': self._extract_stage(raw_deal),
                        'city': raw_deal.get('city', ''),
                        'state': raw_deal.get('state', ''),
                        'address': raw_deal.get('address', ''),
                        'postal_code': raw_deal.get('postal_code', ''),
                        'customer_name': self._extract_customer_name(raw_deal),
                        'customer_email': self._extract_customer_email(raw_deal),
                        'customer_phone': self._extract_customer_phone(raw_deal),
                        'invoice_total': raw_deal.get('invoice_total_currency', '$0.00'),
                        'is_roof_maxx_job': raw_deal.get('is_roof_maxx_job', False),
                        'has_warranty': raw_deal.get('has_warranty', False),
                        'create_date': self._extract_date(raw_deal),
                        'raw_data': raw_deal
                    }
                    self.deals_data.append(processed_deal)
            
            self.last_query_time = datetime.now()
            print(f"✅ Loaded {len(self.deals_data)} deals")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.deals_data = []
    
    def _extract_stage(self, deal):
        """Extract stage from deal data."""
        stage = deal.get('stage', {})
        if isinstance(stage, dict):
            return stage.get('label', 'Unknown')
        return str(stage) if stage else 'Unknown'
    
    def _extract_customer_name(self, deal):
        """Extract customer name from deal data."""
        contact = deal.get('hubspot_contact', {})
        if contact:
            first = contact.get('firstname', '')
            last = contact.get('lastname', '')
            return f"{first} {last}".strip()
        return deal.get('deal_name', '').split(' in ')[0] if ' in ' in deal.get('deal_name', '') else ''
    
    def _extract_customer_email(self, deal):
        """Extract customer email."""
        contact = deal.get('hubspot_contact', {})
        return contact.get('email', '') if contact else ''
    
    def _extract_customer_phone(self, deal):
        """Extract customer phone."""
        contact = deal.get('hubspot_contact', {})
        return contact.get('phone', '') if contact else ''
    
    def _extract_date(self, deal):
        """Extract and convert create date."""
        timestamp = deal.get('createdate')
        if timestamp:
            try:
                # Convert from milliseconds to datetime
                return datetime.fromtimestamp(timestamp / 1000)
            except:
                return None
        return None
    
    def chat(self, query):
        """Main chat interface - answer questions about the data."""
        
        if not self.deals_data:
            return "❌ No data available. Please check database connection."
        
        query_lower = query.lower()
        
        # Source/Lead analysis
        if any(word in query_lower for word in ['source', 'sources', 'lead', 'leads', 'where', 'come from']):
            return self._analyze_sources()
        
        # City/Geographic analysis
        elif any(word in query_lower for word in ['city', 'cities', 'location', 'geographic', 'where']):
            return self._analyze_cities()
        
        # Stage analysis
        elif any(word in query_lower for word in ['stage', 'stages', 'status', 'pipeline']):
            return self._analyze_stages()
        
        # Totals and counts
        elif any(word in query_lower for word in ['total', 'count', 'how many', 'number']):
            return self._analyze_totals()
        
        # Date/Time analysis
        elif any(word in query_lower for word in ['date', 'time', 'when', 'month', 'year', 'recent']):
            return self._analyze_dates()
        
        # Performance analysis
        elif any(word in query_lower for word in ['best', 'top', 'performance', 'most', 'highest']):
            return self._analyze_performance()
        
        # Generate HTML report
        elif any(word in query_lower for word in ['report', 'html', 'dashboard', 'generate']):
            return self._generate_html_report(query)
        
        # General help
        elif any(word in query_lower for word in ['help', 'what can', 'commands']):
            return self._show_help()
        
        else:
            return self._general_response(query)
    
    def _analyze_sources(self):
        """Analyze deal sources."""
        sources = [deal['source'] for deal in self.deals_data]
        source_counts = Counter(sources)
        
        response = "🎯 **DEAL SOURCES ANALYSIS**\n\n"
        
        for source, count in source_counts.most_common():
            percentage = (count / len(sources)) * 100
            response += f"• **{source}**: {count:,} deals ({percentage:.1f}%)\n"
        
        response += f"\n📊 **Key Insights:**\n"
        response += f"• Door-to-door (NAP) dominates with {source_counts.get('NAP', 0)} deals\n"
        response += f"• Digital channels (GRML, DDSM): {source_counts.get('GRML', 0) + source_counts.get('DDSM', 0)} deals\n"
        response += f"• Corporate leads (RMCL): {source_counts.get('RMCL', 0)} deals\n"
        
        return response
    
    def _analyze_cities(self):
        """Analyze deals by city."""
        cities = [deal['city'] for deal in self.deals_data if deal['city']]
        city_counts = Counter(cities)
        
        response = "🏙️ **TOP CITIES ANALYSIS**\n\n"
        
        for city, count in city_counts.most_common(10):
            percentage = (count / len(cities)) * 100
            response += f"• **{city}**: {count:,} deals ({percentage:.1f}%)\n"
        
        response += f"\n📍 **Geographic Insights:**\n"
        response += f"• Kansas City leads with {city_counts.get('Kansas City', 0)} deals\n"
        response += f"• Serving {len(city_counts)} different cities\n"
        response += f"• Top 5 cities represent {sum(list(city_counts.values())[:5]) / len(cities) * 100:.1f}% of business\n"
        
        return response
    
    def _analyze_stages(self):
        """Analyze deal stages."""
        stages = [deal['stage'] for deal in self.deals_data]
        stage_counts = Counter(stages)
        
        response = "📈 **DEAL STAGES ANALYSIS**\n\n"
        
        for stage, count in stage_counts.most_common():
            percentage = (count / len(stages)) * 100
            response += f"• **{stage}**: {count:,} deals ({percentage:.1f}%)\n"
        
        # Calculate conversion metrics
        completed = stage_counts.get('Job 100% Complete', 0)
        accepted = stage_counts.get('Job Offer Accepted', 0)
        lost = stage_counts.get('Lost', 0)
        
        response += f"\n🎯 **Pipeline Insights:**\n"
        response += f"• Completion rate: {completed / len(stages) * 100:.1f}%\n"
        response += f"• Acceptance rate: {accepted / len(stages) * 100:.1f}%\n"
        response += f"• Loss rate: {lost / len(stages) * 100:.1f}%\n"
        
        return response
    
    def _analyze_totals(self):
        """Analyze total numbers."""
        total_deals = len(self.deals_data)
        sources = len(set(deal['source'] for deal in self.deals_data))
        cities = len(set(deal['city'] for deal in self.deals_data if deal['city']))
        
        response = f"📊 **BUSINESS TOTALS**\n\n"
        response += f"• **Total Deals**: {total_deals:,}\n"
        response += f"• **Lead Sources**: {sources}\n"
        response += f"• **Cities Served**: {cities}\n"
        response += f"• **States**: {len(set(deal['state'] for deal in self.deals_data if deal['state']))}\n"
        
        # Date range
        dates = [deal['create_date'] for deal in self.deals_data if deal['create_date']]
        if dates:
            oldest = min(dates)
            newest = max(dates)
            response += f"• **Date Range**: {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}\n"
        
        return response
    
    def _analyze_dates(self):
        """Analyze deals by date."""
        dates = [deal['create_date'] for deal in self.deals_data if deal['create_date']]
        
        if not dates:
            return "❌ No date information available in the data."
        
        response = "📅 **DATE ANALYSIS**\n\n"
        
        # Recent deals (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_deals = [d for d in dates if d > thirty_days_ago]
        
        response += f"• **Recent Deals (30 days)**: {len(recent_deals)}\n"
        response += f"• **Oldest Deal**: {min(dates).strftime('%Y-%m-%d')}\n"
        response += f"• **Newest Deal**: {max(dates).strftime('%Y-%m-%d')}\n"
        
        # Monthly breakdown
        from collections import defaultdict
        monthly = defaultdict(int)
        for date in dates:
            month_key = date.strftime('%Y-%m')
            monthly[month_key] += 1
        
        response += f"\n📈 **Recent Monthly Activity:**\n"
        for month in sorted(monthly.keys())[-6:]:  # Last 6 months
            response += f"• {month}: {monthly[month]} deals\n"
        
        return response
    
    def _analyze_performance(self):
        """Analyze top performance metrics."""
        response = "🏆 **TOP PERFORMANCE ANALYSIS**\n\n"
        
        # Top source
        sources = Counter(deal['source'] for deal in self.deals_data)
        top_source = sources.most_common(1)[0]
        response += f"🥇 **Top Source**: {top_source[0]} with {top_source[1]} deals\n\n"
        
        # Top city
        cities = Counter(deal['city'] for deal in self.deals_data if deal['city'])
        top_city = cities.most_common(1)[0]
        response += f"🏙️ **Top City**: {top_city[0]} with {top_city[1]} deals\n\n"
        
        # Success metrics
        stages = Counter(deal['stage'] for deal in self.deals_data)
        completed = stages.get('Job 100% Complete', 0)
        total = len(self.deals_data)
        
        response += f"📈 **Success Metrics**:\n"
        response += f"• Completion Rate: {completed / total * 100:.1f}%\n"
        response += f"• Most Common Stage: {stages.most_common(1)[0][0]}\n"
        
        return response
    
    def _generate_html_report(self, query=None):
        """Generate an interactive HTML report."""
        
        print("🎨 Generating interactive HTML report...")
        
        html_content = self._create_html_dashboard()
        
        # Save the report
        reports_dir = 'data/outputs/reports'
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{reports_dir}/roofmaxx_dashboard_{timestamp}.html'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return f"✅ **HTML Report Generated!**\n\nSaved to: {filename}\n\n🌐 Open this file in your browser for an interactive dashboard with:\n• Clickable pie chart\n• Filterable deal table\n• Date range selector\n• Source filters"
    
    def _create_html_dashboard(self):
        """Create the interactive HTML dashboard."""
        
        # Get data for JavaScript
        sources = Counter(deal['source'] for deal in self.deals_data)
        
        # Prepare deals data for JavaScript
        deals_json = json.dumps([{
            'deal_id': deal['deal_id'],
            'deal_name': deal['deal_name'],
            'source': deal['source'],
            'stage': deal['stage'],
            'city': deal['city'],
            'state': deal['state'],
            'customer_name': deal['customer_name'],
            'customer_email': deal['customer_email'],
            'customer_phone': deal['customer_phone'],
            'invoice_total': deal['invoice_total'],
            'create_date': deal['create_date'].isoformat() if deal['create_date'] else None
        } for deal in self.deals_data], indent=2)
        
        # Prepare chart data
        chart_data = {
            'labels': list(sources.keys()),
            'data': list(sources.values())
        }
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RoofMaxx Business Intelligence Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .dashboard-content {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
            padding: 30px;
        }}
        
        .chart-section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .table-section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .filters {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .filter-group label {{
            margin-bottom: 5px;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .filter-group select, .filter-group input {{
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }}
        
        .deals-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .deals-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .deals-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }}
        
        .deals-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .source-tag {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }}
        
        .stage-badge {{
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .stage-completed {{ background: #27ae60; color: white; }}
        .stage-accepted {{ background: #3498db; color: white; }}
        .stage-lost {{ background: #e74c3c; color: white; }}
        .stage-paused {{ background: #f39c12; color: white; }}
        .stage-other {{ background: #95a5a6; color: white; }}
        
        #selectedSourceInfo {{
            margin-top: 15px;
            padding: 15px;
            background: #e8f4fd;
            border-left: 4px solid #3498db;
            border-radius: 5px;
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 RoofMaxx Business Intelligence Dashboard</h1>
            <p>Interactive Analysis of {len(self.deals_data):,} Deals • Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(self.deals_data):,}</div>
                <div class="stat-label">Total Deals</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(deal['source'] for deal in self.deals_data))}</div>
                <div class="stat-label">Lead Sources</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(deal['city'] for deal in self.deals_data if deal['city']))}</div>
                <div class="stat-label">Cities Served</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sources.most_common(1)[0][1]}</div>
                <div class="stat-label">Top Source ({sources.most_common(1)[0][0]})</div>
            </div>
        </div>
        
        <div class="dashboard-content">
            <div class="chart-section">
                <h3>📊 Deals by Source</h3>
                <canvas id="sourceChart" width="400" height="400"></canvas>
                <div id="selectedSourceInfo"></div>
            </div>
            
            <div class="table-section">
                <h3>📋 Deals Table</h3>
                
                <div class="filters">
                    <div class="filter-group">
                        <label for="sourceFilter">Filter by Source:</label>
                        <select id="sourceFilter">
                            <option value="">All Sources</option>
                            {chr(10).join(f'<option value="{source}">{source}</option>' for source in sorted(sources.keys()))}
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="cityFilter">Filter by City:</label>
                        <select id="cityFilter">
                            <option value="">All Cities</option>
                            {chr(10).join(f'<option value="{city}">{city}</option>' for city in sorted(set(deal['city'] for deal in self.deals_data if deal['city'])))}
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="stageFilter">Filter by Stage:</label>
                        <select id="stageFilter">
                            <option value="">All Stages</option>
                            {chr(10).join(f'<option value="{stage}">{stage}</option>' for stage in sorted(set(deal['stage'] for deal in self.deals_data)))}
                        </select>
                    </div>
                </div>
                
                <div style="max-height: 600px; overflow-y: auto;">
                    <table class="deals-table" id="dealsTable">
                        <thead>
                            <tr>
                                <th>Deal ID</th>
                                <th>Customer</th>
                                <th>Source</th>
                                <th>Stage</th>
                                <th>City</th>
                                <th>Invoice</th>
                            </tr>
                        </thead>
                        <tbody id="dealsTableBody">
                            <!-- Populated by JavaScript -->
                        </tbody>
                    </table>
                </div>
                
                <div id="tableStats" style="margin-top: 15px; color: #7f8c8d; font-style: italic;">
                    Showing all {len(self.deals_data):,} deals
                </div>
            </div>
        </div>
    </div>

    <script>
        // Deal data
        const dealsData = {deals_json};
        const chartData = {json.dumps(chart_data)};
        
        // Initialize chart
        const ctx = document.getElementById('sourceChart').getContext('2d');
        const sourceChart = new Chart(ctx, {{
            type: 'pie',
            data: {{
                labels: chartData.labels,
                datasets: [{{
                    data: chartData.data,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384',
                        '#36A2EB', '#FFCE56'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            usePointStyle: true
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed * 100) / total).toFixed(1);
                                return context.label + ': ' + context.parsed + ' deals (' + percentage + '%)';
                            }}
                        }}
                    }}
                }},
                onClick: function(event, elements) {{
                    if (elements.length > 0) {{
                        const index = elements[0].index;
                        const source = chartData.labels[index];
                        filterTableBySource(source);
                        showSourceInfo(source, chartData.data[index]);
                    }}
                }}
            }}
        }});
        
        // Table functions
        function renderTable(filteredDeals = dealsData) {{
            const tbody = document.getElementById('dealsTableBody');
            tbody.innerHTML = '';
            
            filteredDeals.forEach(deal => {{
                const row = tbody.insertRow();
                
                // Source color coding
                const sourceColors = {{
                    'NAP': '#e74c3c', 'NAP-L': '#c0392b', 'NAP-S': '#a93226',
                    'RMCL': '#3498db', 'RMCL-F': '#2980b9',
                    'GRML': '#27ae60', 'SG': '#16a085',
                    'DDSM': '#f39c12', 'MICRO': '#e67e22'
                }};
                
                // Stage badge styling
                const stageBadge = getStageClass(deal.stage);
                
                row.innerHTML = `
                    <td>${{deal.deal_id}}</td>
                    <td>${{deal.customer_name || 'N/A'}}</td>
                    <td><span class="source-tag" style="background: ${{sourceColors[deal.source] || '#95a5a6'}}">${{deal.source}}</span></td>
                    <td><span class="stage-badge ${{stageBadge}}">${{deal.stage}}</span></td>
                    <td>${{deal.city || 'N/A'}}</td>
                    <td>${{deal.invoice_total || '$0.00'}}</td>
                `;
            }});
            
            // Update stats
            document.getElementById('tableStats').textContent = 
                `Showing ${{filteredDeals.length.toLocaleString()}} of ${{dealsData.length.toLocaleString()}} deals`;
        }}
        
        function getStageClass(stage) {{
            if (stage.includes('Complete')) return 'stage-completed';
            if (stage.includes('Accepted')) return 'stage-accepted';
            if (stage.includes('Lost')) return 'stage-lost';
            if (stage.includes('Paused')) return 'stage-paused';
            return 'stage-other';
        }}
        
        function filterTableBySource(source) {{
            const filteredDeals = dealsData.filter(deal => deal.source === source);
            renderTable(filteredDeals);
            
            // Update filter dropdown
            document.getElementById('sourceFilter').value = source;
        }}
        
        function showSourceInfo(source, count) {{
            const info = document.getElementById('selectedSourceInfo');
            const percentage = ((count / dealsData.length) * 100).toFixed(1);
            
            info.innerHTML = `
                <strong>Selected: ${{source}}</strong><br>
                ${{count}} deals (${{percentage}}% of total)<br>
                <small>Table filtered to show only ${{source}} deals</small>
            `;
            info.style.display = 'block';
        }}
        
        // Filter event listeners
        document.getElementById('sourceFilter').addEventListener('change', function() {{
            applyFilters();
        }});
        
        document.getElementById('cityFilter').addEventListener('change', function() {{
            applyFilters();
        }});
        
        document.getElementById('stageFilter').addEventListener('change', function() {{
            applyFilters();
        }});
        
        function applyFilters() {{
            const sourceFilter = document.getElementById('sourceFilter').value;
            const cityFilter = document.getElementById('cityFilter').value;
            const stageFilter = document.getElementById('stageFilter').value;
            
            let filteredDeals = dealsData;
            
            if (sourceFilter) {{
                filteredDeals = filteredDeals.filter(deal => deal.source === sourceFilter);
            }}
            
            if (cityFilter) {{
                filteredDeals = filteredDeals.filter(deal => deal.city === cityFilter);
            }}
            
            if (stageFilter) {{
                filteredDeals = filteredDeals.filter(deal => deal.stage === stageFilter);
            }}
            
            renderTable(filteredDeals);
            
            // Hide source info if not filtering by source
            if (!sourceFilter) {{
                document.getElementById('selectedSourceInfo').style.display = 'none';
            }}
        }}
        
        // Initialize table
        renderTable();
        
    </script>
</body>
</html>
        """
        
        return html
    
    def _show_help(self):
        """Show help and available commands."""
        return """
🤖 **RoofMaxx Data Agent Help**

**What can I do for you?**

📊 **Data Analysis:**
• "Show me deal sources" - Analyze lead sources
• "What cities do we serve?" - Geographic analysis  
• "How are deals performing?" - Stage analysis
• "Show me totals" - Overall business metrics

📅 **Date Analysis:**
• "Show recent deals" - Time-based analysis
• "When was our busiest month?" - Date trends

🏆 **Performance Insights:**
• "What's our best source?" - Top performers
• "Show me top cities" - Geographic leaders
• "Performance metrics" - Success rates

📋 **Reports:**
• "Generate HTML report" - Interactive dashboard
• "Create report" - Custom visualizations

💬 **Just ask naturally!** I understand questions like:
• "Where do most of our deals come from?"
• "How many deals do we have in Kansas City?"
• "What's our completion rate?"
• "Show me deals from NAP source"
"""
    
    def _general_response(self, query):
        """Handle general queries."""
        return f"""
🤔 I'm not sure how to answer: "{query}"

Try asking me about:
• Deal sources and lead analysis
• Cities and geographic data  
• Deal stages and pipeline
• Performance metrics
• HTML report generation

Type "help" to see all available commands!
        """

def main():
    """Main chat interface."""
    
    print("🤖 RoofMaxx Data Agent - Interactive Business Intelligence")
    print("=" * 70)
    
    agent = RoofMaxxDataAgent()
    
    if not agent.deals_data:
        print("❌ Failed to load data. Please check your database connection.")
        return
    
    print("\n💬 Chat Interface Ready!")
    print("Type your questions about the deal data, or 'quit' to exit.")
    print("Examples: 'show me deal sources', 'generate html report', 'help'\n")
    
    while True:
        try:
            user_input = input("🗣️  You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thanks for using RoofMaxx Data Agent!")
                break
            
            if not user_input:
                continue
            
            print(f"\n🤖 Agent:")
            response = agent.chat(user_input)
            print(response)
            print("\n" + "-" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 