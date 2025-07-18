"""
Supabase Service Client
Professional Supabase integration for call logs and real-time data.
"""

import requests
from typing import Dict, Any, List, Optional
import json

from ..base_service import BaseService
from .models import CallLogRecord, SupabaseTable, SupabaseQuery, CallLogQueryBuilder
from .exceptions import (
    SupabaseError,
    SupabaseAuthError, 
    SupabaseValidationError,
    SupabaseConnectionError,
    SupabaseNotFoundError
)

class SupabaseService(BaseService):
    """
    Professional Supabase service client.
    
    Provides clean interfaces for call log storage, queries, and analytics
    with proper error handling and monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Supabase service.
        
        Args:
            config: Must contain 'url', 'access_token', optionally 'anon_key'
        """
        super().__init__(config)
        
        # Validate required config
        required_keys = ['url', 'access_token']
        missing_keys = [key for key in required_keys if not config.get(key)]
        if missing_keys:
            raise SupabaseValidationError(f"Missing required config keys: {missing_keys}")
        
        self.url = config['url'].rstrip('/')  # Remove trailing slash
        self.access_token = config['access_token']
        self.anon_key = config.get('anon_key', self.access_token)
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'apikey': self.anon_key
        })
        
        # Define call_logs table
        self.call_logs_table = SupabaseTable("call_logs")
        
    def authenticate(self) -> bool:
        """Test authentication with Supabase."""
        try:
            # Try a simple query to test auth
            url = f"{self.url}/rest/v1/{self.call_logs_table.name}"
            params = {'limit': 1}
            
            self._log_request("GET", url, params=params)
            response = self.session.get(url, params=params)
            
            if response.status_code == 401:
                raise SupabaseAuthError("Invalid Supabase access token")
            elif response.status_code == 403:
                raise SupabaseAuthError("Insufficient Supabase permissions")
            elif response.status_code not in [200, 206]:  # 206 is partial content
                raise SupabaseError(f"Authentication check failed: {response.status_code}")
            
            self._authenticated = True
            self.logger.info("Supabase authentication successful")
            return True
            
        except requests.RequestException as e:
            raise SupabaseConnectionError(f"Network error during authentication: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check Supabase service health."""
        try:
            # Try to get a count of call logs
            count = self.get_call_count()
            
            return {
                "status": "healthy",
                "authenticated": self._authenticated,
                "url": self.url,
                "call_logs_table": self.call_logs_table.name,
                "can_read": True,
                "total_call_logs": count
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": self._authenticated
            }
    
    def create_call_logs_table(self) -> bool:
        """
        Create the call_logs table with proper schema.
        
        Returns:
            True if table created successfully
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS call_logs (
            id SERIAL PRIMARY KEY,
            call_id VARCHAR UNIQUE,
            from_number VARCHAR,
            to_number VARCHAR,
            from_name VARCHAR,
            to_name VARCHAR,
            direction VARCHAR, -- 'Inbound', 'Outbound'
            duration INTEGER, -- seconds
            result VARCHAR, -- 'Connected', 'No Answer', 'Busy', etc.
            start_time TIMESTAMP,
            extension VARCHAR,
            queue VARCHAR,
            handle_time INTEGER,
            raw_data JSONB, -- Store original data from Zapier
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_call_logs_start_time ON call_logs(start_time);
        CREATE INDEX IF NOT EXISTS idx_call_logs_direction ON call_logs(direction);
        CREATE INDEX IF NOT EXISTS idx_call_logs_duration ON call_logs(duration);
        CREATE INDEX IF NOT EXISTS idx_call_logs_extension ON call_logs(extension);
        """
        
        try:
            # Execute SQL via Supabase RPC endpoint
            url = f"{self.url}/rest/v1/rpc/exec_sql"
            
            self._log_request("POST", url, sql=create_table_sql)
            response = self.session.post(url, json={"sql": create_table_sql})
            
            if response.status_code in [200, 201]:
                self.logger.info("Call logs table created successfully")
                return True
            else:
                error_text = response.text
                self.logger.error(f"Failed to create table: {response.status_code} - {error_text}")
                return False
                
        except requests.RequestException as e:
            raise SupabaseConnectionError(f"Network error creating table: {e}")
    
    def insert_call_log(self, call_data: CallLogRecord) -> CallLogRecord:
        """
        Insert a call log record.
        
        Args:
            call_data: CallLogRecord to insert
            
        Returns:
            Inserted CallLogRecord with ID
        """
        url = f"{self.url}/rest/v1/{self.call_logs_table.name}"
        data = call_data.to_dict()
        
        try:
            self._log_request("POST", url, data=data)
            response = self.session.post(url, json=data)
            self._handle_response_errors(response)
            
            if response.status_code in [200, 201]:
                result_data = response.json()
                if isinstance(result_data, list) and len(result_data) > 0:
                    return CallLogRecord.from_api_response(result_data[0])
                else:
                    return CallLogRecord.from_api_response(result_data)
            else:
                raise SupabaseError(f"Insert failed: {response.status_code}")
                
        except requests.RequestException as e:
            raise SupabaseConnectionError(f"Network error inserting call log: {e}")
    
    def get_call_logs(
        self, 
        query: Optional[SupabaseQuery] = None,
        **kwargs
    ) -> List[CallLogRecord]:
        """
        Get call logs from Supabase.
        
        Args:
            query: SupabaseQuery object with filters
            **kwargs: Additional query parameters for backward compatibility
            
        Returns:
            List of CallLogRecord objects
        """
        url = f"{self.url}/rest/v1/{self.call_logs_table.name}"
        
        # Build parameters
        params = {}
        if query:
            params.update(query.to_params())
        
        # Add any direct kwargs for backward compatibility
        for key in ['select', 'limit', 'offset', 'order']:
            if key in kwargs:
                params[key] = kwargs[key]
        
        try:
            self._log_request("GET", url, params=params)
            response = self.session.get(url, params=params)
            self._handle_response_errors(response)
            
            records_data = response.json()
            if not isinstance(records_data, list):
                records_data = [records_data]
            
            records = [CallLogRecord.from_api_response(record) for record in records_data]
            
            self.logger.info(f"Retrieved {len(records)} call log records")
            return records
            
        except requests.RequestException as e:
            raise SupabaseConnectionError(f"Network error retrieving call logs: {e}")
    
    def get_calls_over_threshold(self, threshold_seconds: int = 90, limit: int = None) -> List[CallLogRecord]:
        """Get calls longer than threshold duration."""
        query_builder = CallLogQueryBuilder()
        query_builder.over_threshold(threshold_seconds).order_by_duration()
        
        if limit:
            query_builder.limit(limit)
        
        return self.get_call_logs(query=query_builder.build())
    
    def get_call_count(self) -> int:
        """Get total number of call logs."""
        url = f"{self.url}/rest/v1/{self.call_logs_table.name}"
        params = {'select': 'count'}
        
        try:
            response = self.session.get(url, params=params)
            self._handle_response_errors(response)
            
            # Supabase returns count in a specific format
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('count', 0)
            return 0
            
        except requests.RequestException as e:
            raise SupabaseConnectionError(f"Network error getting call count: {e}")
    
    def get_call_statistics(
        self, 
        date_from: str = None, 
        date_to: str = None,
        threshold_seconds: int = 90
    ) -> Dict[str, Any]:
        """
        Get call statistics and analytics.
        
        Args:
            date_from: Start date filter
            date_to: End date filter  
            threshold_seconds: Duration threshold for analysis
            
        Returns:
            Dictionary with call statistics
        """
        try:
            # Get all calls in date range
            query_builder = CallLogQueryBuilder()
            if date_from:
                query_builder.date_range(date_from, date_to)
            
            all_calls = self.get_call_logs(query=query_builder.build())
            
            # Calculate statistics
            total_calls = len(all_calls)
            total_duration = sum(call.duration or 0 for call in all_calls)
            calls_over_threshold = [call for call in all_calls if call.is_over_threshold(threshold_seconds)]
            
            avg_duration = total_duration / total_calls if total_calls > 0 else 0
            
            return {
                "total_calls": total_calls,
                "total_duration": total_duration,
                "average_duration": avg_duration,
                "calls_over_threshold": len(calls_over_threshold),
                "percentage_over_threshold": (len(calls_over_threshold) / total_calls * 100) if total_calls > 0 else 0,
                "threshold_seconds": threshold_seconds,
                "date_range": {"from": date_from, "to": date_to}
            }
            
        except requests.RequestException as e:
            raise SupabaseConnectionError(f"Network error getting statistics: {e}")
    
    def create_zapier_webhook_config(self) -> Dict[str, Any]:
        """Generate Zapier webhook configuration."""
        webhook_config = {
            "description": "Zapier webhook configuration for RingCentral → Supabase",
            "webhook_url": f"{self.url}/rest/v1/{self.call_logs_table.name}",
            "headers": {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "apikey": self.anon_key
            },
            "method": "POST",
            "body_mapping": {
                "call_id": "{{call_id}}",
                "from_number": "{{from_number}}",
                "to_number": "{{to_number}}",
                "from_name": "{{from_name}}",
                "to_name": "{{to_name}}",
                "direction": "{{direction}}",
                "duration": "{{duration}}",
                "result": "{{result}}",
                "start_time": "{{start_time}}",
                "extension": "{{extension}}",
                "queue": "{{queue}}",
                "handle_time": "{{handle_time}}",
                "raw_data": "{{*}}"  # All fields as JSON
            }
        }
        
        return webhook_config
    
    def _handle_response_errors(self, response: requests.Response) -> None:
        """Handle Supabase API response errors."""
        if response.status_code in [200, 201, 206]:
            return
        
        try:
            error_data = response.json()
            error_message = error_data.get('message', 'Unknown error')
        except:
            error_message = response.text or f"HTTP {response.status_code}"
        
        if response.status_code == 401:
            raise SupabaseAuthError("Invalid or expired Supabase token")
        elif response.status_code == 403:
            raise SupabaseAuthError("Insufficient Supabase permissions")
        elif response.status_code == 404:
            raise SupabaseNotFoundError("resource", "unknown")
        elif response.status_code == 422:
            raise SupabaseValidationError(error_message)
        else:
            raise SupabaseError(error_message, status_code=response.status_code) 