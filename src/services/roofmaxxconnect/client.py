"""
RoofMaxx Connect Service Client
Professional RoofMaxx Connect API integration for dealer management and lead tracking.
"""

import requests
from typing import Dict, Any, List, Optional, Union
import json
from urllib.parse import urlencode
from datetime import datetime

from ..base_service import BaseService
from .models import (
    RoofmaxxRecord, DealRecord, DealerRecord, PaginatedResponse, 
    RoofmaxxTable, RoofmaxxQuery, DealQueryBuilder, PaginationMeta
)
from .exceptions import (
    RoofmaxxError,
    RoofmaxxAuthError,
    RoofmaxxValidationError,
    RoofmaxxRateLimitError,
    RoofmaxxNotFoundError
)

class RoofmaxxConnectService(BaseService):
    """
    Professional RoofMaxx Connect service client.
    
    Provides clean interfaces for dealer data access, lead management,
    and customer relationship management with proper error handling and monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize RoofMaxx Connect service.
        
        Args:
            config: Must contain 'bearer_token', optionally 'base_url'
        """
        super().__init__(config)
        
        # Validate required config
        if not config.get('bearer_token'):
            raise RoofmaxxValidationError("Missing required 'bearer_token' in config")
        
        self.bearer_token = config['bearer_token']
        self.base_url = config.get('base_url', 'https://roofmaxxconnect.com').rstrip('/')
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'localbase-roofmaxxconnect-client/1.0'
        })
        
        # Define default table
        self.dealers_table = RoofmaxxTable("dealers")
    
    def authenticate(self) -> bool:
        """
        Test authentication with the RoofMaxx Connect API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Try accessing the dealers endpoint which we know works
            response = self.session.get(f"{self.base_url}/api/v2/dealers?per_page=1", timeout=10)
            
            if response.status_code == 401:
                self.logger.error("Authentication failed - invalid bearer token")
                self._authenticated = False
                return False
            
            if response.status_code == 200:
                self._authenticated = True
                self.logger.info("Authentication successful")
                return True
            
            self.logger.warning(f"Unexpected response during auth test: {response.status_code}")
            return False
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Authentication test failed: {e}")
            self._authenticated = False
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check service health and connectivity.
        
        Returns:
            Dict with health status and metrics
        """
        try:
            start_time = datetime.now()
            
            # Try to connect to the dealers endpoint
            response = self.session.get(f"{self.base_url}/api/v2/dealers?per_page=1", timeout=5)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_seconds": response_time,
                "api_accessible": True,
                "authenticated": self._authenticated,
                "base_url": self.base_url
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_accessible": False,
                "authenticated": False,
                "base_url": self.base_url
            }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            RoofmaxxError: For various API errors
        """
        url = f"{self.base_url}{endpoint}"
        self._log_request(method, endpoint, **kwargs)
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle common HTTP errors
            if response.status_code == 401:
                raise RoofmaxxAuthError("Invalid or expired bearer token")
            elif response.status_code == 403:
                raise RoofmaxxAuthError("Forbidden - insufficient permissions for this resource")
            elif response.status_code == 404:
                raise RoofmaxxNotFoundError("endpoint", endpoint)
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                raise RoofmaxxRateLimitError(int(retry_after) if retry_after else None)
            elif response.status_code >= 400:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    pass
                raise RoofmaxxError(error_msg, status_code=response.status_code)
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise RoofmaxxError(f"Request failed: {e}")
    
    # =======================
    # DEALERS API METHODS
    # =======================
    
    def get_dealers(self, page: int = 1, per_page: int = 100) -> PaginatedResponse:
        """
        Get dealers with pagination.
        
        Args:
            page: Page number (default: 1)
            per_page: Records per page (default: 100)
            
        Returns:
            PaginatedResponse with dealer records
        """
        params = {'page': page, 'per_page': per_page}
        query_string = urlencode(params)
        endpoint = f"/api/v2/dealers?{query_string}"
        
        response = self._make_request('GET', endpoint)
        response_data = response.json()
        
        return PaginatedResponse.from_api_response(response_data, DealerRecord)
    
    def get_all_dealers(self, max_pages: int = 50) -> List[DealerRecord]:
        """
        Get all dealers with automatic pagination.
        
        Args:
            max_pages: Maximum number of pages to fetch (safety limit)
            
        Returns:
            List of all DealerRecord objects
        """
        all_dealers = []
        page = 1
        
        while page <= max_pages:
            paginated_response = self.get_dealers(page=page, per_page=100)
            
            if not paginated_response.data:
                break
                
            all_dealers.extend(paginated_response.data)
            page += 1
            
            # If we've reached the last page, stop
            if page > paginated_response.meta.last_page:
                break
        
        self.logger.info(f"Fetched {len(all_dealers)} total dealers")
        return all_dealers
    
    def get_dealer_by_id(self, dealer_id: int) -> Optional[DealerRecord]:
        """
        Get a specific dealer by ID.
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            DealerRecord if found, None otherwise
        """
        try:
            endpoint = f"/api/v2/dealers/{dealer_id}"
            response = self._make_request('GET', endpoint)
            dealer_data = response.json()
            return DealerRecord.from_api_response(dealer_data)
        except RoofmaxxNotFoundError:
            return None
    
    def search_dealers(self, search_term: str = None, page: int = 1, per_page: int = 100) -> List[DealerRecord]:
        """
        Search dealers by name or brand.
        
        Args:
            search_term: Search term for dealer name/brand
            page: Page number
            per_page: Records per page
            
        Returns:
            List of matching DealerRecord objects
        """
        params = {'page': page, 'per_page': per_page}
        if search_term:
            params['search'] = search_term
        
        query_string = urlencode(params)
        endpoint = f"/api/v2/dealers?{query_string}"
        
        response = self._make_request('GET', endpoint)
        response_data = response.json()
        
        paginated_response = PaginatedResponse.from_api_response(response_data, DealerRecord)
        return paginated_response.data
    
    # =======================
    # DEALS API METHODS
    # =======================
    
    def get_dealer_deals(self, rmc_id: Union[str, int], **params) -> Dict[str, Any]:
        """
        Get deals for a specific dealer.
        
        Args:
            rmc_id: RoofMaxx Connect dealer ID
            **params: Query parameters (page, per_page, columns, etc.)
            
        Returns:
            API response with deals data
        """
        endpoint = f"/api/v2/dealers/{rmc_id}/deals"
        
        if params:
            query_string = urlencode(params)
            endpoint += f"?{query_string}"
        
        response = self._make_request('GET', endpoint)
        return response.json()
    
    def get_deals(self, rmc_id: Union[str, int], query: Optional[DealQueryBuilder] = None) -> List[DealRecord]:
        """
        Get deals with optional query builder.
        
        Args:
            rmc_id: Dealer ID
            query: Optional query builder for filtering
            
        Returns:
            List of DealRecord objects
        """
        params = query.build_params() if query else {}
        
        response_data = self.get_dealer_deals(rmc_id, **params)
        
        # Handle different possible response structures
        deals_data = response_data
        if isinstance(response_data, dict):
            deals_data = response_data.get('data', response_data.get('deals', []))
        
        if not isinstance(deals_data, list):
            deals_data = [deals_data] if deals_data else []
        
        return [DealRecord.from_api_response(deal) for deal in deals_data]
    
    def get_deal_by_id(self, rmc_id: Union[str, int], deal_id: str) -> Optional[DealRecord]:
        """
        Get a specific deal by ID.
        
        Args:
            rmc_id: Dealer ID
            deal_id: Deal ID
            
        Returns:
            DealRecord if found, None otherwise
        """
        try:
            endpoint = f"/api/v2/dealers/{rmc_id}/deals/{deal_id}"
            response = self._make_request('GET', endpoint)
            deal_data = response.json()
            return DealRecord.from_api_response(deal_data)
        except (RoofmaxxNotFoundError, RoofmaxxAuthError):
            return None
    
    def create_deal_query(self, rmc_id: Union[str, int]) -> DealQueryBuilder:
        """
        Create a query builder for deals.
        
        Args:
            rmc_id: Dealer ID
            
        Returns:
            DealQueryBuilder instance
        """
        return DealQueryBuilder(str(rmc_id))
    
    def search_deals(self, rmc_id: Union[str, int], status: str = None, page: int = 1, per_page: int = 50) -> List[DealRecord]:
        """
        Search deals with common filters.
        
        Args:
            rmc_id: Dealer ID
            status: Filter by deal status
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            List of DealRecord objects
        """
        query = self.create_deal_query(rmc_id).paginate(page, per_page)
        
        if status:
            query.filter_by_status(status)
        
        return self.get_deals(rmc_id, query)
    
    def get_all_deals(self, rmc_id: Union[str, int], max_pages: int = 10) -> List[DealRecord]:
        """
        Get all deals for a dealer with automatic pagination.
        
        Args:
            rmc_id: Dealer ID
            max_pages: Maximum number of pages to fetch (safety limit)
            
        Returns:
            List of all DealRecord objects
        """
        all_deals = []
        page = 1
        
        while page <= max_pages:
            deals = self.search_deals(rmc_id, page=page, per_page=100)
            
            if not deals:
                break
                
            all_deals.extend(deals)
            page += 1
            
            # If we got less than 100 results, we've reached the end
            if len(deals) < 100:
                break
        
        self.logger.info(f"Fetched {len(all_deals)} total deals for dealer {rmc_id}")
        return all_deals
    
    # =======================
    # UTILITY METHODS
    # =======================
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get API statistics and overview.
        
        Returns:
            Dictionary with API statistics
        """
        try:
            # Get dealer statistics
            dealers_response = self.get_dealers(page=1, per_page=1)
            
            return {
                "total_dealers": dealers_response.meta.total,
                "dealers_per_page": dealers_response.meta.per_page,
                "total_pages": dealers_response.meta.last_page,
                "api_base_url": self.base_url,
                "authenticated": self._authenticated
            }
        except Exception as e:
            return {
                "error": str(e),
                "api_base_url": self.base_url,
                "authenticated": self._authenticated
            }
    
    def discover_api_endpoints(self) -> Dict[str, Any]:
        """
        Attempt to discover available API endpoints.
        
        Returns:
            Dictionary with discovery results
        """
        discovery_results = {
            "base_url": self.base_url,
            "endpoints_tested": [],
            "available_endpoints": [],
            "errors": []
        }
        
        # Known working endpoints based on our testing
        test_endpoints = [
            "/api/v2/dealers",
            "/api/docs",
            "/api/v2/health",
            "/api/v1/health",
            "/health",
            "/status"
        ]
        
        for endpoint in test_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                discovery_results["endpoints_tested"].append({
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "accessible": response.status_code in [200, 401]  # 401 means endpoint exists but needs auth
                })
                
                if response.status_code in [200, 401]:
                    discovery_results["available_endpoints"].append(endpoint)
                    
            except requests.exceptions.RequestException as e:
                discovery_results["errors"].append({
                    "endpoint": endpoint,
                    "error": str(e)
                })
        
        return discovery_results 