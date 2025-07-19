"""
Canvassing List Generator Agent

Business-focused agent that generates high-quality prospect lists for canvassing operations.

Takes geographic data sources (currently Google Maps) and orchestrates multiple services
to produce actionable prospect lists ready for sales outreach.

Key Features:
- Geographic data extraction and validation
- Address standardization and enrichment  
- Lead scoring and qualification
- Multi-channel output (Clay, Airtable, CSV)
- Automated workflow integration
"""

from .agent import GoogleMapsAgent
from .scraper import GoogleMapsListScraper

__all__ = ['GoogleMapsAgent', 'GoogleMapsListScraper']
__version__ = "1.0.0" 