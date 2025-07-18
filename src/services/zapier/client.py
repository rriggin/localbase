"""
Zapier Service Client
Professional Zapier integration for workflow automation.
"""

import requests
from typing import Dict, Any, List, Optional
import json

from ..base_service import BaseService

class ZapierService(BaseService):
    """
    Professional Zapier service client.
    
    Provides interfaces for triggering Zapier webhooks, batch processing,
    and workflow automation that can be used across multiple agents.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Zapier service.
        
        Args:
            config: Must contain webhook URLs and any auth tokens
        """
        super().__init__(config)
        
        self.webhook_urls = config.get('webhook_urls', {})
        self.default_timeout = config.get('timeout', 30)
    
    def trigger_webhook(self, webhook_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger a named Zapier webhook.
        
        Args:
            webhook_name: Name of the webhook to trigger
            data: Data to send to the webhook
            
        Returns:
            Response from Zapier webhook
        """
        if webhook_name not in self.webhook_urls:
            raise ValueError(f"Webhook '{webhook_name}' not configured")
        
        webhook_url = self.webhook_urls[webhook_name]
        
        response = requests.post(
            webhook_url,
            json=data,
            timeout=self.default_timeout
        )
        response.raise_for_status()
        
        return response.json() if response.content else {}
    
    def batch_process(self, webhook_name: str, data_list: List[Dict[str, Any]], batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Process data in batches through Zapier webhook.
        
        Args:
            webhook_name: Name of the webhook to trigger
            data_list: List of data items to process
            batch_size: Number of items per batch
            
        Returns:
            List of responses from batch processing
        """
        results = []
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            batch_data = {
                "batch": batch,
                "batch_number": i // batch_size + 1,
                "total_batches": (len(data_list) + batch_size - 1) // batch_size
            }
            
            result = self.trigger_webhook(webhook_name, batch_data)
            results.append(result)
        
        return results 