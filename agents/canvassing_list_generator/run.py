#!/usr/bin/env python3
"""
Convenience script to run the Canvassing List Generator Agent
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from agents.canvassing_list_generator import GoogleMapsAgent

def main():
    """Run the Canvassing List Generator Agent interactively."""
    print("🤖 Canvassing List Generator Agent")
    print("=" * 50)
    print("Professional Google Maps list extraction and address processing")
    print("\nFor detailed usage, see: agents/canvassing_list_generator/README.md")
    print("Core files in this agent:")
    print("• agent.py - Main GoogleMapsAgent class")
    print("• scraper.py - Core Google Maps scraping functionality") 
    print("• backup/ - Previous iterations and experimental scripts")
    
    # Example of how to initialize the agent
    print("\n📝 Example agent initialization:")
    print("```python")
    print("from agents.canvassing_list_generator import GoogleMapsAgent")
    print("agent = GoogleMapsAgent(config, services)")
    print("result = agent.process_google_maps_list(list_url)")
    print("```")

if __name__ == "__main__":
    main() 