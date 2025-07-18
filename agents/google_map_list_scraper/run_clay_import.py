#!/usr/bin/env python3
"""
Run Clay.com Import
Simple script to import scraped addresses to Clay.com
"""

import sys
import os

# Add the parent directory to the path so we can import from the main localbase config
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from clay_integration import main

if __name__ == "__main__":
    main() 