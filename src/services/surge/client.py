"""
Surge.sh Service Client
Professional Surge.sh integration for deploying static files with random subdomain generation.
"""

import os
import subprocess
import shutil
import tempfile
import random
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..base_service import BaseService
from .models import SurgeConfig, SurgeDeployment
from .exceptions import (
    SurgeError,
    SurgeDeploymentError,
    SurgeAuthenticationError,
    SurgeValidationError,
    SurgeConnectionError
)

class SurgeService(BaseService):
    """
    Professional Surge.sh service client.
    
    Provides deployment of static files to Surge.sh with automatic
    random subdomain generation and professional error handling.
    """
    
    # Word lists for random domain generation
    ADJECTIVES = [
        'amazing', 'awesome', 'brilliant', 'clever', 'cool', 'creative', 'elegant', 'epic',
        'fantastic', 'funny', 'genius', 'happy', 'hyper', 'incredible', 'jolly', 'keen',
        'lively', 'magical', 'nice', 'outstanding', 'perfect', 'quick', 'radiant', 'super',
        'terrific', 'unique', 'vibrant', 'wonderful', 'xenial', 'youthful', 'zealous',
        'bold', 'bright', 'calm', 'daring', 'eager', 'fierce', 'gentle', 'honest',
        'intense', 'joyful', 'kind', 'loyal', 'mighty', 'noble', 'optimistic', 'proud',
        'quiet', 'robust', 'smooth', 'tender', 'upbeat', 'vivid', 'wise', 'zesty'
    ]
    
    NOUNS = [
        'anchor', 'balloon', 'castle', 'dragon', 'eagle', 'forest', 'garden', 'harbor',
        'island', 'jaguar', 'knight', 'lighthouse', 'mountain', 'ocean', 'pillow', 'quartz',
        'river', 'sunset', 'tiger', 'umbrella', 'valley', 'waterfall', 'xenon', 'yacht', 'zebra',
        'bridge', 'cloud', 'diamond', 'ember', 'falcon', 'glacier', 'horizon', 'iris',
        'jewel', 'kite', 'lantern', 'meadow', 'nebula', 'opal', 'phoenix', 'quest',
        'rainbow', 'star', 'thunder', 'universe', 'volcano', 'wave', 'crystal', 'prism'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Surge.sh service.
        
        Args:
            config: Service configuration (optional surge_email, surge_token)
        """
        super().__init__(config)
        
        self.surge_email = config.get('surge_email')
        self.surge_token = config.get('surge_token')
        
        # Check if surge CLI is installed
        self._check_surge_cli()
    
    def authenticate(self) -> bool:
        """Test authentication with Surge.sh."""
        try:
            # Check if surge is logged in
            result = subprocess.run(
                ['surge', 'whoami'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self._authenticated = True
                self.logger.info("Surge.sh authentication successful")
                return True
            else:
                # Try to login if credentials provided
                if self.surge_email and self.surge_token:
                    return self._login()
                else:
                    self.logger.warning("Surge.sh not authenticated and no credentials provided")
                    return False
                    
        except subprocess.TimeoutExpired:
            raise SurgeConnectionError("Surge.sh authentication timeout")
        except FileNotFoundError:
            raise SurgeError("Surge CLI not found. Install with: npm install -g surge")
    
    def health_check(self) -> Dict[str, Any]:
        """Check Surge.sh service health."""
        try:
            # Check CLI availability
            surge_version = self._get_surge_version()
            
            # Check authentication
            auth_status = self.authenticate()
            
            return {
                "status": "healthy" if auth_status else "warning",
                "authenticated": auth_status,
                "surge_version": surge_version,
                "cli_available": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": False,
                "cli_available": False
            }
    
    def generate_random_domain(self) -> str:
        """
        Generate a random two-word domain for Surge.sh.
        
        Returns:
            Random domain like 'funny-pillow' or 'hyper-jaguar'
        """
        adjective = random.choice(self.ADJECTIVES)
        noun = random.choice(self.NOUNS)
        return f"{adjective}-{noun}"
    
    def deploy_file(self, 
                   file_path: str, 
                   config: Optional[SurgeConfig] = None) -> SurgeDeployment:
        """
        Deploy a single file to Surge.sh.
        
        Args:
            file_path: Path to the file to deploy
            config: Optional deployment configuration
            
        Returns:
            SurgeDeployment with deployment results
        """
        if not os.path.exists(file_path):
            raise SurgeValidationError(f"File not found: {file_path}")
        
        config = config or SurgeConfig()
        
        # Generate random domain if not provided
        domain = config.domain or self.generate_random_domain()
        
        # Create temporary directory for deployment
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy file to temp directory
            file_name = os.path.basename(file_path)
            temp_file_path = os.path.join(temp_dir, file_name)
            shutil.copy2(file_path, temp_file_path)
            
            # If it's not index.html, create index.html that redirects
            if file_name != 'index.html':
                index_path = os.path.join(temp_dir, 'index.html')
                with open(index_path, 'w') as f:
                    f.write(f'<script>window.location.href = "{file_name}";</script>')
            
            return self.deploy_directory(temp_dir, config)
    
    def deploy_directory(self, 
                        dir_path: str, 
                        config: Optional[SurgeConfig] = None) -> SurgeDeployment:
        """
        Deploy a directory to Surge.sh.
        
        Args:
            dir_path: Path to the directory to deploy
            config: Optional deployment configuration
            
        Returns:
            SurgeDeployment with deployment results
        """
        if not os.path.exists(dir_path):
            raise SurgeValidationError(f"Directory not found: {dir_path}")
        
        config = config or SurgeConfig()
        
        # Generate random domain if not provided
        domain = config.domain or self.generate_random_domain()
        full_domain = f"{domain}.surge.sh"
        
        try:
            # Count files for metadata
            file_count = sum(1 for _ in Path(dir_path).rglob('*') if _.is_file())
            
            # Run surge deployment
            cmd = ['surge', dir_path, full_domain]
            
            self.logger.info(f"Deploying to {full_domain}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=dir_path
            )
            
            if result.returncode == 0:
                # Successful deployment
                url = f"https://{full_domain}"
                
                deployment = SurgeDeployment(
                    success=True,
                    domain=full_domain,
                    url=url,
                    project_name=config.project_name or domain,
                    deployed_at=datetime.now(),
                    file_count=file_count
                )
                
                self.logger.info(f"Successfully deployed to {url}")
                return deployment
            else:
                # Deployment failed
                error_msg = result.stderr or result.stdout or "Unknown deployment error"
                
                deployment = SurgeDeployment(
                    success=False,
                    domain=full_domain,
                    url="",
                    error=error_msg,
                    error_details={'returncode': result.returncode, 'stdout': result.stdout}
                )
                
                self.logger.error(f"Deployment failed: {error_msg}")
                return deployment
                
        except subprocess.TimeoutExpired:
            return SurgeDeployment(
                success=False,
                domain=full_domain,
                url="",
                error="Deployment timeout after 60 seconds"
            )
        except Exception as e:
            return SurgeDeployment(
                success=False,
                domain=full_domain,
                url="",
                error=f"Deployment error: {str(e)}"
            )
    
    def deploy_chart(self, chart_file_path: str, chart_name: str = None) -> SurgeDeployment:
        """
        Deploy a chart file with a completely random domain name.
        
        Args:
            chart_file_path: Path to the chart HTML file
            chart_name: Optional name for the chart (used in project metadata only)
            
        Returns:
            SurgeDeployment with deployment results
        """
        # Always use completely random domain (no business context)
        domain = self.generate_random_domain()
        
        config = SurgeConfig(
            domain=domain,
            project_name=chart_name or "Chart Deployment",
            description=f"Interactive chart deployed via LocalBase"
        )
        
        return self.deploy_file(chart_file_path, config)
    
    def list_deployments(self) -> List[str]:
        """
        List current deployments (requires authentication).
        
        Returns:
            List of deployed domains
        """
        try:
            result = subprocess.run(
                ['surge', 'list'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse the output to extract domains
                domains = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and '.surge.sh' in line:
                        domains.append(line)
                return domains
            else:
                self.logger.warning("Could not list deployments")
                return []
                
        except Exception as e:
            self.logger.error(f"Error listing deployments: {e}")
            return []
    
    def teardown_deployment(self, domain: str) -> bool:
        """
        Remove a deployment from Surge.sh.
        
        Args:
            domain: Domain to teardown (with or without .surge.sh)
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure domain has .surge.sh suffix
        if not domain.endswith('.surge.sh'):
            domain = f"{domain}.surge.sh"
        
        try:
            result = subprocess.run(
                ['surge', 'teardown', domain],
                capture_output=True,
                text=True,
                timeout=30,
                input='y\n'  # Confirm teardown
            )
            
            success = result.returncode == 0
            if success:
                self.logger.info(f"Successfully tore down {domain}")
            else:
                self.logger.error(f"Failed to teardown {domain}: {result.stderr}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error tearing down {domain}: {e}")
            return False
    
    def _check_surge_cli(self):
        """Check if Surge CLI is installed."""
        try:
            subprocess.run(['surge', '--version'], capture_output=True, timeout=5)
        except FileNotFoundError:
            raise SurgeError(
                "Surge CLI not found. Install with: npm install -g surge"
            )
        except subprocess.TimeoutExpired:
            raise SurgeConnectionError("Surge CLI check timeout")
    
    def _get_surge_version(self) -> str:
        """Get Surge CLI version."""
        try:
            result = subprocess.run(
                ['surge', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _login(self) -> bool:
        """Login to Surge.sh with provided credentials."""
        if not self.surge_email or not self.surge_token:
            return False
        
        try:
            # Note: Surge CLI login is typically interactive
            # For automated deployment, users should login manually first
            # or use environment variables
            self.logger.warning(
                "Automated login not implemented. Please run 'surge login' manually."
            )
            return False
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False 