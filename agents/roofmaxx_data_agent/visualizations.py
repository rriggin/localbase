#!/usr/bin/env python3
"""
RoofMaxx Data Agent - Visualizations Module

D3.js-based interactive visualizations for RoofMaxx deal data.
Part of the RoofMaxx Data Agent namespace.
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, Any, List, Optional

from src.services.supabase.client import SupabaseService

class RoofMaxxVisualizations:
    """
    D3.js visualization generator for RoofMaxx deal data.
    
    Provides interactive charts and dashboards specifically designed
    for RoofMaxx business intelligence and analytics.
    """
    
    def __init__(self, supabase_service: SupabaseService):
        """Initialize with Supabase service."""
        self.supabase_service = supabase_service
        self.output_dir = 'data/visualizations/roofmaxx'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_timeline_chart(self, 
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate interactive timeline chart showing:
        1. Total deals created
        2. Non-billable leads (GRML, SG, DDSM, MICRO)
        3. % of non-billable leads
        
        Args:
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            
        Returns:
            Dict with success status and file path
        """
        print("📊 GENERATING ROOFMAXX TIMELINE CHART")
        print("=" * 50)
        
        # Extract timeline data
        timeline_data = self._extract_timeline_data(start_date, end_date)
        if not timeline_data:
            return {'success': False, 'error': 'Failed to extract timeline data'}
        
        # Generate chart HTML
        chart_result = self._create_timeline_chart_html(timeline_data)
        
        print("✅ Timeline chart generated successfully!")
        return chart_result
    
    def generate_deals_pie_chart(self) -> Dict[str, Any]:
        """
        Generate interactive pie chart of deals by source type.
        
        Returns:
            Dict with success status and file path
        """
        print("📊 GENERATING ROOFMAXX DEALS PIE CHART")
        print("=" * 50)
        
        # Extract dealtype data
        dealtype_data = self._extract_dealtype_data()
        if not dealtype_data:
            return {'success': False, 'error': 'Failed to extract dealtype data'}
        
        # Generate chart HTML
        chart_result = self._create_pie_chart_html(dealtype_data)
        
        print("✅ Pie chart generated successfully!")
        return chart_result
    
    def _extract_timeline_data(self, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract and aggregate deal data by time periods."""
        
        try:
            # Get all raw data
            url = f"{self.supabase_service.url}/rest/v1/roofmaxx_deals"
            params = {'select': 'deal_id,raw_data'}
            
            response = self.supabase_service.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                print("⚠️  No data found")
                return []
            
            print(f"📥 Retrieved {len(data):,} records")
            
        except Exception as e:
            print(f"❌ Data fetch error: {e}")
            return []
        
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
                    
                    # Apply date filters if provided
                    if start_date:
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        if dt < start_dt:
                            continue
                    
                    if end_date:
                        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                        if dt > end_dt:
                            continue
                    
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
    
    def _extract_dealtype_data(self) -> List[Dict[str, Any]]:
        """Extract dealtype data for pie chart."""
        
        try:
            url = f"{self.supabase_service.url}/rest/v1/roofmaxx_deals"
            params = {'select': 'raw_data'}
            
            response = self.supabase_service.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                print("⚠️  No data found")
                return []
            
            print(f"📥 Retrieved {len(data):,} records")
            
        except Exception as e:
            print(f"❌ Data fetch error: {e}")
            return []
        
        # Process dealtype data
        dealtype_counts = Counter()
        
        for record in data:
            raw_data = record.get('raw_data', {})
            
            if isinstance(raw_data, dict):
                dealtype = raw_data.get('dealtype', 'Unknown')
                dealtype_counts[dealtype] += 1
            elif isinstance(raw_data, str):
                try:
                    parsed_data = json.loads(raw_data)
                    dealtype = parsed_data.get('dealtype', 'Unknown')
                    dealtype_counts[dealtype] += 1
                except:
                    dealtype_counts['Unknown'] += 1
            else:
                dealtype_counts['Unknown'] += 1
        
        # Convert to list format
        dealtype_data = []
        total_deals = sum(dealtype_counts.values())
        
        for dealtype, count in dealtype_counts.most_common():
            percentage = (count / total_deals * 100) if total_deals > 0 else 0
            dealtype_data.append({
                'dealtype': dealtype,
                'count': count,
                'percentage': round(percentage, 1)
            })
        
        print(f"📈 Found {len(dealtype_data)} deal types:")
        for item in dealtype_data:
            print(f"   {item['dealtype']}: {item['count']} deals ({item['percentage']}%)")
        
        return dealtype_data
    
    def _create_timeline_chart_html(self, timeline_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create HTML for timeline chart."""
        
        chart_id = f"timeline_{uuid.uuid4().hex[:8]}"
        
        # HTML content (using the same template from the original tool)
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
        
        .agent-badge {{
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            background: #f0f8ff;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
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
        
        .axis text {{
            font-weight: 500;
        }}
        
        .axis.x-axis text {{
            font-size: 12px;
            font-weight: 700;
            text-anchor: middle;
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
        
        .line-reference-table {{
            margin: 30px auto;
            max-width: 800px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
        }}
        
        .line-reference-table h3 {{
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 18px;
        }}
        
        .line-reference-table table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .line-reference-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }}
        
        .line-reference-table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
            font-size: 14px;
        }}
        
        .line-reference-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .line-reference-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .line-sample {{
            display: inline-block;
            width: 30px;
            height: 3px;
            border-radius: 2px;
            vertical-align: middle;
        }}
        
        .line-sample-blue {{
            background: #2563eb;
        }}
        
        .line-sample-red {{
            background: #dc2626;
        }}
        
        .line-sample-green {{
            background: #16a34a;
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        <div class="agent-badge">
            <strong>🤖 Generated by RoofMaxx Data Agent</strong> • 
            Interactive D3.js Visualization • 
            {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        </div>
        
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
        
        <div class="line-reference-table">
            <h3>📊 Line Reference</h3>
            <table>
                <thead>
                    <tr>
                        <th>Line Color</th>
                        <th>Data Series</th>
                        <th>Description</th>
                        <th>Y-Axis</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><span class="line-sample line-sample-blue"></span></td>
                        <td><strong>Total Deals</strong></td>
                        <td>All deals created (all sources)</td>
                        <td>Left</td>
                    </tr>
                    <tr>
                        <td><span class="line-sample line-sample-red"></span></td>
                        <td><strong>Non-Billable Leads</strong></td>
                        <td>GRML + SG + DDSM + MICRO deals</td>
                        <td>Left</td>
                    </tr>
                    <tr>
                        <td><span class="line-sample line-sample-green"></span></td>
                        <td><strong>Non-Billable %</strong></td>
                        <td>Percentage of non-billable leads</td>
                        <td>Right</td>
                    </tr>
                </tbody>
            </table>
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
        const margin = {{top: 20, right: 80, bottom: 80, left: 80}};
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
            
            // Force X-axis to show years by generating custom ticks
            const dateExtent = d3.extent(data, d => d.date);
            const startYear = dateExtent[0].getFullYear();
            const endYear = dateExtent[1].getFullYear();
            
            // Generate year-based ticks
            const yearTicks = [];
            for (let year = startYear; year <= endYear; year++) {{
                if (period === 'month') {{
                    // Show every 6 months
                    yearTicks.push(new Date(year, 0, 1)); // Jan
                    if (year < endYear || dateExtent[1].getMonth() >= 6) {{
                        yearTicks.push(new Date(year, 6, 1)); // Jul
                    }}
                }} else {{
                    // Show every year
                    yearTicks.push(new Date(year, 0, 1));
                }}
            }}
            
            const xAxis = d3.axisBottom(xScale)
                .tickValues(yearTicks)
                .tickFormat(d => {{
                    const date = new Date(d);
                    if (period === 'month') {{
                        return d3.timeFormat("%b %Y")(date);
                    }} else {{
                        return d3.timeFormat("%Y")(date);
                    }}
                }});
            
            g.append("g")
                .attr("class", "axis x-axis")
                .attr("transform", `translate(0,${{height}})`)
                .call(xAxis);
            
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
        
        # Save to agent's output directory
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"timeline_chart_{timestamp}.html"
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'success': True,
                'file_path': file_path,
                'chart_id': chart_id,
                'chart_type': 'timeline',
                'data_points': len(timeline_data)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Failed to save chart: {e}"}
    
    def _create_pie_chart_html(self, dealtype_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create HTML for pie chart."""
        
        chart_id = f"pie_{uuid.uuid4().hex[:8]}"
        
        # Simplified pie chart HTML (similar structure but focused on pie chart)
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RoofMaxx Deals by Source Type</title>
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
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .agent-badge {{
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            background: #f0f8ff;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
        }}
        
        .chart-title {{
            text-align: center;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #000000;
        }}
        
        .chart-svg {{
            display: block;
            margin: 0 auto;
        }}
        
        .slice {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .slice:hover {{
            opacity: 0.8;
        }}
        
        .slice-label {{
            font-size: 12px;
            font-weight: 500;
            fill: white;
            text-anchor: middle;
            pointer-events: none;
        }}
        
        .legend {{
            margin-top: 30px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 1000;
        }}
        
        .stats {{
            margin-top: 30px;
            text-align: center;
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        <div class="agent-badge">
            <strong>🤖 Generated by RoofMaxx Data Agent</strong> • 
            Interactive D3.js Pie Chart • 
            {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        </div>
        
        <h1 class="chart-title">RoofMaxx Deals by Source Type</h1>
        <svg id="{chart_id}" class="chart-svg" width="800" height="600"></svg>
        <div class="legend" id="{chart_id}-legend"></div>
        <div class="stats" id="{chart_id}-stats"></div>
    </div>
    
    <div class="tooltip" id="{chart_id}-tooltip"></div>

    <script>
        // Chart data
        const data = {json.dumps(dealtype_data)};
        const chartId = "{chart_id}";
        
        // Chart dimensions
        const width = 800;
        const height = 600;
        const radius = Math.min(width, height) / 2 - 40;
        
        // Color scale
        const color = d3.scaleOrdinal()
            .domain(data.map(d => d.dealtype))
            .range(d3.schemeSet3);
        
        // Create SVG
        const svg = d3.select(`#${{chartId}}`)
            .attr("viewBox", `0 0 ${{width}} ${{height}}`)
            .style("max-width", "100%")
            .style("height", "auto");
        
        const g = svg.append("g")
            .attr("transform", `translate(${{width / 2}}, ${{height / 2}})`);
        
        // Create pie layout
        const pie = d3.pie()
            .value(d => d.count)
            .sort(null);
        
        // Create arc generator
        const arc = d3.arc()
            .innerRadius(0)
            .outerRadius(radius);
        
        const labelArc = d3.arc()
            .innerRadius(radius * 0.6)
            .outerRadius(radius * 0.6);
        
        // Tooltip
        const tooltip = d3.select(`#${{chartId}}-tooltip`);
        
        // Calculate total for percentages
        const total = d3.sum(data, d => d.count);
        
        // Create pie slices
        const arcs = g.selectAll(".slice")
            .data(pie(data))
            .enter()
            .append("g")
            .attr("class", "slice");
        
        // Add paths
        arcs.append("path")
            .attr("d", arc)
            .attr("fill", d => color(d.data.dealtype))
            .attr("stroke", "white")
            .attr("stroke-width", 2)
            .on("mouseover", function(event, d) {{
                const percentage = ((d.data.count / total) * 100).toFixed(1);
                
                tooltip.transition()
                    .duration(200)
                    .style("opacity", 1);
                
                tooltip.html(`
                    <strong>${{d.data.dealtype}}</strong><br/>
                    Count: ${{d.data.count.toLocaleString()}}<br/>
                    Percentage: ${{percentage}}%
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
            }})
            .on("mousemove", function(event) {{
                tooltip
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 10) + "px");
            }})
            .on("mouseout", function() {{
                tooltip.transition()
                    .duration(200)
                    .style("opacity", 0);
            }});
        
        // Add labels for larger slices
        arcs.append("text")
            .attr("class", "slice-label")
            .attr("transform", d => {{
                const percentage = (d.data.count / total) * 100;
                if (percentage < 5) return "translate(1000,1000)"; // Hide small labels
                return `translate(${{labelArc.centroid(d)}})`;
            }})
            .text(d => {{
                const percentage = (d.data.count / total) * 100;
                return percentage >= 5 ? `${{percentage.toFixed(1)}}%` : "";
            }})
            .style("font-size", "12px")
            .style("font-weight", "600");
        
        // Create legend
        const legend = d3.select(`#${{chartId}}-legend`);
        
        const legendItems = legend.selectAll(".legend-item")
            .data(data.sort((a, b) => b.count - a.count))
            .enter()
            .append("div")
            .attr("class", "legend-item");
        
        legendItems.append("div")
            .attr("class", "legend-color")
            .style("background-color", d => color(d.dealtype));
        
        legendItems.append("span")
            .text(d => {{
                const percentage = ((d.count / total) * 100).toFixed(1);
                return `${{d.dealtype}}: ${{d.count.toLocaleString()}} (${{percentage}}%)`;
            }});
        
        // Add statistics
        const stats = d3.select(`#${{chartId}}-stats`);
        stats.html(`
            <strong>Total Deals:</strong> ${{total.toLocaleString()}} | 
            <strong>Deal Types:</strong> ${{data.length}} | 
            <strong>Generated:</strong> ${{new Date().toLocaleDateString()}}
        `);
        
        // Add animation on load
        arcs.selectAll("path")
            .style("opacity", 0)
            .transition()
            .duration(800)
            .delay((d, i) => i * 100)
            .style("opacity", 1)
            .attrTween("d", function(d) {{
                const interpolate = d3.interpolate({{startAngle: 0, endAngle: 0}}, d);
                return function(t) {{
                    return arc(interpolate(t));
                }};
            }});
    </script>
</body>
</html>'''
        
        # Save to agent's output directory
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pie_chart_{timestamp}.html"
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'success': True,
                'file_path': file_path,
                'chart_id': chart_id,
                'chart_type': 'pie',
                'data_points': len(dealtype_data)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Failed to save chart: {e}"} 