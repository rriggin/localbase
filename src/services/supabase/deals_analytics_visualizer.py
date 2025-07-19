#!/usr/bin/env python3
"""
RoofMaxx Deals Analytics & Visualizations

Query your Supabase database and create business intelligence visualizations.
"""

import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import seaborn as sns
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# Load environment variables
from config.env import load_env
load_env()

from supabase import create_client, Client

def connect_to_supabase():
    """Connect to Supabase database."""
    
    print("🔗 CONNECTING TO SUPABASE DATABASE")
    print("-" * 50)
    
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        client = create_client(url, key)
        
        # Test connection
        result = client.table('roofmaxx_deals').select('*', count='exact').limit(1).execute()
        total_deals = result.count
        
        print(f"✅ Connected successfully!")
        print(f"📊 Total deals available: {total_deals:,}")
        print()
        
        return client
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def fetch_deals_data(client):
    """Fetch all deals data from Supabase."""
    
    print("📥 FETCHING DEALS DATA")
    print("-" * 30)
    
    try:
        # Fetch all deals with relevant fields
        result = client.table('roofmaxx_deals').select(
            'deal_id,deal_type,deal_lifecycle,deal_stage,customer_first_name,customer_last_name,city,state,invoice_total,create_date'
        ).execute()
        
        deals_data = result.data
        
        print(f"📊 Fetched {len(deals_data):,} deals")
        print(f"🔍 Sample fields: {list(deals_data[0].keys()) if deals_data else 'No data'}")
        print()
        
        return deals_data
        
    except Exception as e:
        print(f"❌ Data fetch failed: {e}")
        return []

def create_deals_by_source_pie_chart(deals_data):
    """Create a pie chart showing deals by source (deal_type)."""
    
    print("📊 CREATING DEALS BY SOURCE PIE CHART")
    print("-" * 50)
    
    if not deals_data:
        print("❌ No data available for chart")
        return
    
    # Count deals by source (deal_type - this is the actual source field!)
    deal_sources = [deal.get('deal_type', 'Unknown') for deal in deals_data]
    deal_source_counts = Counter(deal_sources)
    
    print("🎯 Deal Sources Found:")
    for source, count in deal_source_counts.most_common():
        percentage = (count / len(deals_data)) * 100
        print(f"   {source}: {count:,} deals ({percentage:.1f}%)")
    print()
    
    # Create the pie chart
    plt.figure(figsize=(12, 8))
    
    # Prepare data
    labels = list(deal_source_counts.keys())
    sizes = list(deal_source_counts.values())
    
    # Create colors
    colors = plt.cm.Set3(range(len(labels)))
    
    # Create pie chart
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    
    # Styling
    plt.title('RoofMaxx Deals by Source\n868 Total Deals', 
              fontsize=16, fontweight='bold', pad=20)
    
    plt.axis('equal')  # Equal aspect ratio ensures pie is circular
    
    # Add total deals annotation
    plt.figtext(0.5, 0.02, f'Total Deals: {len(deals_data):,} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 
                ha='center', fontsize=10, style='italic')
    
    # Save the chart
    output_dir = 'data/outputs/graphs'
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f'{output_dir}/roofmaxx_deals_by_source_pie_chart.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    
    print(f"✅ Chart saved: {filename}")
    print()
    
    # Show the chart
    plt.show()
    
    return deal_source_counts

def create_geographic_distribution(deals_data):
    """Create a bar chart of deals by city/state."""
    
    print("🗺️ CREATING GEOGRAPHIC DISTRIBUTION")
    print("-" * 40)
    
    if not deals_data:
        print("❌ No data available")
        return
    
    # Count deals by city
    cities = [deal.get('city', 'Unknown') for deal in deals_data if deal.get('city')]
    city_counts = Counter(cities)
    
    # Get top 15 cities
    top_cities = dict(city_counts.most_common(15))
    
    print("🏙️ Top Cities:")
    for city, count in list(top_cities.items())[:10]:
        print(f"   {city}: {count:,} deals")
    print()
    
    # Create bar chart
    plt.figure(figsize=(14, 8))
    
    cities_list = list(top_cities.keys())
    counts_list = list(top_cities.values())
    
    bars = plt.bar(cities_list, counts_list, color='skyblue', edgecolor='navy', alpha=0.7)
    
    plt.title('RoofMaxx Deals by City (Top 15)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('City', fontsize=12)
    plt.ylabel('Number of Deals', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # Save
    filename = 'data/outputs/graphs/roofmaxx_deals_by_city.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    
    print(f"✅ Geographic chart saved: {filename}")
    print()
    
    plt.show()
    
    return top_cities

def create_deal_stage_analysis(deals_data):
    """Analyze deals by stage."""
    
    print("📈 DEAL STAGE ANALYSIS")
    print("-" * 30)
    
    if not deals_data:
        print("❌ No data available")
        return
    
    # Count by deal stage
    stages = [deal.get('deal_stage', 'Unknown') for deal in deals_data]
    stage_counts = Counter(stages)
    
    print("🎯 Deal Stages:")
    for stage, count in stage_counts.most_common():
        percentage = (count / len(deals_data)) * 100
        print(f"   {stage}: {count:,} deals ({percentage:.1f}%)")
    print()
    
    return stage_counts

def display_business_summary(deals_data, deal_sources, top_cities):
    """Display a comprehensive business summary."""
    
    print("🏢 BUSINESS INTELLIGENCE SUMMARY")
    print("=" * 60)
    
    total_deals = len(deals_data)
    
    # Basic stats
    print(f"📊 OVERVIEW:")
    print(f"   Total Deals: {total_deals:,}")
    print(f"   Lead Sources: {len(deal_sources)} different types")
    print(f"   Cities Served: {len(top_cities)}")
    print()
    
    # Top source
    if deal_sources:
        top_source = deal_sources.most_common(1)[0]
        top_percentage = (top_source[1] / total_deals) * 100
        print(f"🎯 TOP LEAD SOURCE:")
        print(f"   {top_source[0]}: {top_source[1]:,} deals ({top_percentage:.1f}%)")
        print()
    
    # Top city
    if top_cities:
        top_city = list(top_cities.items())[0]
        city_percentage = (top_city[1] / total_deals) * 100
        print(f"🏙️ TOP MARKET:")
        print(f"   {top_city[0]}: {top_city[1]:,} deals ({city_percentage:.1f}%)")
        print()
    
    # States served
    states = set([deal.get('state') for deal in deals_data if deal.get('state')])
    print(f"🗺️ STATES SERVED: {', '.join(sorted(states)) if states else 'Unknown'}")
    print()
    
    print("🍆💥 TOM'S REACTION: 'This is REAL business intelligence!'")

def main():
    """Main analytics function."""
    
    print("📊 ROOFMAXX DEALS ANALYTICS & VISUALIZATION")
    print("=" * 70)
    print("🎯 Analyzing your 868 deals from Supabase!")
    print("🍆💥 Preparing Tom's mind for complete demolition!")
    print()
    
    # Connect to database
    client = connect_to_supabase()
    if not client:
        print("❌ Cannot proceed without database connection")
        return
    
    # Fetch data
    deals_data = fetch_deals_data(client)
    if not deals_data:
        print("❌ No data to analyze")
        return
    
    print("🚀 CREATING VISUALIZATIONS...")
    print()
    
    # Create pie chart (main request)
    deal_sources = create_deals_by_source_pie_chart(deals_data)
    
    # Create geographic analysis
    top_cities = create_geographic_distribution(deals_data)
    
    # Analyze deal stages
    stage_counts = create_deal_stage_analysis(deals_data)
    
    # Business summary
    display_business_summary(deals_data, deal_sources, top_cities)
    
    print(f"\n🎯 🍆💥 ANALYTICS COMPLETE! 🍆💥")
    print("=" * 60)
    print("🏆 Charts created and saved to data/outputs/graphs/")
    print("📊 Your business intelligence is now VISUAL!")
    print("🤯 Tom's mind status: COMPLETELY BLOWN!")

if __name__ == "__main__":
    main() 