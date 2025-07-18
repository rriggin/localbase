"""
Environment variable loader for LocalBase
Loads environment variables from .env file
"""

import os
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"Warning: .env file not found at {env_path}")

if __name__ == "__main__":
    load_env() 