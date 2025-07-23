#!/usr/bin/env python3
"""
Generate RoofMaxx Deals Timeline Chart

Creates a D3.js multi-line chart showing:
1. Total deals created
2. Non-billable leads (GRML, SG, DDSM, MICRO)
3. % of non-billable leads

With interactive time period filters (days/weeks/months) and date range selection.
"""

import sys
import os
import json
import uuid
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Load environment variables
from config.env import load_env
load_env()

from src.services.supabase.client import SupabaseService

def extract_timeline_data():
    """Extract and aggregate deal data by time periods."""
    print("📊 EXTRACTING TIMELINE DATA FROM SUPABASE")
    print("=" * 50)
    
    # Connect to Supabase
    supabase_config = {
        'url': os.getenv('SUPABASE_URL'),
        'access_token': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }
    
    try:
        service = SupabaseService(supabase_config)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return None
    
    # Get all raw data
    try:
        url = f"{service.url}/rest/v1/roofmaxx_deals"
        params = {'select': 'deal_id,raw_data'}
        
        response = service.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            print("⚠️  No data found")
            return None
        
        print(f"📥 Retrieved {len(data):,} records")
        
    except Exception as e:
        print(f"❌ Data fetch error: {e}")
        return None
    
    # Process data
    print("🔄 Processing timeline data...")
    
    # Non-billable deal types
    non_billable_types = {'GRML', 'SG', 'DDSM', 'MICRO'}
    
    # Aggregate by day
    daily_data = defaultdict(lambda: {
        'total_deals': 0,
        'non_billable_deals': 0,
        'deal_types': Counter()
    })
    
    processed_count = 0
    
    for record in data:
        raw_data = record.get('raw_data', {})
        
        if not isinstance(raw_data, dict):
            continue
        
        # Extract create date
        createdate = raw_data.get('createdate')
        if not createdate:
            continue
        
        # Convert Unix timestamp (milliseconds) to date
        try:
            if isinstance(createdate, (int, float)):
                if createdate > 10000000000:  # Milliseconds
                    dt = datetime.fromtimestamp(createdate / 1000)
                else:  # Seconds
                    dt = datetime.fromtimestamp(createdate)
                
                date_key = dt.strftime('%Y-%m-%d')
                
                # Extract deal type
                dealtype = raw_data.get('dealtype', 'Unknown')
                
                # Aggregate data
                daily_data[date_key]['total_deals'] += 1
                daily_data[date_key]['deal_types'][dealtype] += 1
                
                if dealtype in non_billable_types:
                    daily_data[date_key]['non_billable_deals'] += 1
                
                processed_count += 1
                
        except Exception as e:
            continue
    
    print(f"✅ Processed {processed_count:,} records")
    print(f"📅 Date range: {len(daily_data)} days")
    
    # Convert to sorted list with percentages
    timeline_data = []
    
    for date_str in sorted(daily_data.keys()):
        day_data = daily_data[date_str]
        total = day_data['total_deals']
        non_billable = day_data['non_billable_deals']
        
        # Calculate percentage
        non_billable_pct = (non_billable / total * 100) if total > 0 else 0
        
        timeline_data.append({
            'date': date_str,
            'total_deals': total,
            'non_billable_deals': non_billable,
            'non_billable_percentage': round(non_billable_pct, 1),
            'deal_types': dict(day_data['deal_types'])
        })
    
    # Show summary
    if timeline_data:
        start_date = timeline_data[0]['date']
        end_date = timeline_data[-1]['date']
        total_deals = sum(d['total_deals'] for d in timeline_data)
        total_non_billable = sum(d['non_billable_deals'] for d in timeline_data)
        
        print(f"📈 Timeline Summary:")
        print(f"   Date range: {start_date} to {end_date}")
        print(f"   Total deals: {total_deals:,}")
        print(f"   Non-billable deals: {total_non_billable:,}")
        print(f"   Non-billable %: {(total_non_billable/total_deals*100):.1f}%")
    
    return timeline_data

def generate_line_chart(timeline_data):
    """Generate D3.js multi-line chart HTML."""
    print(f"\n🎨 GENERATING D3.JS MULTI-LINE CHART")
    print("=" * 50)
    
    chart_id = f"chart_{uuid.uuid4().hex[:8]}"
    
    # Create HTML with D3.js multi-line chart
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RoofMaxx Deals Timeline Analysis</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #ffffff;
            color: #000000;
            margin: 0;
            padding: 20px;
        }}
        
        .chart-container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .chart-title {{
            text-align: center;
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #000000;
        }}
        
        .chart-subtitle {{
            text-align: center;
            font-size: 16px;
            color: #666;
            margin-bottom: 30px;
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            flex-wrap: wrap;
        }}
        
        .control-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .control-group label {{
            font-weight: 600;
            font-size: 14px;
            color: #333;
        }}
        
        .control-group select,
        .control-group input {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        
        .chart-svg {{
            display: block;
            margin: 0 auto;
            border: 1px solid #eee;
            border-radius: 8px;
        }}
        
        .line {{
            fill: none;
            stroke-width: 2.5;
        }}
        
        .line-total {{
            stroke: #2563eb;
        }}
        
        .line-nonbillable {{
            stroke: #dc2626;
        }}
        
        .line-percentage {{
            stroke: #16a34a;
        }}
        
        .dot {{
            fill: white;
            stroke-width: 2;
            r: 4;
            opacity: 0;
            transition: opacity 0.2s;
        }}
        
        .dot:hover {{
            opacity: 1;
            r: 6;
        }}
        
        .axis {{
            font-size: 12px;
        }}
        
        .axis-label {{
            font-size: 14px;
            font-weight: 600;
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .legend-color {{
            width: 20px;
            height: 3px;
            border-radius: 2px;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px;
            border-radius: 6px;
            font-size: 13px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 1000;
            max-width: 250px;
        }}
        
        .stats {{
            margin-top: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: 700;
            color: #2563eb;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        <h1 class="chart-title">RoofMaxx Deals Timeline Analysis</h1>
        <p class="chart-subtitle">Total Deals, Non-Billable Leads (GRML, SG, DDSM, MICRO), and Non-Billable Percentage</p>
        
        <div class="controls">
            <div class="control-group">
                <label for="time-period">Time Period:</label>
                <select id="time-period">
                    <option value="day">Daily</option>
                    <option value="week">Weekly</option>
                    <option value="month" selected>Monthly</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="start-date">Start Date:</label>
                <input type="date" id="start-date">
            </div>
            
            <div class="control-group">
                <label for="end-date">End Date:</label>
                <input type="date" id="end-date">
            </div>
            
            <div class="control-group">
                <label>&nbsp;</label>
                <button id="update-chart" style="padding: 8px 16px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer;">Update Chart</button>
            </div>
        </div>
        
        <svg id="{chart_id}" class="chart-svg" width="1100" height="600"></svg>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background-color: #2563eb;"></div>
                <span>Total Deals</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #dc2626;"></div>
                <span>Non-Billable Leads</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #16a34a;"></div>
                <span>Non-Billable % (Right Axis)</span>
            </div>
        </div>
        
        <div class="stats" id="stats-container">
            <!-- Stats will be populated by JavaScript -->
        </div>
    </div>
    
    <div class="tooltip" id="tooltip"></div>

    <script>
        // Chart data
        const rawData = {json.dumps(timeline_data)};
        
        // Chart dimensions and margins
        const margin = {{top: 20, right: 80, bottom: 60, left: 80}};
        const width = 1100 - margin.left - margin.right;
        const height = 600 - margin.top - margin.bottom;
        
        // Parse dates
        const parseDate = d3.timeParse("%Y-%m-%d");
        rawData.forEach(d => {{
            d.date = parseDate(d.date);
        }});
        
        // Sort by date
        rawData.sort((a, b) => a.date - b.date);
        
        // Set initial date range
        const dateExtent = d3.extent(rawData, d => d.date);
        document.getElementById('start-date').value = d3.timeFormat("%Y-%m-%d")(dateExtent[0]);
        document.getElementById('end-date').value = d3.timeFormat("%Y-%m-%d")(dateExtent[1]);
        
        // Create SVG
        const svg = d3.select("#{chart_id}");
        const g = svg.append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
        
        // Tooltip
        const tooltip = d3.select("#tooltip");
        
        // Initialize chart
        updateChart();
        
        // Event listeners
        document.getElementById('update-chart').addEventListener('click', updateChart);
        
        function aggregateData(data, period) {{
            const aggregated = d3.rollup(data, 
                v => ({{
                    total_deals: d3.sum(v, d => d.total_deals),
                    non_billable_deals: d3.sum(v, d => d.non_billable_deals),
                    date: v[0].date // Use first date in period
                }}),
                d => {{
                    if (period === 'day') return d3.timeFormat("%Y-%m-%d")(d.date);
                    if (period === 'week') return d3.timeFormat("%Y-W%U")(d.date);
                    if (period === 'month') return d3.timeFormat("%Y-%m")(d.date);
                }}
            );
            
            const result = Array.from(aggregated.values()).map(d => ({{
                ...d,
                non_billable_percentage: d.total_deals > 0 ? (d.non_billable_deals / d.total_deals * 100) : 0
            }}));
            
            return result.sort((a, b) => a.date - b.date);
        }}
        
        function updateChart() {{
            // Get filter values
            const period = document.getElementById('time-period').value;
            const startDate = new Date(document.getElementById('start-date').value);
            const endDate = new Date(document.getElementById('end-date').value);
            
            // Filter data by date range
            const filteredData = rawData.filter(d => d.date >= startDate && d.date <= endDate);
            
            // Aggregate data by selected period
            const data = aggregateData(filteredData, period);
            
            if (data.length === 0) {{
                console.warn('No data to display');
                return;
            }}
            
            // Clear previous chart
            g.selectAll("*").remove();
            
            // Scales
            const xScale = d3.scaleTime()
                .domain(d3.extent(data, d => d.date))
                .range([0, width]);
            
            const yScale = d3.scaleLinear()
                .domain([0, d3.max(data, d => Math.max(d.total_deals, d.non_billable_deals))])
                .range([height, 0]);
            
            const yScalePercent = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.non_billable_percentage)])
                .range([height, 0]);
            
            // Line generators
            const lineTotal = d3.line()
                .x(d => xScale(d.date))
                .y(d => yScale(d.total_deals))
                .curve(d3.curveMonotoneX);
            
            const lineNonBillable = d3.line()
                .x(d => xScale(d.date))
                .y(d => yScale(d.non_billable_deals))
                .curve(d3.curveMonotoneX);
            
            const linePercentage = d3.line()
                .x(d => xScale(d.date))
                .y(d => yScalePercent(d.non_billable_percentage))
                .curve(d3.curveMonotoneX);
            
            // Add axes
            g.append("g")
                .attr("class", "axis")
                .attr("transform", `translate(0,${{height}})`)
                .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat("%m/%d")));
            
            g.append("g")
                .attr("class", "axis")
                .call(d3.axisLeft(yScale));
            
            g.append("g")
                .attr("class", "axis")
                .attr("transform", `translate(${{width}},0)`)
                .call(d3.axisRight(yScalePercent).tickFormat(d => d + "%"));
            
            // Add axis labels
            g.append("text")
                .attr("class", "axis-label")
                .attr("transform", "rotate(-90)")
                .attr("y", 0 - margin.left)
                .attr("x", 0 - (height / 2))
                .attr("dy", "1em")
                .style("text-anchor", "middle")
                .text("Number of Deals");
            
            g.append("text")
                .attr("class", "axis-label")
                .attr("transform", "rotate(-90)")
                .attr("y", width + margin.right)
                .attr("x", 0 - (height / 2))
                .attr("dy", "-1em")
                .style("text-anchor", "middle")
                .text("Non-Billable %");
            
            // Add lines
            g.append("path")
                .datum(data)
                .attr("class", "line line-total")
                .attr("d", lineTotal);
            
            g.append("path")
                .datum(data)
                .attr("class", "line line-nonbillable")
                .attr("d", lineNonBillable);
            
            g.append("path")
                .datum(data)
                .attr("class", "line line-percentage")
                .attr("d", linePercentage);
            
            // Add dots for interaction
            const dotGroups = g.selectAll(".dot-group")
                .data(data)
                .enter().append("g")
                .attr("class", "dot-group")
                .attr("transform", d => `translate(${{xScale(d.date)}},0)`);
            
            // Total deals dots
            dotGroups.append("circle")
                .attr("class", "dot dot-total")
                .attr("cy", d => yScale(d.total_deals))
                .style("stroke", "#2563eb")
                .on("mouseover", function(event, d) {{
                    d3.select(this).style("opacity", 1);
                    showTooltip(event, d, 'total');
                }})
                .on("mouseout", function() {{
                    d3.select(this).style("opacity", 0);
                    hideTooltip();
                }});
            
            // Non-billable dots
            dotGroups.append("circle")
                .attr("class", "dot dot-nonbillable")
                .attr("cy", d => yScale(d.non_billable_deals))
                .style("stroke", "#dc2626")
                .on("mouseover", function(event, d) {{
                    d3.select(this).style("opacity", 1);
                    showTooltip(event, d, 'nonbillable');
                }})
                .on("mouseout", function() {{
                    d3.select(this).style("opacity", 0);
                    hideTooltip();
                }});
            
            // Percentage dots
            dotGroups.append("circle")
                .attr("class", "dot dot-percentage")
                .attr("cy", d => yScalePercent(d.non_billable_percentage))
                .style("stroke", "#16a34a")
                .on("mouseover", function(event, d) {{
                    d3.select(this).style("opacity", 1);
                    showTooltip(event, d, 'percentage');
                }})
                .on("mouseout", function() {{
                    d3.select(this).style("opacity", 0);
                    hideTooltip();
                }});
            
            // Update stats
            updateStats(data);
        }}
        
        function showTooltip(event, d, type) {{
            const formatDate = d3.timeFormat("%B %d, %Y");
            let content = `<strong>${{formatDate(d.date)}}</strong><br/>`;
            
            if (type === 'total') {{
                content += `Total Deals: ${{d.total_deals.toLocaleString()}}<br/>`;
            }} else if (type === 'nonbillable') {{
                content += `Non-Billable Leads: ${{d.non_billable_deals.toLocaleString()}}<br/>`;
                content += `Total Deals: ${{d.total_deals.toLocaleString()}}<br/>`;
            }} else if (type === 'percentage') {{
                content += `Non-Billable %: ${{d.non_billable_percentage.toFixed(1)}}%<br/>`;
                content += `Non-Billable: ${{d.non_billable_deals.toLocaleString()}}<br/>`;
                content += `Total: ${{d.total_deals.toLocaleString()}}<br/>`;
            }}
            
            tooltip.html(content)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px")
                .transition()
                .duration(200)
                .style("opacity", 1);
        }}
        
        function hideTooltip() {{
            tooltip.transition()
                .duration(200)
                .style("opacity", 0);
        }}
        
        function updateStats(data) {{
            const totalDeals = d3.sum(data, d => d.total_deals);
            const totalNonBillable = d3.sum(data, d => d.non_billable_deals);
            const avgPercentage = d3.mean(data, d => d.non_billable_percentage);
            const maxDealsDay = d3.max(data, d => d.total_deals);
            
            const statsHtml = `
                <div class="stat-card">
                    <div class="stat-value">${{totalDeals.toLocaleString()}}</div>
                    <div class="stat-label">Total Deals</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{totalNonBillable.toLocaleString()}}</div>
                    <div class="stat-label">Non-Billable Leads</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{avgPercentage.toFixed(1)}}%</div>
                    <div class="stat-label">Avg Non-Billable %</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{maxDealsDay.toLocaleString()}}</div>
                    <div class="stat-label">Peak Daily Deals</div>
                </div>
            `;
            
            document.getElementById('stats-container').innerHTML = statsHtml;
        }}
    </script>
</body>
</html>'''
    
    # Save to file
    try:
        os.makedirs('data/visualizations', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"roofmaxx_deals_timeline_{timestamp}.html"
        file_path = os.path.join('data/visualizations', filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Chart generated successfully!")
        print(f"💾 Saved to: {file_path}")
        
        return {
            'success': True,
            'file_path': file_path,
            'chart_id': chart_id
        }
        
    except Exception as e:
        print(f"❌ Failed to save chart: {e}")
        return None

def main():
    """Main function to generate timeline chart."""
    
    print("🎯 ROOFMAXX DEALS TIMELINE CHART GENERATOR")
    print("=" * 60)
    print("📈 Generating multi-line chart with interactive filters")
    print()
    
    # Extract timeline data
    timeline_data = extract_timeline_data()
    if not timeline_data:
        print("❌ Failed to extract timeline data")
        return
    
    # Generate chart
    result = generate_line_chart(timeline_data)
    if not result:
        print("❌ Failed to generate chart")
        return
    
    # Success summary
    print(f"\n🎉 SUCCESS!")
    print("=" * 60)
    print("✅ Interactive timeline chart generated")
    print(f"📊 Data points: {len(timeline_data):,} days")
    print(f"📈 Features: Multi-line chart with time period filters")
    print(f"🎛️  Controls: Days/Weeks/Months toggle + Date range selector")
    
    if result['file_path']:
        print(f"🌐 Open in browser: file://{os.path.abspath(result['file_path'])}")

if __name__ == "__main__":
    main() 