#!/usr/bin/env python3
"""
RoofMaxx Connect Data Explorer

Interactive exploration of the RoofMaxx Connect dealer data.
Let's see what insights we can find!
"""

import sys
import os
from collections import Counter, defaultdict
from typing import Dict, Any, List
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.roofmaxxconnect.client import RoofmaxxConnectService
from src.services.roofmaxxconnect.models import DealerRecord

def explore_roofmaxx_data():
    """Explore and analyze the RoofMaxx Connect dealer data."""
    
    print("🕵️ RoofMaxx Connect Data Explorer")
    print("=" * 60)
    print("Let's dig into that dealer data and see what we can find!")
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
    
    # Get a sample of dealers to analyze
    print("📥 Fetching dealer data for analysis...")
    all_dealers = []
    
    # Fetch first few pages to get a good sample
    for page in range(1, 6):  # First 5 pages = 500 dealers
        print(f"   Fetching page {page}...")
        dealers_response = service.get_dealers(page=page, per_page=100)
        all_dealers.extend(dealers_response.data)
        
        if page == 1:
            total_available = dealers_response.meta.total
            print(f"   📊 Total dealers available: {total_available:,}")
    
    print(f"✅ Retrieved {len(all_dealers)} dealers for analysis")
    print()
    
    # ANALYSIS 1: Active vs Retired Dealers
    print("1️⃣ ACTIVE vs RETIRED ANALYSIS")
    print("-" * 40)
    
    active_dealers = []
    retired_dealers = []
    
    for dealer in all_dealers:
        if dealer.name and "RETIRED" in dealer.name.upper():
            retired_dealers.append(dealer)
        else:
            active_dealers.append(dealer)
    
    print(f"🟢 Active Dealers: {len(active_dealers)} ({len(active_dealers)/len(all_dealers)*100:.1f}%)")
    print(f"🔴 Retired Dealers: {len(retired_dealers)} ({len(retired_dealers)/len(all_dealers)*100:.1f}%)")
    print()
    
    # ANALYSIS 2: Geographic Distribution
    print("2️⃣ GEOGRAPHIC DISTRIBUTION")
    print("-" * 40)
    
    # Extract states from brand names
    state_counter = Counter()
    
    for dealer in all_dealers:
        if dealer.brand_name:
            # Look for state abbreviations (2 letters at the end)
            words = dealer.brand_name.split()
            for word in words:
                # Common state patterns
                if len(word) == 2 and word.isupper():
                    state_counter[word] += 1
                elif word.upper() in ['FLORIDA', 'CALIFORNIA', 'TEXAS', 'GEORGIA']:
                    state_counter[word.upper()[:2]] += 1
    
    print("🗺️  Top 10 States by Dealer Count:")
    for state, count in state_counter.most_common(10):
        print(f"   {state}: {count} dealers")
    print()
    
    # ANALYSIS 3: HubSpot Integration
    print("3️⃣ HUBSPOT INTEGRATION ANALYSIS")
    print("-" * 40)
    
    hubspot_integrated = [d for d in all_dealers if d.hubspot_company_id]
    hubspot_missing = [d for d in all_dealers if not d.hubspot_company_id]
    
    print(f"🔗 HubSpot Integrated: {len(hubspot_integrated)} dealers")
    print(f"❌ No HubSpot ID: {len(hubspot_missing)} dealers")
    print(f"📊 Integration Rate: {len(hubspot_integrated)/len(all_dealers)*100:.1f}%")
    print()
    
    # ANALYSIS 4: Website/Microsite Coverage
    print("4️⃣ ONLINE PRESENCE ANALYSIS")
    print("-" * 40)
    
    has_microsite = [d for d in all_dealers if d.microsite_url]
    no_microsite = [d for d in all_dealers if not d.microsite_url]
    
    print(f"🌐 Has Microsite: {len(has_microsite)} dealers")
    print(f"❌ No Microsite: {len(no_microsite)} dealers")
    print(f"📊 Website Coverage: {len(has_microsite)/len(all_dealers)*100:.1f}%")
    print()
    
    # ANALYSIS 5: Sample Active Dealers by Region
    print("5️⃣ SAMPLE ACTIVE DEALERS")
    print("-" * 40)
    
    print("🟢 Active Dealers with Full Online Presence:")
    active_with_sites = [d for d in active_dealers if d.microsite_url and d.google_review_link]
    
    for i, dealer in enumerate(active_with_sites[:5], 1):
        print(f"   {i}. {dealer.brand_name}")
        print(f"      🌐 {dealer.microsite_url}")
        print(f"      ⭐ Google Reviews Available")
        print(f"      🔗 HubSpot ID: {dealer.hubspot_company_id}")
        print()
    
    # ANALYSIS 6: Data Quality Assessment
    print("6️⃣ DATA QUALITY ASSESSMENT")
    print("-" * 40)
    
    complete_profiles = []
    incomplete_profiles = []
    
    for dealer in all_dealers:
        score = 0
        if dealer.name: score += 1
        if dealer.brand_name: score += 1
        if dealer.hubspot_company_id: score += 1
        if dealer.microsite_url: score += 1
        if dealer.google_review_link: score += 1
        
        if score >= 4:
            complete_profiles.append(dealer)
        else:
            incomplete_profiles.append(dealer)
    
    print(f"✅ Complete Profiles (4-5 fields): {len(complete_profiles)} dealers")
    print(f"⚠️  Incomplete Profiles (<4 fields): {len(incomplete_profiles)} dealers")
    print(f"📊 Data Completeness: {len(complete_profiles)/len(all_dealers)*100:.1f}%")
    print()
    
    # ANALYSIS 7: Business Insights
    print("7️⃣ BUSINESS INSIGHTS")
    print("-" * 40)
    
    # Active dealers with strong online presence
    strong_online_presence = [
        d for d in active_dealers 
        if d.microsite_url and d.google_review_link and d.hubspot_company_id
    ]
    
    print(f"🚀 Active dealers with strong online presence: {len(strong_online_presence)}")
    print(f"💼 Potential high-performing dealers: {len(strong_online_presence)}")
    
    # Retired dealers - potential reactivation targets
    recently_retired = [d for d in retired_dealers if "2024" in (d.name or "")]
    print(f"🔄 Recently retired dealers (potential reactivation): {len(recently_retired)}")
    
    # Geographic expansion opportunities
    underrepresented_states = [state for state, count in state_counter.items() if count < 3]
    print(f"🎯 States with <3 dealers (expansion opportunities): {len(underrepresented_states)}")
    print()
    
    # ANALYSIS 8: Actionable Recommendations
    print("8️⃣ ACTIONABLE RECOMMENDATIONS")
    print("-" * 40)
    
    print("📋 Based on the data analysis:")
    print()
    print("🎯 PRIORITY ACTIONS:")
    print(f"   1. Reactivate {len(recently_retired)} recently retired dealers")
    print(f"   2. Complete profiles for {len(incomplete_profiles)} dealers missing data")
    print(f"   3. Add microsites for {len(no_microsite)} dealers without websites")
    print(f"   4. Integrate {len(hubspot_missing)} dealers with HubSpot")
    print()
    
    print("🌍 EXPANSION OPPORTUNITIES:")
    if underrepresented_states:
        print(f"   • Target {underrepresented_states[:5]} for dealer recruitment")
    print(f"   • Focus on states with highest activity: {[s for s, c in state_counter.most_common(3)]}")
    print()
    
    print("💡 SUCCESS PATTERNS:")
    print(f"   • {len(strong_online_presence)} dealers have complete digital presence")
    print(f"   • Active dealers: {len(active_dealers)/len(all_dealers)*100:.1f}% of total")
    print(f"   • Online presence correlates with active status")
    print()
    
    return {
        "total_dealers": len(all_dealers),
        "active_dealers": len(active_dealers),
        "retired_dealers": len(retired_dealers),
        "top_states": state_counter.most_common(5),
        "hubspot_integration_rate": len(hubspot_integrated)/len(all_dealers),
        "website_coverage": len(has_microsite)/len(all_dealers),
        "strong_online_presence": len(strong_online_presence),
        "data_completeness": len(complete_profiles)/len(all_dealers)
    }

def quick_queries():
    """Run some quick targeted queries."""
    
    print("\n" + "=" * 60)
    print("🔍 QUICK TARGETED QUERIES")
    print("=" * 60)
    
    config = {
        'bearer_token': 'aBhYri6MDq4hE4yrKH55nVRMTICVtdpF4zbZDsXd',
        'base_url': 'https://roofmaxxconnect.com'
    }
    
    service = RoofmaxxConnectService(config)
    
    # Query 1: Find specific dealer by ID
    print("1️⃣ Looking up specific dealer (ID: 17 - Mills Roofing)...")
    dealer_17 = service.get_dealer_by_id(17)
    if dealer_17:
        print(f"   ✅ Found: {dealer_17.brand_name}")
        print(f"   🏢 Name: {dealer_17.name}")
        print(f"   🌐 Website: {dealer_17.microsite_url}")
    print()
    
    # Query 2: Get API statistics
    print("2️⃣ API Statistics...")
    stats = service.get_api_stats()
    print(f"   📊 Total dealers in system: {stats.get('total_dealers', 'Unknown'):,}")
    print(f"   📄 Total pages: {stats.get('total_pages', 'Unknown')}")
    print(f"   ⚡ Per page: {stats.get('dealers_per_page', 'Unknown')}")
    print()
    
    # Query 3: Last page peek
    print("3️⃣ Checking the last page of dealers...")
    last_page_response = service.get_dealers(page=stats.get('total_pages', 49), per_page=10)
    print(f"   📋 Last page has {len(last_page_response.data)} dealers")
    if last_page_response.data:
        last_dealer = last_page_response.data[-1]
        print(f"   🏁 Last dealer: {last_dealer.brand_name} (ID: {last_dealer.id})")
    print()

if __name__ == "__main__":
    # Run the full exploration
    insights = explore_roofmaxx_data()
    
    # Run quick queries
    quick_queries()
    
    print("🎯 EXPLORATION COMPLETE!")
    print("=" * 60)
    print("Ready to dive deeper into any specific area that caught your interest! 🚀") 