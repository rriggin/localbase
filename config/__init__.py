"""
LocalBase Configuration Package

Contains configuration utilities for the LocalBase project:
- env: Environment variable loading utilities

Modern configuration is handled by src.config module.
"""

# Re-export common utilities for convenience
from .env import load_env

__all__ = ['load_env'] 