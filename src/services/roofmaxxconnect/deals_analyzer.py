#!/usr/bin/env python3
"""
RoofMaxx Connect Deals Analyzer

Let's find OUR deals and see where the money is coming from!
This is where the real payoff is for Tom! 💰
"""

import sys
import os
from collections import Counter, defaultdict
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.roofmaxxconnect.client import RoofmaxxConnectService
from src.services.roofmaxxconnect.models import DealerRecord

def find_our_dealer_id(service):
    """Find which dealer ID this token belongs to by testing access."""
    print("🔍 Finding our dealer ID...")
    
    # Try common dealer IDs or use a smart approach
    test_ids = [1, 17, 100, 200, 500, 1000, 1500, 2000, 2500, 3000]
    
    for dealer_id in test_ids:
        try:
            print(f"   Testing dealer ID {dealer_id}...")
            response = service.get_dealer_deals(dealer_id, per_page=1)
            if response and 'data' in response:
                print(f"   ✅ SUCCESS! Our dealer ID is: {dealer_id}")
                return dealer_id
        except Exception as e:
            if "Forbidden" not in str(e):
                print(f"   ⚠️  Error testing {dealer_id}: {e}")
            continue
    
    # Try to get current dealer info from profile endpoint
    try:
        print("   🔍 Trying profile/me endpoint...")
        response = service._make_request('GET', '/api/v2/me')
        data = response.json()
        if 'dealer_id' in data:
            return data['dealer_id']
        elif 'id' in data:
            return data['id']
    except:
        pass
    
    # If we can't find it, let's try a different approach
    print("   🤔 Let's try searching dealers for one we can access...")
    dealers_response = service.get_dealers(page=1, per_page=50)
    
    for dealer in dealers_response.data:
        try:
            response = service.get_dealer_deals(dealer.id, per_page=1)
            if response and 'data' in response:
                print(f"   ✅ Found accessible dealer: {dealer.id} - {dealer.brand_name}")
                return dealer.id
        except:
            continue
    
    return None

def analyze_deals_by_source():
    """Analyze our deals by source - this is where the money insights are!"""
    
    print("💰 RoofMaxx Connect Deals Analyzer")
    print("=" * 60)
    print("Time to find the MONEY and see where our deals come from! 🎯")
    print()
    
    # Initialize service
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    service = RoofmaxxConnectService(config)
    
    print("🔗 Connecting to RoofMaxx Connect API...")
    if not service.authenticate():
        print("❌ Authentication failed!")
        return
    
    print("✅ Connected successfully!")
    print()
    
    # Find our dealer ID
    our_dealer_id = find_our_dealer_id(service)
    
    if not our_dealer_id:
        print("❌ Could not determine our dealer ID!")
        print("🔍 Let's try a different approach - checking general deals endpoint...")
        
        # Try general deals endpoint
        try:
            response = service._make_request('GET', '/api/v2/deals?per_page=10')
            deals_data = response.json()
            print(f"✅ Found general deals endpoint! Sample deals: {len(deals_data.get('data', []))}")
            
            if deals_data.get('data'):
                print("\n📋 SAMPLE DEALS STRUCTURE:")
                sample_deal = deals_data['data'][0]
                for key, value in sample_deal.items():
                    print(f"   {key}: {value}")
                print()
                
                return analyze_general_deals(service)
            
        except Exception as e:
            print(f"❌ General deals endpoint failed: {e}")
            print("\n🤷‍♂️ Unable to access deals data with this token.")
            print("💡 This token might be restricted to specific dealer operations.")
            return
    
    print(f"🎯 Our Dealer ID: {our_dealer_id}")
    
    # Get our dealer info
    our_dealer = service.get_dealer_by_id(our_dealer_id)
    if our_dealer:
        print(f"🏢 Our Business: {our_dealer.brand_name}")
        print(f"📍 Dealer Name: {our_dealer.name}")
        print(f"🌐 Website: {our_dealer.microsite_url}")
        print()
    
    # Get ALL our deals
    print("📥 Fetching ALL our deals...")
    all_deals = []
    page = 1
    
    while True:
        print(f"   📄 Fetching page {page}...")
        try:
            response = service.get_dealer_deals(our_dealer_id, page=page, per_page=100)
            deals_data = response.get('data', [])
            
            if not deals_data:
                break
                
            all_deals.extend(deals_data)
            page += 1
            
            # Safety break
            if page > 50:  # Max 5000 deals
                print("   ⚠️  Reached safety limit of 50 pages")
                break
                
        except Exception as e:
            print(f"   ❌ Error fetching page {page}: {e}")
            break
    
    print(f"✅ Retrieved {len(all_deals)} total deals!")
    print()
    
    if not all_deals:
        print("😅 No deals found! Either we're new or the API structure is different.")
        return
    
    # Analyze the first deal to understand structure
    print("🔍 DEAL DATA STRUCTURE:")
    sample_deal = all_deals[0]
    for key, value in sample_deal.items():
        print(f"   {key}: {value}")
    print()
    
    return analyze_deal_sources(all_deals)

def analyze_general_deals(service):
    """Analyze deals from general endpoint if available."""
    print("📊 ANALYZING GENERAL DEALS DATA")
    print("-" * 40)
    
    all_deals = []
    page = 1
    
    while page <= 5:  # Get first 5 pages for analysis
        try:
            response = service._make_request('GET', f'/api/v2/deals?page={page}&per_page=100')
            deals_data = response.json()
            
            if not deals_data.get('data'):
                break
                
            all_deals.extend(deals_data['data'])
            print(f"   📄 Page {page}: {len(deals_data['data'])} deals")
            page += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            break
    
    print(f"✅ Analyzed {len(all_deals)} deals from general endpoint")
    return analyze_deal_sources(all_deals)

def analyze_deal_sources(deals_list):
    """Analyze deals by source and provide business insights."""
    
    print("💰 DEALS BY SOURCE ANALYSIS")
    print("=" * 60)
    
    # Source analysis
    source_counter = Counter()
    source_values = defaultdict(float)
    source_details = defaultdict(list)
    
    # Status analysis
    status_counter = Counter()
    
    # Date analysis
    recent_deals = []
    
    total_value = 0
    
    for deal in deals_list:
        # Extract source information
        source = "Unknown"
        if 'source' in deal:
            source = deal['source'] or "Unknown"
        elif 'lead_source' in deal:
            source = deal['lead_source'] or "Unknown"
        elif 'referral_source' in deal:
            source = deal['referral_source'] or "Unknown"
        
        source_counter[source] += 1
        
        # Extract deal value
        value = 0
        if 'value' in deal:
            value = float(deal.get('value', 0) or 0)
        elif 'amount' in deal:
            value = float(deal.get('amount', 0) or 0)
        elif 'total' in deal:
            value = float(deal.get('total', 0) or 0)
        
        source_values[source] += value
        total_value += value
        
        # Extract status
        status = deal.get('status', 'Unknown')
        status_counter[status] += 1
        
        # Store deal details for source analysis
        source_details[source].append({
            'id': deal.get('id'),
            'value': value,
            'status': status,
            'created_at': deal.get('created_at'),
            'customer': deal.get('customer_name', deal.get('customer', 'Unknown'))
        })
        
        # Check if recent (last 90 days)
        if 'created_at' in deal and deal['created_at']:
            try:
                deal_date = datetime.fromisoformat(deal['created_at'].replace('Z', '+00:00'))
                if deal_date > datetime.now().replace(tzinfo=deal_date.tzinfo) - timedelta(days=90):
                    recent_deals.append(deal)
            except:
                pass
    
    # RESULTS
    print("📊 DEALS BY SOURCE BREAKDOWN:")
    print("-" * 40)
    
    for source, count in source_counter.most_common():
        avg_value = source_values[source] / count if count > 0 else 0
        total_source_value = source_values[source]
        percentage = (count / len(deals_list)) * 100
        
        print(f"🎯 {source}:")
        print(f"   📈 Count: {count} deals ({percentage:.1f}%)")
        print(f"   💰 Total Value: ${total_source_value:,.2f}")
        print(f"   📊 Avg Value: ${avg_value:,.2f}")
        print()
    
    print("💼 DEAL STATUS BREAKDOWN:")
    print("-" * 40)
    for status, count in status_counter.most_common():
        percentage = (count / len(deals_list)) * 100
        print(f"   {status}: {count} deals ({percentage:.1f}%)")
    print()
    
    print("📈 BUSINESS INSIGHTS:")
    print("-" * 40)
    print(f"💰 Total Portfolio Value: ${total_value:,.2f}")
    print(f"📊 Average Deal Value: ${total_value/len(deals_list):,.2f}")
    print(f"🔥 Recent Deals (90 days): {len(recent_deals)}")
    
    # Top performing source
    if source_values:
        top_value_source = max(source_values.keys(), key=lambda x: source_values[x])
        print(f"🏆 Highest Value Source: {top_value_source} (${source_values[top_value_source]:,.2f})")
    
    # Most frequent source
    if source_counter:
        top_volume_source = source_counter.most_common(1)[0][0]
        print(f"📈 Highest Volume Source: {top_volume_source} ({source_counter[top_volume_source]} deals)")
    
    print()
    
    print("🎯 ACTIONABLE RECOMMENDATIONS:")
    print("-" * 40)
    print("💡 Based on your deals data:")
    
    if source_counter:
        top_sources = source_counter.most_common(3)
        print(f"   1. Double down on: {', '.join([s[0] for s in top_sources])}")
        
        if len(source_counter) > 3:
            underperforming = [s for s, c in source_counter.items() if c < 3]
            if underperforming:
                print(f"   2. Investigate underperforming: {', '.join(underperforming[:3])}")
    
    print(f"   3. Recent activity: {len(recent_deals)} deals in last 90 days")
    print("   4. Focus on source optimization for highest ROI")
    print()
    
    return {
        'total_deals': len(deals_list),
        'total_value': total_value,
        'sources': dict(source_counter),
        'source_values': dict(source_values),
        'recent_deals': len(recent_deals),
        'top_source_by_volume': source_counter.most_common(1)[0] if source_counter else None,
        'top_source_by_value': max(source_values.items(), key=lambda x: x[1]) if source_values else None
    }

if __name__ == "__main__":
    print("🎯 LET'S FIND THE MONEY! 💰")
    print("=" * 60)
    
    insights = analyze_deals_by_source()
    
    print("\n🎉 ANALYSIS COMPLETE!")
    print("=" * 60)
    print("Now we're talking business! This is where the rubber meets the road! 🚀")
    
    if insights:
        print(f"\n📋 EXECUTIVE SUMMARY:")
        print(f"   💰 Total Value: ${insights.get('total_value', 0):,.2f}")
        print(f"   📊 Total Deals: {insights.get('total_deals', 0):,}")
        if insights.get('top_source_by_value'):
            top_source, top_value = insights['top_source_by_value']
            print(f"   🏆 Best Source: {top_source} (${top_value:,.2f})") 