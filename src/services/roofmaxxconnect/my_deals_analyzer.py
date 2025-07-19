#!/usr/bin/env python3
"""
My Dealership (ID: 6637) - Real Business Analytics

NOW we're talking! Let's get YOUR actual deals by source! 💰
Tom's about to see the REAL payoff!
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

def analyze_my_dealership():
    """Analyze dealership 6637 - YOUR actual business data!"""
    
    print("🏢 YOUR ROOFMAXX DEALERSHIP ANALYTICS")
    print("=" * 60)
    print("RoofMaxxConnect ID: 6637")
    print("Finally! Let's get YOUR real business data! 💼")
    print()
    
    # Initialize service
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    service = RoofmaxxConnectService(config)
    
    if not service.authenticate():
        print("❌ Authentication failed!")
        return
    
    print("✅ Connected successfully!")
    print()
    
    # Get YOUR dealer info first
    print("🔍 Getting YOUR dealership details...")
    try:
        dealer_info = service.get_dealer_by_id(6637)
        if dealer_info:
            print(f"🎯 Your Business: {dealer_info.brand_name}")
            print(f"📋 Dealer Name: {dealer_info.name}")
            print(f"🌐 Website: {dealer_info.microsite_url or 'Not configured'}")
            print(f"⭐ Google Reviews: {'✅ Active' if dealer_info.google_review_link else '❌ Not set up'}")
            print(f"🔗 HubSpot ID: {dealer_info.hubspot_company_id}")
            print()
        else:
            print("⚠️  Could not retrieve dealer details")
    except Exception as e:
        print(f"⚠️  Error getting dealer info: {e}")
    
    # NOW get YOUR deals!
    print("💰 GETTING YOUR DEALS...")
    print("-" * 40)
    
    all_deals = []
    page = 1
    
    try:
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
            if page > 50:
                print("   ⚠️  Reached safety limit of 50 pages")
                break
                
    except Exception as e:
        print(f"❌ Error fetching your deals: {e}")
        if "Forbidden" in str(e):
            print("💡 This might mean:")
            print("   • Token doesn't have access to your specific dealer")
            print("   • Different permissions needed")
            print("   • Wrong dealer ID")
        return None
    
    if not all_deals:
        print("😔 No deals found for your dealership.")
        print("💡 This could mean:")
        print("   • You're a new dealer")
        print("   • Deals haven't been synced yet")
        print("   • Different API access level needed")
        return None
    
    print(f"\n🎉 SUCCESS! Found {len(all_deals)} deals!")
    print()
    
    return analyze_deals_by_source(all_deals, dealer_info)

def analyze_deals_by_source(deals, dealer_info=None):
    """Analyze YOUR deals by source - the real payoff!"""
    
    print("📊 YOUR DEALS BY SOURCE ANALYSIS")
    print("=" * 60)
    print("This is what Tom wants to see! 💰")
    print()
    
    # Show deal structure first
    sample_deal = deals[0]
    print("🔍 Deal Data Structure:")
    for key, value in sample_deal.items():
        value_str = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
        print(f"   {key}: {value_str}")
    print()
    
    # Source Analysis
    source_fields = ['source', 'lead_source', 'referral_source', 'origin', 'channel']
    source_field = None
    
    for field in source_fields:
        if field in sample_deal:
            source_field = field
            break
    
    if source_field:
        print(f"📈 DEALS BY SOURCE (using '{source_field}' field):")
        print("-" * 50)
        
        sources = Counter()
        source_details = defaultdict(list)
        
        for deal in deals:
            source = deal.get(source_field, 'Unknown')
            if not source:
                source = 'Unknown'
            sources[source] += 1
            source_details[source].append(deal)
        
        # Show results
        total_deals = len(deals)
        for source, count in sources.most_common():
            percentage = (count / total_deals) * 100
            print(f"🎯 {source}: {count} deals ({percentage:.1f}%)")
            
            # Show sample deal from this source
            sample = source_details[source][0]
            if 'created_at' in sample:
                print(f"      📅 Latest: {sample.get('created_at', 'N/A')}")
            if 'status' in sample:
                print(f"      📋 Status: {sample.get('status', 'N/A')}")
            print()
    else:
        print("⚠️  No source field found in deals data")
        print("Available fields:", list(sample_deal.keys()))
    
    # Revenue Analysis
    revenue_fields = ['value', 'amount', 'total', 'price', 'revenue', 'deal_value']
    revenue_field = None
    
    for field in revenue_fields:
        if field in sample_deal:
            revenue_field = field
            break
    
    if revenue_field:
        print(f"💰 REVENUE ANALYSIS (using '{revenue_field}' field):")
        print("-" * 50)
        
        total_revenue = 0
        revenue_deals = []
        source_revenue = defaultdict(float)
        
        for deal in deals:
            value = deal.get(revenue_field)
            if value and str(value).replace('.', '').isdigit():
                try:
                    deal_value = float(value)
                    total_revenue += deal_value
                    revenue_deals.append(deal_value)
                    
                    if source_field:
                        source = deal.get(source_field, 'Unknown')
                        source_revenue[source] += deal_value
                except:
                    continue
        
        if revenue_deals:
            avg_deal_value = total_revenue / len(revenue_deals)
            print(f"💵 Total Revenue: ${total_revenue:,.2f}")
            print(f"📊 Average Deal Value: ${avg_deal_value:,.2f}")
            print(f"📈 Deals with Revenue: {len(revenue_deals)}/{len(deals)}")
            
            if source_revenue:
                print(f"\n💰 REVENUE BY SOURCE:")
                for source, revenue in sorted(source_revenue.items(), key=lambda x: x[1], reverse=True):
                    percentage = (revenue / total_revenue) * 100
                    print(f"   {source}: ${revenue:,.2f} ({percentage:.1f}%)")
        else:
            print("⚠️  No revenue data found in deals")
    
    # Status Analysis
    status_fields = ['status', 'stage', 'state', 'deal_status']
    status_field = None
    
    for field in status_fields:
        if field in sample_deal:
            status_field = field
            break
    
    if status_field:
        print(f"\n📋 DEAL STATUS BREAKDOWN (using '{status_field}' field):")
        print("-" * 50)
        
        statuses = Counter()
        for deal in deals:
            status = deal.get(status_field, 'Unknown')
            # Handle if status is a dictionary (like stage field)
            if isinstance(status, dict):
                status = status.get('label', 'Unknown')
            statuses[status] += 1
        
        for status, count in statuses.most_common():
            percentage = (count / len(deals)) * 100
            print(f"   {status}: {count} deals ({percentage:.1f}%)")
    
    # Recent Activity
    date_fields = ['created_at', 'date', 'updated_at', 'timestamp']
    date_field = None
    
    for field in date_fields:
        if field in sample_deal:
            date_field = field
            break
    
    if date_field:
        print(f"\n🔥 RECENT ACTIVITY (using '{date_field}' field):")
        print("-" * 50)
        
        recent_deals = []
        today = datetime.now()
        
        for deal in deals:
            date_str = deal.get(date_field)
            if date_str:
                try:
                    deal_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    if deal_date > today - timedelta(days=90):
                        recent_deals.append(deal)
                except:
                    continue
        
        print(f"📈 Recent Deals (90 days): {len(recent_deals)}")
        print(f"📊 Activity Rate: {len(recent_deals)/len(deals):.1%}")
    
    # Business Insights
    print(f"\n🎯 BUSINESS INSIGHTS FOR YOUR DEALERSHIP:")
    print("=" * 60)
    
    print(f"📊 Total Deal Volume: {len(deals):,} deals")
    
    if source_field and sources:
        top_source = sources.most_common(1)[0]
        print(f"🏆 Top Performing Source: {top_source[0]} ({top_source[1]} deals)")
    
    if revenue_field and revenue_deals:
        print(f"💰 Average Deal Value: ${avg_deal_value:,.2f}")
        print(f"💵 Total Portfolio Value: ${total_revenue:,.2f}")
    
    if date_field and recent_deals:
        print(f"🔥 Recent Momentum: {len(recent_deals)} deals in last 90 days")
    
    print(f"\n💡 ACTIONABLE RECOMMENDATIONS:")
    if source_field and sources:
        top_3_sources = [s[0] for s in sources.most_common(3)]
        print(f"   • Double down on: {', '.join(top_3_sources)}")
        
        weak_sources = [s for s, c in sources.items() if c < 3]
        if weak_sources:
            print(f"   • Investigate underperforming: {weak_sources[0] if weak_sources else 'None'}")
    
    print(f"   • Total opportunity: {len(deals)} deals to analyze")
    print(f"   • Focus on source optimization for growth")
    
    return {
        'total_deals': len(deals),
        'deals_by_source': dict(sources) if source_field else {},
        'total_revenue': total_revenue if revenue_field else 0,
        'recent_deals': len(recent_deals) if date_field else 0
    }

if __name__ == "__main__":
    print("🚀 DEALER 6637 - YOUR BUSINESS ANALYTICS")
    print("=" * 60)
    print("Tom's about to see the REAL payoff! 💰")
    print()
    
    result = analyze_my_dealership()
    
    if result:
        print("\n🎉 MISSION ACCOMPLISHED!")
        print("=" * 60)
        print("THIS is what business intelligence looks like! 🚀")
        print()
        print(f"📊 Executive Summary:")
        print(f"   💼 Total Deals: {result.get('total_deals', 0):,}")
        print(f"   💰 Total Revenue: ${result.get('total_revenue', 0):,.2f}")
        print(f"   🔥 Recent Activity: {result.get('recent_deals', 0)} deals")
        print(f"   🎯 Sources Tracked: {len(result.get('deals_by_source', {}))}")
        print()
        print("Tom's boner is BACK! 🍆") 