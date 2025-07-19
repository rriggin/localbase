#!/usr/bin/env python3
"""
My RoofMaxx Dealership Analyzer

Find YOUR specific dealership and analyze YOUR business performance!
Let's get the real deal on YOUR deals! 💰
"""

import sys
import os
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.roofmaxxconnect.client import RoofmaxxConnectService
from src.services.roofmaxxconnect.models import DealerRecord

def find_my_dealership():
    """Find which specific dealer account this token belongs to."""
    
    print("🔍 FINDING YOUR DEALERSHIP")
    print("=" * 60)
    print("Let's identify YOUR specific dealer account and business! 🏢")
    print()
    
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    service = RoofmaxxConnectService(config)
    
    if not service.authenticate():
        print("❌ Authentication failed!")
        return None
    
    print("✅ Connected successfully!")
    print()
    
    # Strategy 1: Try profile/user endpoints without query params
    profile_endpoints = [
        "/api/v2/me",
        "/api/v2/profile", 
        "/api/v2/user",
        "/api/v2/account",
        "/api/v2/dealer/me",
        "/api/v2/my/profile",
        "/api/v2/current/dealer"
    ]
    
    print("🔍 Trying profile endpoints to identify your account...")
    for endpoint in profile_endpoints:
        try:
            print(f"   Testing: {endpoint}")
            response = service._make_request('GET', endpoint)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS! Found profile data at {endpoint}")
                print("   📋 Profile data:")
                for key, value in data.items():
                    print(f"      {key}: {value}")
                print()
                
                # Extract dealer ID if available
                dealer_id = None
                if 'dealer_id' in data:
                    dealer_id = data['dealer_id']
                elif 'id' in data:
                    dealer_id = data['id']
                elif isinstance(data, dict) and 'data' in data:
                    inner_data = data['data']
                    if isinstance(inner_data, dict):
                        dealer_id = inner_data.get('dealer_id') or inner_data.get('id')
                
                if dealer_id:
                    print(f"   🎯 Found your dealer ID: {dealer_id}")
                    return dealer_id
                    
        except Exception as e:
            print(f"   ❌ {endpoint}: {str(e)[:50]}...")
    
    print()
    
    # Strategy 2: Try to find accessible deals endpoints with different patterns
    print("🔍 Trying alternative deal access patterns...")
    deal_endpoints = [
        "/api/v2/my/deals",
        "/api/v2/dealer/deals", 
        "/api/v2/current/deals",
        "/api/v2/deals/mine",
        "/api/v2/my/leads",
        "/api/v2/my/customers",
        "/api/v2/my/sales"
    ]
    
    for endpoint in deal_endpoints:
        try:
            print(f"   Testing: {endpoint}")
            response = service._make_request('GET', endpoint + "?per_page=5")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ JACKPOT! Found your deals at {endpoint}")
                return analyze_my_deals(service, endpoint, data)
        except Exception as e:
            print(f"   ❌ {endpoint}: {str(e)[:50]}...")
    
    print()
    
    # Strategy 3: Smart dealer ID detection by testing deal access
    print("🔍 Smart detection: Testing dealer IDs for accessible deals...")
    
    # Get some recent dealers and test access
    dealers_response = service.get_dealers(page=1, per_page=20)
    recent_dealers = dealers_response.data
    
    for dealer in recent_dealers:
        # Skip obviously retired dealers
        if dealer.name and "RETIRED" in dealer.name.upper():
            continue
            
        try:
            print(f"   Testing access to dealer {dealer.id}: {dealer.brand_name}")
            response = service.get_dealer_deals(dealer.id, per_page=1)
            
            # If we get data back (not forbidden), this might be us!
            if response and 'data' in response:
                print(f"   🎯 SUCCESS! You might be dealer {dealer.id}")
                print(f"   🏢 Business: {dealer.brand_name}")
                print(f"   📍 Name: {dealer.name}")
                return analyze_my_dealership_details(service, dealer)
                
        except Exception as e:
            if "Forbidden" not in str(e):
                print(f"      ❌ Error: {str(e)[:30]}...")
            continue
    
    print("❌ Could not identify your specific dealer account with this token.")
    print("💡 This might be a read-only admin token for market intelligence.")
    return None

def analyze_my_dealership_details(service, dealer):
    """Analyze details for the identified dealership."""
    
    print("\n🏢 YOUR DEALERSHIP DETAILS")
    print("=" * 60)
    
    print(f"🎯 Your Business: {dealer.brand_name}")
    print(f"📋 Dealer Name: {dealer.name}")
    print(f"🆔 Dealer ID: {dealer.id}")
    print(f"🌐 Website: {dealer.microsite_url or 'Not set'}")
    print(f"⭐ Google Reviews: {'✅ Set up' if dealer.google_review_link else '❌ Not configured'}")
    print(f"🔗 HubSpot ID: {dealer.hubspot_company_id}")
    print()
    
    # Try to get your deals
    print("💰 YOUR DEALS ANALYSIS")
    print("-" * 40)
    
    try:
        deals_response = service.get_dealer_deals(dealer.id, per_page=100)
        deals = deals_response.get('data', [])
        
        if deals:
            print(f"📊 Total deals found: {len(deals)}")
            
            # Analyze deal structure
            sample_deal = deals[0]
            print("\n🔍 Deal data structure:")
            for key, value in sample_deal.items():
                print(f"   {key}: {value}")
            
            return analyze_deal_performance(deals, dealer)
        else:
            print("📭 No deals found in your account.")
            print("💡 This could mean:")
            print("   • You're a new dealer")
            print("   • Deals are stored elsewhere")
            print("   • Different API access level needed")
            
    except Exception as e:
        print(f"❌ Could not access your deals: {e}")
    
    return dealer

def analyze_my_deals(service, endpoint, initial_data):
    """Analyze deals data from the accessible endpoint."""
    
    print(f"\n💰 YOUR DEALS ANALYSIS (from {endpoint})")
    print("=" * 60)
    
    deals = initial_data.get('data', [])
    
    if not deals:
        print("📭 No deals found.")
        return None
    
    print(f"📊 Found {len(deals)} deals in initial response")
    
    # Get more deals if available
    all_deals = deals.copy()
    
    # Try to get more pages
    page = 2
    while page <= 10:  # Limit to prevent infinite loop
        try:
            response = service._make_request('GET', f"{endpoint}?page={page}&per_page=100")
            if response.status_code == 200:
                page_data = response.json()
                page_deals = page_data.get('data', [])
                if not page_deals:
                    break
                all_deals.extend(page_deals)
                print(f"   📄 Page {page}: {len(page_deals)} more deals")
                page += 1
            else:
                break
        except:
            break
    
    print(f"✅ Total deals retrieved: {len(all_deals)}")
    
    return analyze_deal_performance(all_deals, None)

def analyze_deal_performance(deals, dealer_info=None):
    """Analyze deal performance and provide business insights."""
    
    print("\n📈 YOUR BUSINESS PERFORMANCE")
    print("=" * 60)
    
    if not deals:
        print("No deals to analyze.")
        return
    
    # Basic stats
    total_deals = len(deals)
    print(f"📊 Total Deals: {total_deals}")
    
    # Analyze deal structure from first deal
    sample_deal = deals[0]
    print(f"\n🔍 Deal Fields Available:")
    for key in sample_deal.keys():
        print(f"   • {key}")
    
    # Revenue analysis (if value fields exist)
    revenue_fields = ['value', 'amount', 'total', 'price', 'revenue']
    total_revenue = 0
    deal_values = []
    
    for deal in deals:
        for field in revenue_fields:
            if field in deal and deal[field]:
                try:
                    value = float(deal[field])
                    deal_values.append(value)
                    total_revenue += value
                    break
                except:
                    continue
    
    if deal_values:
        avg_deal_value = total_revenue / len(deal_values)
        print(f"\n💰 REVENUE ANALYSIS:")
        print(f"   Total Revenue: ${total_revenue:,.2f}")
        print(f"   Average Deal Value: ${avg_deal_value:,.2f}")
        print(f"   Deals with $ values: {len(deal_values)}")
    
    # Status analysis
    status_field = None
    for field in ['status', 'stage', 'state']:
        if field in sample_deal:
            status_field = field
            break
    
    if status_field:
        statuses = {}
        for deal in deals:
            status = deal.get(status_field, 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"\n📋 DEAL STATUS BREAKDOWN:")
        for status, count in statuses.items():
            percentage = (count / total_deals) * 100
            print(f"   {status}: {count} deals ({percentage:.1f}%)")
    
    # Source analysis
    source_field = None
    for field in ['source', 'lead_source', 'referral_source', 'origin']:
        if field in sample_deal:
            source_field = field
            break
    
    if source_field:
        sources = {}
        for deal in deals:
            source = deal.get(source_field, 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\n🎯 DEAL SOURCES:")
        sorted_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)
        for source, count in sorted_sources:
            percentage = (count / total_deals) * 100
            print(f"   {source}: {count} deals ({percentage:.1f}%)")
    
    # Date analysis (if date fields exist)
    date_fields = ['created_at', 'date', 'timestamp', 'created']
    recent_deals = []
    
    for field in date_fields:
        if field in sample_deal:
            for deal in deals:
                date_str = deal.get(field)
                if date_str:
                    try:
                        deal_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        if deal_date > datetime.now().replace(tzinfo=deal_date.tzinfo) - timedelta(days=90):
                            recent_deals.append(deal)
                    except:
                        continue
            break
    
    if recent_deals:
        print(f"\n🔥 RECENT ACTIVITY (90 days):")
        print(f"   Recent Deals: {len(recent_deals)}")
        print(f"   Activity Rate: {len(recent_deals)/total_deals:.1%}")
    
    # Business recommendations
    print(f"\n🎯 BUSINESS INSIGHTS:")
    print(f"   📊 Total deal volume: {total_deals}")
    if deal_values:
        print(f"   💰 Revenue performance: ${avg_deal_value:,.0f} avg deal")
    if recent_deals:
        print(f"   🔥 Recent momentum: {len(recent_deals)} deals in 90 days")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if source_field and sources:
        top_source = max(sources.items(), key=lambda x: x[1])
        print(f"   • Focus on your top source: {top_source[0]}")
    if len(recent_deals) < total_deals * 0.3:
        print(f"   • Consider reactivation campaigns for lead generation")
    
    return {
        'total_deals': total_deals,
        'total_revenue': total_revenue,
        'recent_deals': len(recent_deals),
        'avg_deal_value': avg_deal_value if deal_values else 0
    }

if __name__ == "__main__":
    print("🏢 MY ROOFMAXX DEALERSHIP ANALYZER")
    print("=" * 60)
    print("Let's find YOUR business and analyze YOUR performance! 💼")
    print()
    
    result = find_my_dealership()
    
    if result:
        print("\n🎉 SUCCESS!")
        print("=" * 60)
        print("Found your dealership data! This is YOUR business intelligence! 🚀")
    else:
        print("\n🤔 ALTERNATIVE APPROACH NEEDED")
        print("=" * 60)
        print("This token might be for market intelligence rather than specific dealer access.")
        print("💡 We could help you get proper dealer-specific API access!") 