#!/usr/bin/env python3
"""
Enhanced Deals Analysis for Dealer 6637

Using the ACTUAL data fields to provide ACTIONABLE business intelligence!
Tom's about to see the full picture! 💰
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

def enhanced_dealership_analysis():
    """Enhanced analysis using actual available data fields."""
    
    print("📊 ENHANCED DEALERSHIP ANALYSIS - DEALER 6637")
    print("=" * 60)
    print("Using REAL data fields for ACTIONABLE insights! 🎯")
    print()
    
    # Get the data
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    service = RoofmaxxConnectService(config)
    
    if not service.authenticate():
        print("❌ Authentication failed!")
        return
    
    # Get ALL deals from all pages
    print("📥 Fetching ALL your deals...")
    all_deals = []
    page = 1
    
    while True:
        print(f"   📄 Fetching page {page}...")
        deals_response = service.get_dealer_deals(6637, page=page, per_page=100)
        
        if not deals_response or 'data' not in deals_response:
            print(f"   📭 No more deals found")
            break
        
        page_deals = deals_response['data']
        if not page_deals:
            print(f"   📭 Page {page} is empty")
            break
        
        all_deals.extend(page_deals)
        print(f"   ✅ Page {page}: {len(page_deals)} deals")
        
        # Check if there are more pages
        if len(page_deals) < 100:  # Less than full page means we're done
            break
            
        page += 1
        
        # Safety limit
        if page > 100:
            print("   ⚠️  Reached safety limit of 100 pages")
            break
    
    deals = all_deals
    
    if not deals:
        print("No deals found!")
        return
    
    print(f"\n🎉 SUCCESS! Retrieved {len(deals)} total deals!")
    print(f"📊 Now analyzing your COMPLETE deal history...")
    print()
    
    # ANALYSIS 1: Deal Types (This is like "source")
    print("🎯 DEALS BY TYPE (Your Lead Sources):")
    print("-" * 50)
    
    deal_types = Counter()
    for deal in deals:
        deal_type = deal.get('dealtype', 'Unknown')
        deal_types[deal_type] += 1
    
    for deal_type, count in deal_types.most_common():
        percentage = (count / len(deals)) * 100
        print(f"   {deal_type}: {count} deals ({percentage:.1f}%)")
    print()
    
    # ANALYSIS 2: Deal Lifecycle Analysis
    print("📈 DEAL LIFECYCLE BREAKDOWN:")
    print("-" * 50)
    
    lifecycles = Counter()
    for deal in deals:
        lifecycle = deal.get('deal_lifecycle', 'Unknown')
        lifecycles[lifecycle] += 1
    
    for lifecycle, count in lifecycles.most_common():
        percentage = (count / len(deals)) * 100
        print(f"   {lifecycle}: {count} deals ({percentage:.1f}%)")
    print()
    
    # ANALYSIS 3: Win/Loss Analysis
    print("🏆 WIN/LOSS ANALYSIS:")
    print("-" * 50)
    
    won_deals = []
    lost_deals = []
    in_progress = []
    
    for deal in deals:
        stage = deal.get('stage', {})
        if isinstance(stage, dict):
            stage_label = stage.get('label', 'Unknown')
        else:
            stage_label = str(stage)
        
        if 'accepted' in stage_label.lower() or 'won' in stage_label.lower() or 'closed' in stage_label.lower():
            won_deals.append(deal)
        elif 'lost' in stage_label.lower():
            lost_deals.append(deal)
        else:
            in_progress.append(deal)
    
    total = len(deals)
    print(f"   🟢 Won/Accepted: {len(won_deals)} deals ({len(won_deals)/total*100:.1f}%)")
    print(f"   🔴 Lost: {len(lost_deals)} deals ({len(lost_deals)/total*100:.1f}%)")
    print(f"   🟡 In Progress: {len(in_progress)} deals ({len(in_progress)/total*100:.1f}%)")
    print()
    
    # ANALYSIS 4: Geographic Analysis
    print("🗺️  GEOGRAPHIC DISTRIBUTION:")
    print("-" * 50)
    
    cities = Counter()
    states = Counter()
    zip_codes = Counter()
    
    for deal in deals:
        city = deal.get('city', 'Unknown')
        state = deal.get('state', 'Unknown')
        zip_code = deal.get('postal_code', 'Unknown')
        
        if city != 'Unknown':
            cities[city] += 1
        if state != 'Unknown':
            states[state] += 1
        if zip_code != 'Unknown':
            zip_codes[zip_code] += 1
    
    print(f"📍 Cities:")
    for city, count in cities.most_common(5):
        print(f"   {city}: {count} deals")
    
    print(f"\n📍 States:")
    for state, count in states.most_common():
        print(f"   {state}: {count} deals")
    
    print(f"\n📍 Top Zip Codes:")
    for zip_code, count in zip_codes.most_common(5):
        print(f"   {zip_code}: {count} deals")
    print()
    
    # ANALYSIS 5: Roof Maxx vs Other Services
    print("🏠 SERVICE TYPE ANALYSIS:")
    print("-" * 50)
    
    roof_maxx_jobs = 0
    other_jobs = 0
    
    for deal in deals:
        is_roof_maxx = deal.get('is_roof_maxx_job', False)
        if is_roof_maxx:
            roof_maxx_jobs += 1
        else:
            other_jobs += 1
    
    print(f"   🔧 Roof Maxx Jobs: {roof_maxx_jobs} deals ({roof_maxx_jobs/total*100:.1f}%)")
    print(f"   🏗️  Other Services: {other_jobs} deals ({other_jobs/total*100:.1f}%)")
    print()
    
    # ANALYSIS 6: Warranty Analysis
    print("🛡️  WARRANTY ANALYSIS:")
    print("-" * 50)
    
    with_warranty = 0
    without_warranty = 0
    
    for deal in deals:
        has_warranty = deal.get('has_warranty', False)
        if has_warranty:
            with_warranty += 1
        else:
            without_warranty += 1
    
    print(f"   ✅ With Warranty: {with_warranty} deals ({with_warranty/total*100:.1f}%)")
    print(f"   ❌ Without Warranty: {without_warranty} deals ({without_warranty/total*100:.1f}%)")
    print()
    
    # ANALYSIS 7: Deal Timeline Analysis (using createdate)
    print("📅 TIMELINE ANALYSIS:")
    print("-" * 50)
    
    deal_dates = []
    for deal in deals:
        createdate = deal.get('createdate')
        if createdate:
            try:
                # Convert from timestamp (assuming it's in milliseconds)
                deal_date = datetime.fromtimestamp(int(createdate) / 1000)
                deal_dates.append(deal_date)
            except:
                continue
    
    if deal_dates:
        deal_dates.sort()
        oldest = deal_dates[0]
        newest = deal_dates[-1]
        
        print(f"   📅 Date Range: {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}")
        print(f"   📊 Deal Span: {(newest - oldest).days} days")
        
        # Recent activity (last 90 days)
        ninety_days_ago = datetime.now() - timedelta(days=90)
        recent_deals = [d for d in deal_dates if d > ninety_days_ago]
        print(f"   🔥 Recent Activity (90 days): {len(recent_deals)} deals")
    print()
    
    # BUSINESS RECOMMENDATIONS
    print("💡 ACTIONABLE BUSINESS RECOMMENDATIONS:")
    print("=" * 60)
    
    win_rate = len(won_deals) / total * 100
    
    print(f"🎯 PERFORMANCE METRICS:")
    print(f"   • Win Rate: {win_rate:.1f}% ({len(won_deals)}/{total} deals)")
    print(f"   • Primary Market: {list(cities.keys())[0] if cities else 'Unknown'}")
    print(f"   • Main Service: {'Roof Maxx' if roof_maxx_jobs > other_jobs else 'Other Services'}")
    
    print(f"\n🚀 GROWTH OPPORTUNITIES:")
    if win_rate > 60:
        print(f"   • Excellent win rate! Focus on lead volume increase")
    else:
        print(f"   • Improve win rate through better qualification")
    
    if len(cities) == 1:
        print(f"   • Consider geographic expansion beyond {list(cities.keys())[0]}")
    else:
        print(f"   • Good geographic diversification across {len(cities)} cities")
    
    if roof_maxx_jobs < other_jobs:
        print(f"   • Opportunity to increase Roof Maxx service penetration")
    
    if with_warranty < without_warranty:
        print(f"   • Increase warranty attachment rate for recurring revenue")
    
    print(f"\n📊 EXECUTIVE SUMMARY:")
    print(f"   💼 Total Pipeline: {total} deals")
    print(f"   🏆 Success Rate: {win_rate:.1f}%")
    print(f"   🗺️  Market Coverage: {len(cities)} cities, {len(states)} states")
    print(f"   🔧 Service Mix: {roof_maxx_jobs} Roof Maxx, {other_jobs} Other")
    print(f"   🛡️  Warranty Rate: {with_warranty/total*100:.1f}%")
    
    return {
        'total_deals': total,
        'win_rate': win_rate,
        'deal_types': dict(deal_types),
        'geographic_coverage': len(cities),
        'roof_maxx_percentage': roof_maxx_jobs/total*100,
        'warranty_rate': with_warranty/total*100
    }

if __name__ == "__main__":
    print("🚀 ENHANCED BUSINESS INTELLIGENCE")
    print("=" * 60)
    print("THIS is what Tom wants to see! Real insights from real data! 💰")
    print()
    
    result = enhanced_dealership_analysis()
    
    if result:
        print(f"\n🎉 TOM'S SATISFACTION LEVEL: 🍆🍆🍆")
        print("=" * 60)
        print("NOW we're talking business intelligence! 🚀") 