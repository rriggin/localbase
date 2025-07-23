#!/usr/bin/env python3
"""
Generate RoofMaxx Deals Pie Chart

Creates a D3.js pie chart showing deals segmented by dealtype using the existing Supabase data.
"""

import sys
import os
import ast
from collections import Counter
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Load environment and services
from config.env import load_env
load_env()

from src.services.supabase.client import SupabaseService

def get_dealtype_data():
    """Extract dealtype data from Supabase."""
    print("📊 EXTRACTING DEALTYPE DATA FROM SUPABASE")
    print("=" * 50)
    
    # Initialize Supabase service
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
    
    # Query raw_data to extract dealtype
    try:
        url = f"{service.url}/rest/v1/roofmaxx_deals"
        params = {'select': 'raw_data'}
        
        response = service.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            print("⚠️  No data found in roofmaxx_deals table")
            return None
        
        print(f"📥 Retrieved {len(data):,} records")
        
        # Extract dealtype from raw_data
        dealtype_counts = Counter()
        
        for record in data:
            try:
                raw_data_str = record['raw_data']
                
                # Handle different data formats
                if isinstance(raw_data_str, dict):
                    raw_data = raw_data_str
                elif isinstance(raw_data_str, str):
                    # Try to parse as Python literal
                    try:
                        raw_data = ast.literal_eval(raw_data_str)
                    except:
                        # Try to parse as JSON
                        import json
                        raw_data = json.loads(raw_data_str)
                else:
                    raw_data = {}
                
                dealtype = raw_data.get('dealtype', 'Unknown')
                dealtype_counts[dealtype] += 1
                
            except Exception as e:
                print(f"   ⚠️  Parse error for record: {str(e)[:100]}")
                dealtype_counts['Parse Error'] += 1
        
        # Convert to list format for D3
        chart_data = []
        for dealtype, count in dealtype_counts.most_common():
            chart_data.append({
                'dealtype': dealtype,
                'count': count
            })
        
        print(f"📈 Found {len(chart_data)} deal types:")
        for item in chart_data:
            percentage = (item['count'] / len(data)) * 100
            print(f"   {item['dealtype']}: {item['count']:,} deals ({percentage:.1f}%)")
        
        return chart_data
        
    except Exception as e:
        print(f"❌ Data extraction failed: {e}")
        return None

def generate_pie_chart(dealtype_data):
    """Generate D3.js pie chart HTML directly."""
    print(f"\n🎨 GENERATING D3.JS PIE CHART")
    print("=" * 50)
    
    import json
    import uuid
    
    # Generate chart ID
    chart_id = f"chart_{uuid.uuid4().hex[:8]}"
    
    # Create HTML with embedded D3.js
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
    
    # Save to file
    try:
        os.makedirs('data/visualizations', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"roofmaxx_deals_pie_chart_{timestamp}.html"
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
    """Main execution."""
    print("🎯 ROOFMAXX DEALS PIE CHART GENERATOR")
    print("=" * 60)
    print("📈 Generating D3.js pie chart of deals by dealtype")
    print()
    
    # Get dealtype data
    dealtype_data = get_dealtype_data()
    if not dealtype_data:
        print("❌ Failed to extract dealtype data")
        sys.exit(1)
    
    # Generate pie chart
    result = generate_pie_chart(dealtype_data)
    if not result:
        print("❌ Failed to generate pie chart")
        sys.exit(1)
    
    print(f"\n🎉 SUCCESS!")
    print("=" * 60)
    print(f"✅ Interactive pie chart generated")
    print(f"📊 Total deals: {sum(item['count'] for item in dealtype_data):,}")
    print(f"🎯 Deal types: {len(dealtype_data)}")
    
    if result['file_path']:
        print(f"🌐 Open in browser: file://{os.path.abspath(result['file_path'])}")

if __name__ == "__main__":
    main() 