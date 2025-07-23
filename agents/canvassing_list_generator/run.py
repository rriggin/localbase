#!/usr/bin/env python3
"""
Convenience script to run the Canvassing List Generator Agent
"""

import sys
import os
import argparse
import subprocess

def activate_venv_and_run():
    """Activate virtual environment and run the script."""
    # Get the project root directory
    project_root = os.path.join(os.path.dirname(__file__), '../../')
    project_root = os.path.abspath(project_root)
    
    # Path to virtual environment
    venv_path = os.path.join(project_root, 'venv', 'bin', 'activate')
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # Already in virtual environment, proceed normally
        return False
    
    # Check if virtual environment exists
    if os.path.exists(venv_path):
        # Build command to activate venv and run this script
        script_path = os.path.abspath(__file__)
        cmd = f'source "{venv_path}" && python3 "{script_path}" {" ".join(sys.argv[1:])}'
        
        print("🔄 Activating virtual environment...")
        # Execute with shell=True to handle the source command
        result = subprocess.run(cmd, shell=True, cwd=project_root)
        sys.exit(result.returncode)
    else:
        print("⚠️  Virtual environment not found. Please run from project root or create venv.")
        return False

# Check if we need to activate virtual environment
if activate_venv_and_run() is not False:
    sys.exit(0)

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from agents.canvassing_list_generator.agent import GoogleMapsAgent
from src.config import config

def main():
    """Run the Canvassing List Generator Agent with a Google Maps URL."""
    
    parser = argparse.ArgumentParser(description='Google Maps Canvassing List Generator')
    parser.add_argument('url', help='Google Maps list URL to extract addresses from')
    parser.add_argument('--list-title', '-t', 
                       help='List title for records (will extract from list if not provided)')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode (default: True)')
    parser.add_argument('--timeout', type=int, default=60,
                       help='Selenium timeout in seconds (default: 60)')
    parser.add_argument('--no-airtable', action='store_true',
                       help='Skip saving to Airtable (uses gist workflow)')
    
    args = parser.parse_args()
    
    print("🤖 Google Maps Canvassing List Generator")
    print("=" * 50)
    print(f"📍 URL: {args.url}")
    print(f"📋 List Title: {args.list_title or 'Will extract from list'}")
    print(f"🔄 Starting extraction...")
    
    try:
        # Initialize agent without Airtable service for gist workflow
        agent = GoogleMapsAgent(
            config={"timeout": args.timeout},
            services={}  # No services needed for gist workflow
        )
        
        # Execute agent (defaults to gist workflow)
        result = agent.execute({
            'list_url': args.url,
            'list_title': args.list_title,
            'headless': args.headless,
            'timeout': args.timeout
        })
        
        # Display results
        if result['status'] == 'success':
            print("✅ Extraction completed successfully!")
            print(f"📊 Extracted {result['addresses_count']} addresses")
            print(f"📋 List Title: {result['list_title']}")
            print(f"🔄 Workflow: {result['workflow']} (gist → Zapier → Clay)")
            
            print(f"\n📍 Sample addresses (from agent extraction):")
            print("   Note: Full data has been saved to Gist for Zapier/Clay integration")
                
        else:
            print(f"❌ Extraction failed: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error running agent: {e}")

if __name__ == "__main__":
    main() 