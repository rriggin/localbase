#!/usr/bin/env python3
"""
RoofMaxx Deals Analytics

Query and analyze your stored deals data from Supabase.
Business intelligence made permanent! 📊
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.supabase.client import SupabaseService

class DealsAnalytics:
    """Analytics service for stored RoofMaxx deals data."""
    
    def __init__(self, supabase_config: Dict[str, Any]):
        """Initialize with Supabase config."""
        self.supabase_service = SupabaseService(supabase_config)
        self.table_name = 'roofmaxx_deals'
        self.dealer_id = 6637
    
    def get_deals_by_source(self) -> Dict[str, Any]:
        """Get deals breakdown by source (deal_type)."""
        
        response = self.supabase_service.session.get(
            f"{self.supabase_service.url}/rest/v1/{self.table_name}",
            params={
                'select': 'deal_type,count(*)',
                'dealer_id': f'eq.{self.dealer_id}',
                'group_by': 'deal_type'
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch deals by source: {response.text}")
    
    def get_conversion_metrics(self) -> Dict[str, Any]:
        """Get conversion rate metrics."""
        
        # Get counts by lifecycle
        response = self.supabase_service.session.get(
            f"{self.supabase_service.url}/rest/v1/{self.table_name}",
            params={
                'select': 'deal_lifecycle,count(*)',
                'dealer_id': f'eq.{self.dealer_id}',
                'group_by': 'deal_lifecycle'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            total = sum(item['count'] for item in data)
            leads = next((item['count'] for item in data if item['deal_lifecycle'] == 'Lead'), 0)
            lost = next((item['count'] for item in data if item['deal_lifecycle'] == 'Lost'), 0)
            
            conversion_rate = (leads / (leads + lost) * 100) if (leads + lost) > 0 else 0
            
            return {
                'total_deals': total,
                'active_leads': leads,
                'lost_deals': lost,
                'conversion_rate': conversion_rate,
                'breakdown': data
            }
        else:
            raise Exception(f"Failed to fetch conversion metrics: {response.text}")
    
    def get_geographic_distribution(self) -> Dict[str, Any]:
        """Get deals by geographic location."""
        
        # Get by state
        state_response = self.supabase_service.session.get(
            f"{self.supabase_service.url}/rest/v1/{self.table_name}",
            params={
                'select': 'state,count(*)',
                'dealer_id': f'eq.{self.dealer_id}',
                'state': 'not.is.null',
                'group_by': 'state',
                'order': 'count.desc'
            }
        )
        
        # Get by city (top 10)
        city_response = self.supabase_service.session.get(
            f"{self.supabase_service.url}/rest/v1/{self.table_name}",
            params={
                'select': 'city,count(*)',
                'dealer_id': f'eq.{self.dealer_id}',
                'city': 'not.is.null',
                'group_by': 'city',
                'order': 'count.desc',
                'limit': '10'
            }
        )
        
        return {
            'by_state': state_response.json() if state_response.status_code == 200 else [],
            'top_cities': city_response.json() if city_response.status_code == 200 else []
        }
    
    def get_timeline_analytics(self) -> Dict[str, Any]:
        """Get deals over time analytics."""
        
        # Monthly trends
        monthly_response = self.supabase_service.session.get(
            f"{self.supabase_service.url}/rest/v1/{self.table_name}",
            params={
                'select': 'extract(year from create_date) as year,extract(month from create_date) as month,count(*)',
                'dealer_id': f'eq.{self.dealer_id}',
                'create_date': 'not.is.null',
                'group_by': 'year,month',
                'order': 'year,month'
            }
        )
        
        # Recent activity (last 90 days)
        ninety_days_ago = (datetime.now() - timedelta(days=90)).isoformat()
        recent_response = self.supabase_service.session.get(
            f"{self.supabase_service.url}/rest/v1/{self.table_name}",
            params={
                'select': 'count(*)',
                'dealer_id': f'eq.{self.dealer_id}',
                'create_date': f'gte.{ninety_days_ago}'
            },
            headers={'Prefer': 'count=exact'}
        )
        
        recent_count = 0
        if recent_response.status_code == 200:
            count_header = recent_response.headers.get('Content-Range', '0-0/0')
            recent_count = int(count_header.split('/')[-1])
        
        return {
            'monthly_trends': monthly_response.json() if monthly_response.status_code == 200 else [],
            'recent_activity_90_days': recent_count
        }
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Get complete business summary dashboard."""
        
        print("📊 GENERATING BUSINESS SUMMARY FROM SUPABASE")
        print("=" * 60)
        
        # Get all analytics
        deals_by_source = self.get_deals_by_source()
        conversion_metrics = self.get_conversion_metrics()
        geographic_data = self.get_geographic_distribution()
        timeline_data = self.get_timeline_analytics()
        
        # Format for display
        print("🎯 DEALS BY SOURCE:")
        for item in sorted(deals_by_source, key=lambda x: x['count'], reverse=True):
            print(f"   {item['deal_type']}: {item['count']:,} deals")
        
        print(f"\n🏆 CONVERSION METRICS:")
        print(f"   Total Deals: {conversion_metrics['total_deals']:,}")
        print(f"   Active Leads: {conversion_metrics['active_leads']:,}")
        print(f"   Lost Deals: {conversion_metrics['lost_deals']:,}")
        print(f"   Conversion Rate: {conversion_metrics['conversion_rate']:.1f}%")
        
        print(f"\n🗺️  GEOGRAPHIC DISTRIBUTION:")
        print("   Top States:")
        for item in geographic_data['by_state'][:5]:
            print(f"   {item['state']}: {item['count']:,} deals")
        
        print("   Top Cities:")
        for item in geographic_data['top_cities'][:5]:
            print(f"   {item['city']}: {item['count']:,} deals")
        
        print(f"\n📅 TIMELINE INSIGHTS:")
        print(f"   Recent Activity (90 days): {timeline_data['recent_activity_90_days']:,} deals")
        
        if timeline_data['monthly_trends']:
            latest_month = timeline_data['monthly_trends'][-1]
            print(f"   Latest Month: {latest_month['year']}-{latest_month['month']:02d} with {latest_month['count']} deals")
        
        print("\n✅ All data successfully retrieved from Supabase!")
        print("🎯 Ready for dashboards, reporting, and advanced analytics!")
        
        return {
            'deals_by_source': deals_by_source,
            'conversion_metrics': conversion_metrics,
            'geographic_data': geographic_data,
            'timeline_data': timeline_data,
            'generated_at': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # You'll need to provide your Supabase config
    supabase_config = {
        'url': 'YOUR_SUPABASE_URL',
        'access_token': 'YOUR_SUPABASE_ACCESS_TOKEN'
    }
    
    print("⚠️  PLEASE UPDATE SUPABASE CONFIG BEFORE RUNNING!")
    print("Update the supabase_config dictionary with your actual Supabase credentials")
    print()
    
    # Uncomment when config is ready:
    # analytics = DealsAnalytics(supabase_config)
    # summary = analytics.get_business_summary() 