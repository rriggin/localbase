#!/usr/bin/env python3
"""
Convenience script to run the RoofMaxx Data Agent
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from agents.roofmaxx_data_agent.agent import main

if __name__ == "__main__":
    main() 