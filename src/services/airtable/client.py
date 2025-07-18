"""
Airtable Service Client
Professional Airtable integration with clean interfaces, error handling, and monitoring.
"""

import requests
from typing import Dict, Any, List, Optional
from time import sleep
import json

from ..base_service import BaseService
from .models import AirtableRecord, AirtableTable, AirtableQuery
from .exceptions import (
    AirtableError, 
    AirtableAuthError, 
    AirtableValidationError,
    AirtableRateLimitError,
    AirtableNotFoundError
)

class AirtableService(BaseService):
    """
    Professional Airtable service client.
    
    Provides clean interfaces for all Airtable operations with proper
    error handling, authentication, and monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Airtable service.
        
        Args:
            config: Must contain 'token', 'base_id', 'table_name'
        """
        super().__init__(config)
        
        # Validate required config
        required_keys = ['token', 'base_id', 'table_name']
        missing_keys = [key for key in required_keys if not config.get(key)]
        if missing_keys:
            raise AirtableValidationError(f"Missing required config keys: {missing_keys}")
        
        self.token = config['token']
        self.base_id = config['base_id']
        self.default_table = config['table_name']
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        })
        
    def authenticate(self) -> bool:
        """Test authentication with Airtable."""
        try:
            # Try to access the base metadata
            url = f"https://api.airtable.com/v0/meta/bases/{self.base_id}/tables"
            response = self.session.get(url)
            
            if response.status_code == 401:
                raise AirtableAuthError("Invalid Airtable token")
            elif response.status_code == 403:
                raise AirtableAuthError("Insufficient Airtable permissions")
            elif response.status_code != 200:
                raise AirtableError(f"Authentication check failed: {response.status_code}")
            
            self._authenticated = True
            self.logger.info("Airtable authentication successful")
            return True
            
        except requests.RequestException as e:
            raise AirtableError(f"Network error during authentication: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check Airtable service health."""
        try:
            # Quick check by getting 1 record
            records = self.get_records(max_records=1)
            
            return {
                "status": "healthy",
                "authenticated": self._authenticated,
                "base_id": self.base_id,
                "default_table": self.default_table,
                "can_read": True,
                "record_count_sample": len(records)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": self._authenticated
            }
    
    def get_records(
        self, 
        table_name: Optional[str] = None,
        query: Optional[AirtableQuery] = None,
        **kwargs
    ) -> List[AirtableRecord]:
        """
        Get records from Airtable.
        
        Args:
            table_name: Table name (uses default if not provided)
            query: AirtableQuery object with filters
            **kwargs: Additional query parameters for backward compatibility
            
        Returns:
            List of AirtableRecord objects
        """
        table_name = table_name or self.default_table
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}"
        
        # Build parameters
        params = {}
        if query:
            params.update(query.to_params())
        
        # Add any direct kwargs for backward compatibility
        for key in ['filterByFormula', 'maxRecords', 'fields', 'sort', 'view']:
            if key in kwargs:
                params[key] = kwargs[key]
        
        all_records = []
        
        try:
            while True:
                self._log_request("GET", url, params=params)
                response = self.session.get(url, params=params)
                self._handle_response_errors(response)
                
                data = response.json()
                records_data = data.get('records', [])
                
                # Convert to AirtableRecord objects
                records = [AirtableRecord.from_api_response(record) for record in records_data]
                all_records.extend(records)
                
                # Check for pagination
                offset = data.get('offset')
                if not offset:
                    break
                
                params['offset'] = offset
                
                # Rate limiting protection
                sleep(0.2)  # 5 requests per second max
            
            self.logger.info(f"Retrieved {len(all_records)} records from {table_name}")
            return all_records
            
        except requests.RequestException as e:
            raise AirtableError(f"Network error retrieving records: {e}")
    
    def create_record(self, data: Dict[str, Any], table_name: Optional[str] = None) -> AirtableRecord:
        """
        Create a new record.
        
        Args:
            data: Record data (can be full record dict or just fields)
            table_name: Table name (uses default if not provided)
            
        Returns:
            Created AirtableRecord
        """
        table_name = table_name or self.default_table
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}"
        
        # Ensure proper format
        if 'fields' not in data:
            data = {'fields': data}
        
        try:
            self._log_request("POST", url, data=data)
            response = self.session.post(url, json=data)
            self._handle_response_errors(response)
            
            record_data = response.json()
            record = AirtableRecord.from_api_response(record_data)
            
            self.logger.info(f"Created record {record.id} in {table_name}")
            return record
            
        except requests.RequestException as e:
            raise AirtableError(f"Network error creating record: {e}")
    
    def update_record(self, record_id: str, data: Dict[str, Any], table_name: Optional[str] = None) -> AirtableRecord:
        """
        Update an existing record.
        
        Args:
            record_id: Airtable record ID
            data: Updated data (can be full record dict or just fields)
            table_name: Table name (uses default if not provided)
            
        Returns:
            Updated AirtableRecord
        """
        table_name = table_name or self.default_table
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}/{record_id}"
        
        # Ensure proper format
        if 'fields' not in data:
            data = {'fields': data}
        
        try:
            self._log_request("PATCH", url, data=data)
            response = self.session.patch(url, json=data)
            self._handle_response_errors(response)
            
            record_data = response.json()
            record = AirtableRecord.from_api_response(record_data)
            
            self.logger.info(f"Updated record {record.id} in {table_name}")
            return record
            
        except requests.RequestException as e:
            raise AirtableError(f"Network error updating record: {e}")
    
    def delete_record(self, record_id: str, table_name: Optional[str] = None) -> bool:
        """
        Delete a record.
        
        Args:
            record_id: Airtable record ID
            table_name: Table name (uses default if not provided)
            
        Returns:
            True if deleted successfully
        """
        table_name = table_name or self.default_table
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}/{record_id}"
        
        try:
            self._log_request("DELETE", url)
            response = self.session.delete(url)
            self._handle_response_errors(response)
            
            self.logger.info(f"Deleted record {record_id} from {table_name}")
            return True
            
        except requests.RequestException as e:
            raise AirtableError(f"Network error deleting record: {e}")
    
    def search_records(self, search_term: str, fields: Optional[List[str]] = None, table_name: Optional[str] = None) -> List[AirtableRecord]:
        """
        Search for records containing a term.
        
        Args:
            search_term: Term to search for
            fields: Fields to search in (searches all if not provided)
            table_name: Table name (uses default if not provided)
            
        Returns:
            List of matching AirtableRecord objects
        """
        if fields:
            # Build formula to search specific fields
            field_conditions = [f"SEARCH(LOWER('{search_term}'), LOWER(CONCATENATE({field})))" for field in fields]
            formula = f"OR({', '.join(field_conditions)})"
        else:
            # Simple search across all fields (less efficient but comprehensive)
            formula = f"SEARCH(LOWER('{search_term}'), LOWER(CONCATENATE(ARRAYJOIN(VALUES, ' '))))"
        
        query = AirtableQuery(filter_formula=formula)
        return self.get_records(table_name=table_name, query=query)
    
    def _handle_response_errors(self, response: requests.Response) -> None:
        """Handle Airtable API response errors."""
        if response.status_code == 200:
            return
        
        try:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Unknown error')
        except:
            error_message = response.text or f"HTTP {response.status_code}"
        
        if response.status_code == 401:
            raise AirtableAuthError("Invalid or expired Airtable token")
        elif response.status_code == 403:
            raise AirtableAuthError("Insufficient Airtable permissions")
        elif response.status_code == 404:
            raise AirtableNotFoundError("record or table", "unknown")
        elif response.status_code == 422:
            raise AirtableValidationError(error_message)
        elif response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise AirtableRateLimitError(int(retry_after) if retry_after else None)
        else:
            raise AirtableError(error_message, status_code=response.status_code) 