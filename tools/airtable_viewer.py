#!/usr/bin/env python3
"""
Airtable Data Viewer Tool
Professional CLI tool for viewing and exporting Airtable data using the new service architecture.
"""

import sys
import os
import json
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add parent directory to path for src imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.services.airtable import AirtableService, AirtableQuery
from src.services.base_service import ServiceError

class AirtableViewerTool:
    """Professional Airtable viewer tool using service architecture."""
    
    def __init__(self):
        try:
            self.airtable = config.get_service("airtable")
            print("✅ Connected to Airtable")
        except Exception as e:
            print(f"❌ Failed to connect to Airtable: {e}")
            sys.exit(1)
    
    def run_interactive_menu(self):
        """Run the interactive menu system."""
        while True:
            self._display_menu()
            
            try:
                choice = input("\nSelect option (0-8): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self._view_all_records()
                elif choice == "2":
                    self._export_all_records()
                elif choice == "3":
                    self._search_records()
                elif choice == "4":
                    self._view_recent_records()
                elif choice == "5":
                    self._export_recent_records()
                elif choice == "6":
                    self._view_business_breakdown()
                elif choice == "7":
                    self._quick_peek()
                elif choice == "8":
                    self._service_health_check()
                else:
                    print("❌ Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
            input("\nPress Enter to continue...")
    
    def _display_menu(self):
        """Display the main menu."""
        print("\n" + "="*50)
        print("🎯 AIRTABLE VIEWER - Professional Edition")
        print("="*50)
        print("1. View all records summary")
        print("2. Export all records to CSV")
        print("3. Search records")
        print("4. View recent records (last 7 days)")
        print("5. Export recent records to CSV")
        print("6. View business breakdown")
        print("7. Quick peek (first 10 records)")
        print("8. Service health check")
        print("0. Exit")
    
    def _view_all_records(self):
        """View summary of all records."""
        try:
            print("📊 Loading all records...")
            records = self.airtable.get_records()
            
            print(f"\n✅ Total Records: {len(records)}")
            
            if records:
                # Show sample data
                sample_record = records[0]
                print(f"\n📋 Sample Record Fields:")
                for field_name, field_value in sample_record.fields.items():
                    value_preview = str(field_value)[:50] + "..." if len(str(field_value)) > 50 else str(field_value)
                    print(f"  • {field_name}: {value_preview}")
                
                # Business breakdown
                self._show_business_summary(records)
                
        except ServiceError as e:
            print(f"❌ Service Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
    
    def _export_all_records(self):
        """Export all records to CSV."""
        try:
            print("📤 Exporting all records...")
            records = self.airtable.get_records()
            
            # Convert to DataFrame
            df = self._records_to_dataframe(records)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/airtable_export_{timestamp}.csv"
            
            df.to_csv(filename, index=False)
            print(f"✅ Exported {len(records)} records to {filename}")
            
        except ServiceError as e:
            print(f"❌ Service Error: {e}")
        except Exception as e:
            print(f"❌ Export Error: {e}")
    
    def _search_records(self):
        """Search for specific records."""
        search_term = input("🔍 Enter search term: ").strip()
        
        if not search_term:
            print("❌ Search term cannot be empty")
            return
        
        try:
            print(f"🔍 Searching for '{search_term}'...")
            records = self.airtable.search_records(search_term)
            
            if records:
                print(f"\n✅ Found {len(records)} matching records:")
                for i, record in enumerate(records[:10], 1):  # Show first 10
                    name = record.get_field("Name", "Unknown")
                    business = record.get_field("Business", "Unknown")
                    print(f"  {i}. {name} (Business: {business})")
                
                if len(records) > 10:
                    print(f"  ... and {len(records) - 10} more records")
            else:
                print("❌ No records found matching your search")
                
        except ServiceError as e:
            print(f"❌ Service Error: {e}")
        except Exception as e:
            print(f"❌ Search Error: {e}")
    
    def _view_recent_records(self):
        """View records from the last 7 days."""
        try:
            # Calculate date 7 days ago
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            # Create query for recent records
            query = AirtableQuery(
                filter_formula=f"IS_AFTER({{Created}}, '{week_ago}')",
                sort=[{"field": "Created", "direction": "desc"}]
            )
            
            print("📅 Loading recent records (last 7 days)...")
            records = self.airtable.get_records(query=query)
            
            if records:
                print(f"\n✅ Recent Records: {len(records)}")
                for record in records[:10]:  # Show first 10
                    name = record.get_field("Name", "Unknown")
                    business = record.get_field("Business", "Unknown")
                    created = record.get_field("Created", "Unknown")
                    print(f"  • {name} (Business: {business}, Created: {created})")
            else:
                print("❌ No recent records found")
                
        except ServiceError as e:
            print(f"❌ Service Error: {e}")
        except Exception as e:
            print(f"❌ Recent Records Error: {e}")
    
    def _export_recent_records(self):
        """Export recent records to CSV."""
        try:
            # Calculate date 7 days ago
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            # Create query for recent records
            query = AirtableQuery(
                filter_formula=f"IS_AFTER({{Created}}, '{week_ago}')",
                sort=[{"field": "Created", "direction": "desc"}]
            )
            
            print("📤 Exporting recent records...")
            records = self.airtable.get_records(query=query)
            
            if records:
                # Convert to DataFrame
                df = self._records_to_dataframe(records)
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/airtable_recent_{timestamp}.csv"
                
                df.to_csv(filename, index=False)
                print(f"✅ Exported {len(records)} recent records to {filename}")
            else:
                print("❌ No recent records to export")
                
        except ServiceError as e:
            print(f"❌ Service Error: {e}")
        except Exception as e:
            print(f"❌ Export Error: {e}")
    
    def _view_business_breakdown(self):
        """View breakdown by business."""
        try:
            print("🏢 Loading business breakdown...")
            records = self.airtable.get_records()
            
            # Group by business
            business_counts = {}
            for record in records:
                business = record.get_field("Business", "Unknown")
                business_counts[business] = business_counts.get(business, 0) + 1
            
            print(f"\n📊 Business Breakdown ({len(records)} total records):")
            for business, count in sorted(business_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(records)) * 100
                print(f"  • {business}: {count} records ({percentage:.1f}%)")
                
        except ServiceError as e:
            print(f"❌ Service Error: {e}")
        except Exception as e:
            print(f"❌ Business Breakdown Error: {e}")
    
    def _quick_peek(self):
        """Show first 10 records for quick overview."""
        try:
            print("👀 Quick peek at first 10 records...")
            query = AirtableQuery(max_records=10)
            records = self.airtable.get_records(query=query)
            
            if records:
                print(f"\n📋 Showing {len(records)} records:")
                for i, record in enumerate(records, 1):
                    name = record.get_field("Name", "No Name")
                    business = record.get_field("Business", "No Business")
                    phone = record.get_field("Phone", "No Phone")
                    print(f"  {i:2d}. {name} | {business} | {phone}")
            else:
                print("❌ No records found")
                
        except ServiceError as e:
            print(f"❌ Service Error: {e}")
        except Exception as e:
            print(f"❌ Quick Peek Error: {e}")
    
    def _service_health_check(self):
        """Check service health and status."""
        try:
            print("🔍 Checking service health...")
            
            # Check Airtable service health
            health = self.airtable.health_check()
            
            print(f"\n📊 Airtable Service Status:")
            print(f"  • Status: {health.get('status', 'unknown')}")
            print(f"  • Authenticated: {health.get('authenticated', 'unknown')}")
            print(f"  • Base ID: {health.get('base_id', 'unknown')}")
            print(f"  • Table: {health.get('default_table', 'unknown')}")
            print(f"  • Can Read: {health.get('can_read', 'unknown')}")
            
            # Check overall config
            config_status = config.get_status()
            print(f"\n⚙️  Configuration Status:")
            print(f"  • Config Loaded: {config_status.get('config_loaded', False)}")
            print(f"  • Environment File: {config_status.get('environment_file', False)}")
            print(f"  • Airtable Configured: {config_status.get('airtable_configured', False)}")
            print(f"  • Supabase Configured: {config_status.get('supabase_configured', False)}")
            
        except Exception as e:
            print(f"❌ Health Check Error: {e}")
    
    def _records_to_dataframe(self, records: List) -> pd.DataFrame:
        """Convert Airtable records to pandas DataFrame."""
        if not records:
            return pd.DataFrame()
        
        # Extract all field data
        data = []
        for record in records:
            row = {"Record_ID": record.id, "Created_Time": record.created_time}
            row.update(record.fields)
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _show_business_summary(self, records: List):
        """Show business summary statistics."""
        business_counts = {}
        for record in records:
            business = record.get_field("Business", "Unknown")
            business_counts[business] = business_counts.get(business, 0) + 1
        
        print(f"\n🏢 Top Businesses:")
        for business, count in sorted(business_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {business}: {count} records")


def main():
    """Main entry point."""
    print("🚀 Starting LocalBase Airtable Viewer...")
    
    try:
        viewer = AirtableViewerTool()
        viewer.run_interactive_menu()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 