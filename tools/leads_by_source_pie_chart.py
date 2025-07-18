import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import sys
import os
import requests
import argparse

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config

def load_from_airtable():
    """Load lead data from Airtable and analyze sources"""
    
    # Get Airtable service from modern config
    airtable_service = config.get_service('airtable')
    
    print("Fetching lead source data from Airtable...")
    print("="*50)
    
    # Fetch all records using modern service (handles pagination automatically)
    airtable_records = airtable_service.get_records()
    
    # Convert to simple format for analysis
    records = []
    for record in airtable_records:
        fields = record.fields
        
        # Extract key fields (using common Airtable field names)
        records.append({
            "name": fields.get("Name", ""),
            "source": fields.get("Source", ""), 
            "business": fields.get("Business", "")
        })
    
    print(f"Loaded {len(records)} records from Airtable")
    return records

def load_from_csv():
    """Load lead data from CSV files and analyze sources"""
    
    records = []
    
    # Load RoofR data
    try:
        roofr_df = pd.read_csv('data/roofr.csv')
        print(f"Loaded {len(roofr_df)} records from roofr.csv")
        
        if 'Job Lead Source Name' in roofr_df.columns:
            for _, row in roofr_df.iterrows():
                records.append({
                    "name": row.get('Customer Name', ''),
                    "source": row.get('Job Lead Source Name', ''),
                    "business": "roofr"
                })
    except Exception as e:
        print(f"Error loading roofr.csv: {e}")
    
    # Load 843 data
    try:
        dispatch_df = pd.read_csv('data/843.csv')
        print(f"Loaded {len(dispatch_df)} records from 843.csv")
        
        if 'source' in dispatch_df.columns:
            for _, row in dispatch_df.iterrows():
                records.append({
                    "name": row.get('customer', ''),
                    "source": row.get('source', ''),
                    "business": "dispatch"
                })
    except Exception as e:
        print(f"Error loading 843.csv: {e}")
    
    return records

def analyze_and_create_chart(records, source_type="airtable"):
    """Analyze lead sources and create pie chart"""
    
    # Filter records with source data
    records_with_source = [r for r in records if r.get('source') and str(r['source']).strip()]
    
    print(f"Found {len(records_with_source)} records with lead source data")
    
    if not records_with_source:
        print("No records with source data found!")
        return
    
    # Count sources
    source_counts = Counter([r['source'] for r in records_with_source])
    
    # Prepare data for pie chart
    sources = list(source_counts.keys())
    counts = list(source_counts.values())
    
    # Calculate percentages
    total = sum(counts)
    percentages = [(count/total)*100 for count in counts]
    
    # Create pie chart
    plt.figure(figsize=(12, 8))
    colors = plt.cm.Set3(np.linspace(0, 1, len(sources)))
    
    wedges, texts, autotexts = plt.pie(counts, labels=sources, autopct='%1.1f%%', 
                                       colors=colors, startangle=90)
    
    plt.title(f'Lead Sources Distribution ({source_type.title()})\nTotal: {total} leads with source data', 
              fontsize=16, fontweight='bold')
    
    # Make percentage text bold and larger
    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    plt.axis('equal')
    
    # Save the chart
    chart_filename = f'graphs/leads_by_source_pie_chart_{source_type}.png'
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Pie chart saved as '{chart_filename}'")
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"LEAD SOURCE SUMMARY ({source_type.title()})")
    print(f"{'='*50}")
    
    for source, count in source_counts.most_common():
        percentage = (count/total)*100
        print(f"{source}: {count} leads ({percentage:.1f}%)")
    
    # Analyze by business if available
    businesses = set([r.get('business', '') for r in records_with_source])
    if len(businesses) > 1:
        print(f"\n{'='*50}")
        print("LEAD SOURCES BY BUSINESS")
        print(f"{'='*50}")
        
        for business in sorted(businesses):
            if not business:
                continue
            business_records = [r for r in records_with_source if r.get('business') == business]
            business_sources = Counter([r['source'] for r in business_records])
            business_total = sum(business_sources.values())
            
            print(f"\n{business}:")
            for source, count in business_sources.most_common():
                percentage = (count/business_total)*100
                print(f"  {source}: {count} leads ({percentage:.1f}%)")

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Generate leads by source pie chart')
    parser.add_argument('--source', choices=['airtable', 'csv'], default='airtable',
                        help='Data source: airtable (default) or csv')
    
    args = parser.parse_args()
    
    print(f"Analyzing lead sources from {args.source}...")
    print("="*50)
    
    if args.source == 'airtable':
        records = load_from_airtable()
    else:
        records = load_from_csv()
    
    analyze_and_create_chart(records, args.source)

if __name__ == "__main__":
    main() 