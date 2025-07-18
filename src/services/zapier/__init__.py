"""
Zapier Service Package

Provides integration with Zapier for workflow automation across agents.
Handles webhook triggers, batch processing, and workflow orchestration.
"""

from .client import ZapierService

__all__ = ['ZapierService']
__version__ = "1.0.0" 