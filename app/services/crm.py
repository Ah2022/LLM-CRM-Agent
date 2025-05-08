"""
CRM Service Integration

This module provides integration with CRM systems like Salesforce and HubSpot
for creating and retrieving customer records.
"""

import logging
import os
import json
from typing import List, Dict, Any, Optional
import aiohttp
import asyncio
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class CRMService:
    """
    Service for interacting with CRM systems.
    
    This service provides methods for creating and retrieving customer records,
    logging interactions, and managing customer data.
    """
    
    def __init__(self):
        """Initialize the CRM service based on configuration."""
        self.service_type = settings.CRM_SERVICE_TYPE.lower()
        self.api_key = settings.CRM_API_KEY
        self.instance_url = settings.CRM_INSTANCE_URL
        self.username = settings.CRM_USERNAME
        self.password = settings.CRM_PASSWORD
        
        # Initialize service-specific clients
        if self.service_type == "salesforce":
            self._init_salesforce()
        elif self.service_type == "hubspot":
            self._init_hubspot()
        else:
            logger.warning(f"Unsupported CRM service type: {self.service_type}. Using mock implementation.")
        
        logger.info(f"CRM service initialized with type: {self.service_type}")
    
    def _init_salesforce(self):
        """Initialize Salesforce API client."""
        try:
            # In a real implementation, this would use the Salesforce API client
            # For this example, we'll use a mock implementation
            logger.info("Salesforce API client initialized")
        except Exception as e:
            logger.error(f"Error initializing Salesforce API client: {str(e)}")
    
    def _init_hubspot(self):
        """Initialize HubSpot API client."""
        try:
            # In a real implementation, this would use the HubSpot API client
            # For this example, we'll use a mock implementation
            logger.info("HubSpot API client initialized")
        except Exception as e:
            logger.error(f"Error initializing HubSpot API client: {str(e)}")
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a customer record by ID.
        
        Args:
            customer_id: The ID of the customer to retrieve
            
        Returns:
            A dictionary containing customer details, or None if not found
        """
        try:
            # In a real implementation, this would call the appropriate API
            # For this example, we'll return mock data
            
            # Simulate API delay
            await asyncio.sleep(0.3)
            
            # Generate mock customer data based on ID
            if customer_id == "CUST12345":
                return {
                    "id": "CUST12345",
                    "name": "John Smith",
                    "email": "john.smith@example.com",
                    "phone": "555-123-4567",
                    "company": "ABC Corp",
                    "status": "Active",
                    "plan": "Enterprise",
                    "created_at": "2022-01-15T10:30:00Z",
                    "last_contact": "2023-09-28T14:45:00Z",
                    "notes": "Frequent support requests about login issues"
                }
            elif customer_id == "CUST67890":
                return {
                    "id": "CUST67890",
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@example.com",
                    "phone": "555-987-6543",
                    "company": "XYZ Inc",
                    "status": "Active",
                    "plan": "Professional",
                    "created_at": "2022-03-22T09:15:00Z",
                    "last_contact": "2023-10-10T11:20:00Z",
                    "notes": "Recently upgraded from Basic plan"
                }
            elif customer_id == "CUST24680":
                return {
                    "id": "CUST24680",
                    "name": "Michael Chen",
                    "email": "michael.chen@example.com",
                    "phone": "555-246-8024",
                    "company": "Tech Solutions LLC",
                    "status": "Active",
                    "plan": "Professional",
                    "created_at": "2022-05-10T14:00:00Z",
                    "last_contact": "2023-10-05T16:30:00Z",
                    "notes": "Interested in API integration features"
                }
            elif customer_id == "CUST13579":
                return {
                    "id": "CUST13579",
                    "name": "David Wilson",
                    "email": "david.wilson@acmecorp.com",
                    "phone": "555-135-7913",
                    "company": "Acme Corporation",
                    "status": "Prospect",
                    "plan": None,
                    "created_at": "2023-09-15T10:00:00Z",
                    "last_contact": "2023-10-08T15:45:00Z",
                    "notes": "In sales pipeline, demo provided on Oct 5"
                }
            else:
                return None
            
        except Exception as e:
            logger.error(f"Error retrieving customer {customer_id}: {str(e)}")
            return None
    
    async def search_customers(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for customers based on a query string.
        
        Args:
            query: The search query (name, email, company, etc.)
            
        Returns:
            A list of matching customer records
        """
        try:
            # In a real implementation, this would call the appropriate API
            # For this example, we'll return mock data
            
            # Simulate API delay
            await asyncio.sleep(0.5)
            
            # Return mock results based on query
            results = []
            
            # Simple mock implementation that checks if query is in any of the mock customer fields
            mock_customers = [
                {
                    "id": "CUST12345",
                    "name": "John Smith",
                    "email": "john.smith@example.com",
                    "company": "ABC Corp"
                },
                {
                    "id": "CUST67890",
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@example.com",
                    "company": "XYZ Inc"
                },
                {
                    "id": "CUST24680",
                    "name": "Michael Chen",
                    "email": "michael.chen@example.com",
                    "company": "Tech Solutions LLC"
                },
                {
                    "id": "CUST13579",
                    "name": "David Wilson",
                    "email": "david.wilson@acmecorp.com",
                    "company": "Acme Corporation"
                }
            ]
            
            query = query.lower()
            for customer in mock_customers:
                if (query in customer["name"].lower() or 
                    query in customer["email"].lower() or 
                    query in customer["company"].lower()):
                    results.append(customer)
            
            logger.info(f"Found {len(results)} customers matching query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching customers with query '{query}': {str(e)}")
            return []
    
    async def create_entry(self, entry_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new CRM entry (interaction, note, activity, etc.).
        
        Args:
            entry_data: Dictionary containing the entry data
            
        Returns:
            The ID of the created entry, or None if creation failed
        """
        try:
            # In a real implementation, this would call the appropriate API
            # For this example, we'll simulate success
            
            # Simulate API delay
            await asyncio.sleep(0.4)
            
            # Generate a mock entry ID
            entry_id = f"ENTRY_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            logger.info(f"Created CRM entry: {entry_id}")
            return entry_id
            
        except Exception as e:
            logger.error(f"Error creating CRM entry: {str(e)}")
            return None
    
    async def update_customer(self, customer_id: str, 
                             update_data: Dict[str, Any]) -> bool:
        """
        Update a customer record.
        
        Args:
            customer_id: The ID of the customer to update
            update_data: Dictionary containing the fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would call the appropriate API
            # For this example, we'll simulate success
            
            # Simulate API delay
            await asyncio.sleep(0.3)
            
            logger.info(f"Updated customer {customer_id} with data: {json.dumps(update_data)}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating customer {customer_id}: {str(e)}")
            return False
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new customer record.
        
        Args:
            customer_data: Dictionary containing the customer data
            
        Returns:
            The ID of the created customer, or None if creation failed
        """
        try:
            # In a real implementation, this would call the appropriate API
            # For this example, we'll simulate success
            
            # Simulate API delay
            await asyncio.sleep(0.5)
            
            # Generate a mock customer ID
            customer_id = f"CUST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            logger.info(f"Created customer: {customer_id}")
            return customer_id
            
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return None
    
    async def get_recent_interactions(self, customer_id: str, 
                                     limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve recent interactions for a customer.
        
        Args:
            customer_id: The ID of the customer
            limit: Maximum number of interactions to retrieve
            
        Returns:
            A list of recent interactions
        """
        try:
            # In a real implementation, this would call the appropriate API
            # For this example, we'll return mock data
            
            # Simulate API delay
            await asyncio.sleep(0.3)
            
            # Generate mock interactions
            interactions = []
            for i in range(min(3, limit)):  # Simulate up to 3 interactions or limit, whichever is smaller
                interaction_id = f"INT_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Create different types of mock interactions
                if i == 0:
                    interactions.append({
                        "id": interaction_id,
                        "type": "Email",
                        "subject": "Product inquiry",
                        "description": "Customer asked about product features and pricing",
                        "date": (datetime.now() - asyncio.timedelta(days=i*3)).isoformat(),
                        "agent": "Alex Johnson"
                    })
                elif i == 1:
                    interactions.append({
                        "id": interaction_id,
                        "type": "Support Ticket",
                        "subject": "Login issue",
                        "description": "Customer reported difficulty logging in. Issue resolved by resetting account.",
                        "date": (datetime.now() - asyncio.timedelta(days=i*3)).isoformat(),
                        "agent": "Maria Garcia"
                    })
                else:
                    interactions.append({
                        "id": interaction_id,
                        "type": "Call",
                        "subject": "Follow-up call",
                        "description": "Followed up on recent purchase. Customer is satisfied with the product.",
                        "date": (datetime.now() - asyncio.timedelta(days=i*3)).isoformat(),
                        "agent": "James Wilson"
                    })
            
            logger.info(f"Retrieved {len(interactions)} recent interactions for customer {customer_id}")
            return interactions
            
        except Exception as e:
            logger.error(f"Error retrieving interactions for customer {customer_id}: {str(e)}")
            return []