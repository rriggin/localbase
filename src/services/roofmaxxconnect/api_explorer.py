#!/usr/bin/env python3
"""
RoofMaxx Connect API Explorer

Let's find out what we CAN access and discover hidden business value!
Sometimes the real gold is in unexpected places! 💎
"""

import sys
import os
from typing import Dict, Any, List
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.roofmaxxconnect.client import RoofmaxxConnectService

def comprehensive_api_exploration():
    """Comprehensive exploration of what endpoints are actually available."""
    
    print("🔍 RoofMaxx Connect API Deep Dive")
    print("=" * 60)
    print("Let's find out what we CAN access and discover hidden business value! 💎")
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
    
    # Test common API endpoints
    endpoints_to_test = [
        # Dealer related
        "/api/v2/dealers",
        "/api/v2/dealers/17",
        "/api/v2/dealers/1",
        
        # Deal related attempts
        "/api/v2/deals", 
        "/api/v2/deals/1",
        "/api/v2/leads",
        "/api/v2/opportunities", 
        "/api/v2/sales",
        "/api/v2/quotes",
        "/api/v2/estimates",
        
        # User/Profile related
        "/api/v2/me",
        "/api/v2/user",
        "/api/v2/profile",
        "/api/v2/account",
        
        # System info
        "/api/v2/stats",
        "/api/v2/analytics",
        "/api/v2/dashboard",
        "/api/v2/reports",
        "/api/v2/metrics",
        
        # Configuration
        "/api/v2/config",
        "/api/v2/settings",
        "/api/v2/preferences",
        
        # Business entities
        "/api/v2/customers",
        "/api/v2/contacts",
        "/api/v2/companies",
        "/api/v2/territories",
        "/api/v2/regions",
        "/api/v2/markets",
        
        # Product/Service related
        "/api/v2/services",
        "/api/v2/products",
        "/api/v2/treatments",
        "/api/v2/inspections",
        "/api/v2/appointments",
        
        # Marketing
        "/api/v2/campaigns",
        "/api/v2/leads",
        "/api/v2/referrals",
        
        # Other versions
        "/api/v1/dealers",
        "/api/v3/dealers",
        "/api/dealers",
        
        # Documentation
        "/api/docs",
        "/api/v2/docs",
        "/api/swagger",
        "/api/openapi"
    ]
    
    accessible_endpoints = []
    forbidden_endpoints = []
    not_found_endpoints = []
    error_endpoints = []
    
    print("🌐 ENDPOINT DISCOVERY:")
    print("-" * 40)
    
    for endpoint in endpoints_to_test:
        try:
            print(f"   Testing: {endpoint}")
            response = service._make_request('GET', endpoint + "?per_page=1")
            
            if response.status_code == 200:
                accessible_endpoints.append({
                    'endpoint': endpoint,
                    'status': 200,
                    'data': response.json()
                })
                print(f"   ✅ {endpoint} - ACCESSIBLE!")
                
            elif response.status_code == 403:
                forbidden_endpoints.append(endpoint)
                print(f"   🚫 {endpoint} - FORBIDDEN")
                
            elif response.status_code == 404:
                not_found_endpoints.append(endpoint)
                print(f"   ❌ {endpoint} - NOT FOUND")
                
            else:
                error_endpoints.append({
                    'endpoint': endpoint,
                    'status': response.status_code,
                    'response': response.text[:200]
                })
                print(f"   ⚠️  {endpoint} - ERROR {response.status_code}")
                
        except Exception as e:
            error_endpoints.append({
                'endpoint': endpoint,
                'error': str(e)
            })
            print(f"   💥 {endpoint} - EXCEPTION: {str(e)[:50]}...")
    
    print("\n📊 DISCOVERY RESULTS:")
    print("=" * 60)
    
    print(f"✅ ACCESSIBLE ENDPOINTS ({len(accessible_endpoints)}):")
    for item in accessible_endpoints:
        endpoint = item['endpoint']
        data = item['data']
        print(f"   🟢 {endpoint}")
        
        # Show sample data structure
        if isinstance(data, dict):
            if 'data' in data:
                sample_count = len(data['data']) if isinstance(data['data'], list) else 1
                print(f"      📊 Contains {sample_count} records")
                
            if 'meta' in data:
                meta = data['meta']
                if 'total' in meta:
                    print(f"      📈 Total available: {meta['total']:,}")
            
            # Show first few keys
            keys = list(data.keys())[:5]
            print(f"      🔑 Keys: {', '.join(keys)}")
        print()
    
    print(f"🚫 FORBIDDEN ENDPOINTS ({len(forbidden_endpoints)}):")
    for endpoint in forbidden_endpoints[:5]:  # Show first 5
        print(f"   🔴 {endpoint}")
    if len(forbidden_endpoints) > 5:
        print(f"   ... and {len(forbidden_endpoints) - 5} more")
    print()
    
    print(f"❌ NOT FOUND ENDPOINTS ({len(not_found_endpoints)}):")
    for endpoint in not_found_endpoints[:5]:  # Show first 5
        print(f"   ⚪ {endpoint}")
    if len(not_found_endpoints) > 5:
        print(f"   ... and {len(not_found_endpoints) - 5} more")
    print()
    
    # Deep dive into accessible endpoints
    if accessible_endpoints:
        print("🔬 DEEP DIVE INTO ACCESSIBLE DATA:")
        print("=" * 60)
        
        for item in accessible_endpoints:
            endpoint = item['endpoint']
            data = item['data']
            
            print(f"📋 ANALYZING: {endpoint}")
            print("-" * 40)
            
            if isinstance(data, dict) and 'data' in data:
                records = data['data']
                if records and isinstance(records, list):
                    sample_record = records[0]
                    print("🔍 Sample record structure:")
                    for key, value in sample_record.items():
                        value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"   {key}: {value_preview}")
                    print()
                    
                    # Look for business-relevant fields
                    business_fields = []
                    for key in sample_record.keys():
                        if any(term in key.lower() for term in [
                            'revenue', 'sales', 'deal', 'lead', 'customer', 
                            'contact', 'phone', 'email', 'address', 'value',
                            'amount', 'price', 'cost', 'profit', 'commission',
                            'status', 'stage', 'source', 'campaign', 'referral'
                        ]):
                            business_fields.append(key)
                    
                    if business_fields:
                        print(f"💼 Business-relevant fields found: {', '.join(business_fields)}")
                        print()
    
    # Alternative approaches
    print("🚀 ALTERNATIVE APPROACHES:")
    print("=" * 60)
    
    print("💡 Since direct deals access is restricted, let's try:")
    print("   1. Analyze dealer data for business patterns")
    print("   2. Look for indirect business indicators")  
    print("   3. Extract competitive intelligence")
    print("   4. Find geographic/market opportunities")
    print()
    
    return {
        'accessible': accessible_endpoints,
        'forbidden': forbidden_endpoints,
        'not_found': not_found_endpoints,
        'errors': error_endpoints
    }

def extract_business_intelligence():
    """Extract business intelligence from available data."""
    
    print("🧠 BUSINESS INTELLIGENCE EXTRACTION")
    print("=" * 60)
    print("Let's mine business gold from the data we CAN access! ⛏️💰")
    print()
    
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    service = RoofmaxxConnectService(config)
    
    # Get comprehensive dealer data
    print("📊 Gathering comprehensive dealer intelligence...")
    all_dealers = []
    
    # Get more pages for better analysis
    for page in range(1, 11):  # 1000 dealers
        print(f"   📄 Page {page}...")
        dealers_response = service.get_dealers(page=page, per_page=100)
        all_dealers.extend(dealers_response.data)
        
        if page == 1:
            total_available = dealers_response.meta.total
            print(f"   📊 Total dealers in system: {total_available:,}")
    
    print(f"✅ Analyzed {len(all_dealers)} dealers")
    print()
    
    # BUSINESS INTELLIGENCE ANALYSIS
    
    # 1. Market Saturation by State
    print("1️⃣ MARKET SATURATION ANALYSIS")
    print("-" * 40)
    
    state_analysis = {}
    for dealer in all_dealers:
        if dealer.brand_name:
            words = dealer.brand_name.split()
            for word in words:
                if len(word) == 2 and word.isupper():
                    state = word
                    if state not in state_analysis:
                        state_analysis[state] = {'total': 0, 'active': 0, 'retired': 0, 'with_websites': 0}
                    
                    state_analysis[state]['total'] += 1
                    
                    if not (dealer.name and "RETIRED" in dealer.name.upper()):
                        state_analysis[state]['active'] += 1
                    else:
                        state_analysis[state]['retired'] += 1
                        
                    if dealer.microsite_url:
                        state_analysis[state]['with_websites'] += 1
    
    # Top opportunity states
    opportunity_states = []
    for state, data in state_analysis.items():
        if data['total'] >= 5:  # Significant presence
            active_rate = data['active'] / data['total']
            website_rate = data['with_websites'] / data['total']
            opportunity_score = (active_rate * 0.6) + (website_rate * 0.4)
            
            opportunity_states.append({
                'state': state,
                'total_dealers': data['total'],
                'active_rate': active_rate,
                'website_rate': website_rate,
                'opportunity_score': opportunity_score
            })
    
    opportunity_states.sort(key=lambda x: x['opportunity_score'], reverse=True)
    
    print("🎯 TOP OPPORTUNITY MARKETS:")
    for state_data in opportunity_states[:10]:
        state = state_data['state']
        print(f"   {state}: {state_data['total_dealers']} dealers")
        print(f"      🟢 Active Rate: {state_data['active_rate']:.1%}")
        print(f"      🌐 Website Rate: {state_data['website_rate']:.1%}")
        print(f"      ⭐ Opportunity Score: {state_data['opportunity_score']:.2f}")
        print()
    
    # 2. Competitive Analysis
    print("2️⃣ COMPETITIVE LANDSCAPE")
    print("-" * 40)
    
    # Find patterns in dealer names/brands
    brand_patterns = {}
    for dealer in all_dealers:
        if dealer.brand_name and dealer.name and "RETIRED" not in dealer.name.upper():
            # Extract business model patterns
            if "Roof Maxx of" in dealer.brand_name:
                territory = dealer.brand_name.replace("Roof Maxx of ", "").strip()
                brand_patterns[territory] = brand_patterns.get(territory, 0) + 1
    
    print("🏢 ACTIVE TERRITORY DISTRIBUTION:")
    sorted_territories = sorted(brand_patterns.items(), key=lambda x: x[1], reverse=True)
    for territory, count in sorted_territories[:15]:
        print(f"   {territory}: {count} active dealer{'s' if count > 1 else ''}")
    print()
    
    # 3. Digital Presence Gap Analysis
    print("3️⃣ DIGITAL PRESENCE OPPORTUNITIES")
    print("-" * 40)
    
    active_dealers = [d for d in all_dealers if not (d.name and "RETIRED" in d.name.upper())]
    no_website = [d for d in active_dealers if not d.microsite_url]
    no_reviews = [d for d in active_dealers if not d.google_review_link]
    
    print(f"💰 REVENUE OPPORTUNITIES:")
    print(f"   🌐 {len(no_website)} active dealers need websites")
    print(f"   ⭐ {len(no_reviews)} active dealers need review setup")
    print(f"   💼 Potential website revenue: ${len(no_website) * 2000:,} (est. $2k/site)")
    print(f"   📈 Potential review setup: ${len(no_reviews) * 500:,} (est. $500/setup)")
    print()
    
    # 4. Geographic Expansion Analysis
    print("4️⃣ EXPANSION OPPORTUNITIES")
    print("-" * 40)
    
    expansion_targets = []
    for state, data in state_analysis.items():
        if data['total'] < 10 and data['active'] >= 2:  # Underserved but viable
            expansion_targets.append({
                'state': state,
                'current_dealers': data['total'],
                'active_dealers': data['active'],
                'potential': min(20 - data['total'], 10)  # Room for growth
            })
    
    expansion_targets.sort(key=lambda x: x['potential'], reverse=True)
    
    print("🎯 EXPANSION TARGET STATES:")
    for target in expansion_targets[:10]:
        print(f"   {target['state']}: {target['current_dealers']} total, {target['active_dealers']} active")
        print(f"      🚀 Expansion potential: {target['potential']} new dealers")
    print()
    
    return {
        'total_dealers_analyzed': len(all_dealers),
        'market_opportunities': opportunity_states[:5],
        'expansion_targets': expansion_targets[:5],
        'website_revenue_potential': len(no_website) * 2000,
        'review_revenue_potential': len(no_reviews) * 500
    }

if __name__ == "__main__":
    print("🔍 API EXPLORATION & BUSINESS INTELLIGENCE")
    print("=" * 60)
    
    # Discover available endpoints
    discovery_results = comprehensive_api_exploration()
    
    print("\n" + "=" * 60)
    
    # Extract business intelligence
    business_insights = extract_business_intelligence()
    
    print("\n🎯 EXECUTIVE SUMMARY FOR TOM")
    print("=" * 60)
    
    if business_insights:
        print("💼 BUSINESS OPPORTUNITIES DISCOVERED:")
        print(f"   📊 Analyzed: {business_insights['total_dealers_analyzed']:,} dealers")
        print(f"   💰 Website Revenue Potential: ${business_insights['website_revenue_potential']:,}")
        print(f"   ⭐ Review Setup Revenue: ${business_insights['review_revenue_potential']:,}")
        print(f"   🎯 Market Opportunities: {len(business_insights['market_opportunities'])} states")
        print(f"   🚀 Expansion Targets: {len(business_insights['expansion_targets'])} states")
        print()
        print("🔥 THIS IS ACTIONABLE BUSINESS INTELLIGENCE!")
        print("Even without direct deals access, we found GOLD! 💎") 