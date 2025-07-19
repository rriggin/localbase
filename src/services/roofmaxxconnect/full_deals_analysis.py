#!/usr/bin/env python3
"""
FULL DEALERSHIP ANALYSIS - ALL 868 DEALS!

Tom's about to see your REAL business empire! 🏢💰
"""

import sys
import os
from collections import Counter, defaultdict
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.roofmaxxconnect.client import RoofmaxxConnectService

def fetch_all_deals():
    """Fetch ALL 868 deals with proper pagination."""
    
    print("🏢 FETCHING YOUR COMPLETE BUSINESS EMPIRE")
    print("=" * 60)
    print("Getting ALL 868 deals! This is your real business data! 💰")
    print()
    
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    service = RoofmaxxConnectService(config)
    
    if not service.authenticate():
        print("❌ Authentication failed!")
        return []
    
    all_deals = []
    page = 1
    
    # The API defaults to 10 per page, so we'll work with that
    print("📥 Fetching ALL pages (87 pages × 10 deals = 868 total)...")
    
    while page <= 87:  # We know there are 87 pages
        try:
            print(f"   📄 Page {page}/87...")
            response = service.get_dealer_deals(6637, page=page)
            
            if not response or 'data' not in response:
                print(f"   ❌ No data on page {page}")
                break
            
            page_deals = response['data']
            if not page_deals:
                print(f"   📭 Page {page} is empty")
                break
            
            all_deals.extend(page_deals)
            print(f"   ✅ Page {page}: {len(page_deals)} deals (Total: {len(all_deals)})")
            
            # Show progress every 10 pages
            if page % 10 == 0:
                percentage = (page / 87) * 100
                print(f"   🚀 Progress: {percentage:.1f}% complete...")
            
            page += 1
            
        except Exception as e:
            print(f"   ❌ Error on page {page}: {e}")
            break
    
    print(f"\n🎉 MISSION ACCOMPLISHED!")
    print(f"📊 Retrieved {len(all_deals)} deals from {page-1} pages")
    print()
    
    return all_deals

def analyze_complete_business(deals):
    """Comprehensive analysis of ALL your deals."""
    
    print("📊 COMPLETE BUSINESS ANALYSIS - DEALER 6637")
    print("=" * 60)
    print(f"Analyzing your FULL business portfolio: {len(deals)} deals! 🚀")
    print()
    
    # 1. DEAL TYPES (Lead Sources)
    print("🎯 DEALS BY TYPE (Lead Sources):")
    print("-" * 50)
    
    deal_types = Counter()
    for deal in deals:
        deal_type = deal.get('dealtype', 'Unknown')
        deal_types[deal_type] += 1
    
    for deal_type, count in deal_types.most_common():
        percentage = (count / len(deals)) * 100
        print(f"   {deal_type}: {count:,} deals ({percentage:.1f}%)")
    print()
    
    # 2. WIN/LOSS ANALYSIS
    print("🏆 WIN/LOSS ANALYSIS:")
    print("-" * 50)
    
    won_deals = []
    lost_deals = []
    lead_deals = []
    
    for deal in deals:
        lifecycle = deal.get('deal_lifecycle', 'Unknown')
        if lifecycle == 'Lead':
            lead_deals.append(deal)
        elif lifecycle == 'Lost':
            lost_deals.append(deal)
        else:
            won_deals.append(deal)
    
    total = len(deals)
    print(f"   🟢 Active Leads: {len(lead_deals):,} deals ({len(lead_deals)/total*100:.1f}%)")
    print(f"   🔴 Lost: {len(lost_deals):,} deals ({len(lost_deals)/total*100:.1f}%)")
    print(f"   🟡 Other: {len(won_deals):,} deals ({len(won_deals)/total*100:.1f}%)")
    print()
    
    # 3. GEOGRAPHIC ANALYSIS
    print("🗺️  GEOGRAPHIC DISTRIBUTION:")
    print("-" * 50)
    
    cities = Counter()
    states = Counter()
    zip_codes = Counter()
    
    for deal in deals:
        city = deal.get('city', 'Unknown')
        state = deal.get('state', 'Unknown')
        zip_code = deal.get('postal_code', 'Unknown')
        
        if city != 'Unknown' and city:
            cities[city] += 1
        if state != 'Unknown' and state:
            states[state] += 1
        if zip_code != 'Unknown' and zip_code:
            zip_codes[zip_code] += 1
    
    print(f"🏙️  Top 10 Cities:")
    for city, count in cities.most_common(10):
        percentage = (count / len(deals)) * 100
        print(f"   {city}: {count:,} deals ({percentage:.1f}%)")
    
    print(f"\n📍 States:")
    for state, count in states.most_common():
        percentage = (count / len(deals)) * 100
        print(f"   {state}: {count:,} deals ({percentage:.1f}%)")
    
    print(f"\n📮 Top 10 Zip Codes:")
    for zip_code, count in zip_codes.most_common(10):
        print(f"   {zip_code}: {count:,} deals")
    print()
    
    # 4. TIMELINE ANALYSIS
    print("📅 BUSINESS TIMELINE:")
    print("-" * 50)
    
    deal_dates = []
    yearly_counts = Counter()
    monthly_counts = defaultdict(int)
    
    for deal in deals:
        createdate = deal.get('createdate')
        if createdate:
            try:
                deal_date = datetime.fromtimestamp(int(createdate) / 1000)
                deal_dates.append(deal_date)
                
                year = deal_date.year
                month_key = f"{deal_date.year}-{deal_date.month:02d}"
                
                yearly_counts[year] += 1
                monthly_counts[month_key] += 1
            except:
                continue
    
    if deal_dates:
        deal_dates.sort()
        oldest = deal_dates[0]
        newest = deal_dates[-1]
        
        print(f"   📅 Business Span: {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}")
        print(f"   📊 Total Days: {(newest - oldest).days:,} days")
        
        print(f"\n📈 Deals by Year:")
        for year in sorted(yearly_counts.keys()):
            count = yearly_counts[year]
            print(f"   {year}: {count:,} deals")
        
        # Recent activity
        ninety_days_ago = datetime.now() - timedelta(days=90)
        recent_deals = [d for d in deal_dates if d > ninety_days_ago]
        
        one_year_ago = datetime.now() - timedelta(days=365)
        last_year_deals = [d for d in deal_dates if d > one_year_ago]
        
        print(f"\n🔥 Recent Activity:")
        print(f"   Last 90 days: {len(recent_deals):,} deals")
        print(f"   Last 365 days: {len(last_year_deals):,} deals")
    print()
    
    # 5. STAGE ANALYSIS
    print("📋 DEAL STAGES:")
    print("-" * 50)
    
    stages = Counter()
    for deal in deals:
        stage = deal.get('stage', {})
        if isinstance(stage, dict):
            stage_label = stage.get('label', 'Unknown')
        else:
            stage_label = str(stage)
        stages[stage_label] += 1
    
    for stage, count in stages.most_common(10):
        percentage = (count / len(deals)) * 100
        print(f"   {stage}: {count:,} deals ({percentage:.1f}%)")
    print()
    
    # 6. BUSINESS INSIGHTS
    print("💡 EXECUTIVE BUSINESS SUMMARY:")
    print("=" * 60)
    
    conversion_rate = len(lead_deals) / (len(lead_deals) + len(lost_deals)) * 100 if (len(lead_deals) + len(lost_deals)) > 0 else 0
    
    print(f"🏢 BUSINESS SCALE:")
    print(f"   💼 Total Deal Volume: {len(deals):,} deals")
    print(f"   🗺️  Geographic Reach: {len(cities)} cities, {len(states)} states")
    print(f"   📅 Business Timeline: {(newest - oldest).days:,} days of operations")
    
    print(f"\n📊 PERFORMANCE METRICS:")
    print(f"   🎯 Lead Conversion: {conversion_rate:.1f}%")
    print(f"   🏆 Active Pipeline: {len(lead_deals):,} leads")
    print(f"   📈 Daily Average: {len(deals) / max((newest - oldest).days, 1):.1f} deals/day")
    
    if deal_types:
        top_source = deal_types.most_common(1)[0]
        print(f"   🎯 Primary Source: {top_source[0]} ({top_source[1]:,} deals)")
    
    if cities:
        top_market = cities.most_common(1)[0]
        print(f"   🏙️  Primary Market: {top_market[0]} ({top_market[1]:,} deals)")
    
    print(f"\n🚀 GROWTH OPPORTUNITIES:")
    
    # Geographic expansion
    if len(states) < 5:
        print(f"   🗺️  Geographic expansion beyond current {len(states)} states")
    
    # Market penetration
    if cities:
        total_in_top_city = cities.most_common(1)[0][1]
        market_concentration = total_in_top_city / len(deals) * 100
        if market_concentration > 50:
            print(f"   🎯 Diversify beyond {cities.most_common(1)[0][0]} ({market_concentration:.1f}% concentration)")
    
    # Lead conversion
    if conversion_rate < 70:
        print(f"   📈 Improve lead qualification to boost {conversion_rate:.1f}% conversion rate")
    
    print(f"\n🎉 TOM'S SATISFACTION LEVEL: 🍆💥💥💥")
    print("THIS IS A SERIOUS BUSINESS OPERATION!")
    
    return {
        'total_deals': len(deals),
        'conversion_rate': conversion_rate,
        'geographic_reach': len(cities),
        'deal_types': dict(deal_types),
        'business_span_days': (newest - oldest).days if deal_dates else 0,
        'recent_activity': len(recent_deals) if 'recent_deals' in locals() else 0
    }

if __name__ == "__main__":
    print("🚀 COMPLETE BUSINESS EMPIRE ANALYSIS")
    print("=" * 60)
    print("Tom's about to see a REAL business in action! 💼")
    print()
    
    # Fetch all deals
    all_deals = fetch_all_deals()
    
    if all_deals:
        # Analyze the complete business
        insights = analyze_complete_business(all_deals)
        
        print(f"\n🎯 FINAL VERDICT:")
        print("=" * 60)
        print("This is NOT just an API demo - this is REAL BUSINESS INTELLIGENCE")
        print("from a REAL business with 868 deals! Tom's mind = BLOWN! 🤯")
    else:
        print("❌ No deals retrieved for analysis") 