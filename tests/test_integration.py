"""
Integration tests for the LLM Customer Service Agent.

This module contains integration tests that verify the interaction between
different components of the system, such as the agent, tools, and services.
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock
import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent import CustomerServiceAgent
from app.tools.summarizer import EmailSummarizer
from app.tools.crm_entry import CRMEntryGenerator
from app.tools.ticket_router import TicketRouter
from app.services.email import EmailService
from app.services.crm import CRMService
from app.services.tickets import TicketService
from app.config import settings

class TestEmailProcessingWorkflow(unittest.TestCase):
    """Test the complete email processing workflow."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock all external dependencies
        self.patches = []
        
        # Mock LLM
        llm_patcher = patch('app.agent.ChatOpenAI')
        self.mock_llm = llm_patcher.start()
        self.patches.append(llm_patcher)
        
        # Mock services
        email_service_patcher = patch('app.services.email.EmailService', autospec=True)
        crm_service_patcher = patch('app.services.crm.CRMService', autospec=True)
        ticket_service_patcher = patch('app.services.tickets.TicketService', autospec=True)
        
        self.mock_email_service = email_service_patcher.start()
        self.mock_crm_service = crm_service_patcher.start()
        self.mock_ticket_service = ticket_service_patcher.start()
        
        self.patches.extend([email_service_patcher, crm_service_patcher, ticket_service_patcher])
        
        # Mock memory
        memory_patcher = patch('app.memory.AgentMemory')
        self.mock_memory = memory_patcher.start()
        self.patches.append(memory_patcher)
        
        # Create test data
        self.test_email = {
            "id": "email_12345",
            "subject": "Login Issue",
            "body": "I can't log in to my account. I've tried resetting my password but it's not working.",
            "sender": "customer@example.com",
            "date": datetime.now().isoformat(),
            "customer_id": "CUST12345"
        }
        
        # Set up mock responses
        self.mock_email_service.return_value.get_unprocessed_emails.return_value = [self.test_email]
        self.mock_email_service.return_value.mark_as_processed.return_value = True
        
        self.mock_ticket_service.return_value.create_ticket.return_value = "TICKET12345"
        
        self.mock_crm_service.return_value.create_entry.return_value = "ENTRY12345"
        
        # Create real instances of the tools with mocked LLMs
        self.email_summarizer = EmailSummarizer(self.mock_llm.return_value)
        self.crm_generator = CRMEntryGenerator(self.mock_llm.return_value)
        self.ticket_router = TicketRouter(self.mock_llm.return_value)
        
        # Mock the tool methods
        self.email_summarizer.summarize_email = MagicMock(return_value="Email summary: Customer can't log in")
        self.ticket_router.is_support_request = MagicMock(return_value=True)
        self.ticket_router.categorize_ticket = MagicMock(return_value={
            "category": "Technical",
            "priority": "High",
            "department": "Support",
            "estimated_response_time": "24 hours"
        })
        self.crm_generator.create_crm_entry = MagicMock(return_value={
            "customer_name": "customer@example.com",
            "interaction_type": "Email",
            "summary": "Customer reported login issues"
        })
        
        # Create the agent with our mocked dependencies
        self.agent = CustomerServiceAgent()
        
        # Replace the agent's tools and services with our mocked versions
        self.agent.email_summarizer = self.email_summarizer
        self.agent.crm_generator = self.crm_generator
        self.agent.ticket_router = self.ticket_router
        self.agent.email_service = self.mock_email_service.return_value
        self.agent.crm_service = self.mock_crm_service.return_value
        self.agent.ticket_service = self.mock_ticket_service.return_value
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        for patcher in self.patches:
            patcher.stop()
    
    def test_email_to_ticket_workflow(self):
        """Test the complete workflow from email to ticket and CRM entry."""
        # Run the email batch processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.agent.process_email_batch())
        finally:
            loop.close()
        
        # Verify that all the expected methods were called
        self.agent.email_service.get_unprocessed_emails.assert_called_once()
        
        self.agent.email_summarizer.summarize_email.assert_called_once()
        call_args = self.agent.email_summarizer.summarize_email.call_args[0][0]
        self.assertEqual(call_args["subject"], self.test_email["subject"])
        self.assertEqual(call_args["body"], self.test_email["body"])
        
        self.agent.ticket_router.is_support_request.assert_called_once_with(
            self.test_email["subject"], self.test_email["body"]
        )
        
        self.agent.ticket_router.categorize_ticket.assert_called_once()
        call_args = self.agent.ticket_router.categorize_ticket.call_args[0][0]
        self.assertEqual(call_args["title"], self.test_email["subject"])
        self.assertEqual(call_args["description"], self.test_email["body"])
        
        self.agent.ticket_service.create_ticket.assert_called_once()
        call_args, call_kwargs = self.agent.ticket_service.create_ticket.call_args
        self.assertEqual(call_kwargs["title"], self.test_email["subject"])
        self.assertEqual(call_kwargs["description"], self.test_email["body"])
        self.assertEqual(call_kwargs["category"], "Technical")
        self.assertEqual(call_kwargs["priority"], "High")
        
        self.agent.crm_generator.create_crm_entry.assert_called_once()
        call_args = self.agent.crm_generator.create_crm_entry.call_args[0][0]
        self.assertEqual(call_args["customer_name"], self.test_email["sender"])
        self.assertIn("Email:", call_args["interaction_details"])
        self.assertIn(self.test_email["subject"], call_args["interaction_details"])
        
        self.agent.crm_service.create_entry.assert_called_once()
        
        self.agent.email_service.mark_as_processed.assert_called_once_with(self.test_email["id"])

class TestAPIEndpoints(unittest.TestCase):
    """Test the API endpoints with mocked agent."""
    
    @patch('app.main.CustomerServiceAgent')
    def setUp(self, mock_agent_class):
        """Set up test fixtures before each test method."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        # Create a mock agent
        self.mock_agent = mock_agent_class.return_value
        
        # Set up mock responses for agent methods
        self.mock_agent.summarize_email.return_value = "Email summary: Customer can't log in"
        self.mock_agent.categorize_ticket.return_value = {
            "category": "Technical",
            "priority": "High",
            "department": "Support",
            "estimated_response_time": "24 hours"
        }
        self.mock_agent.create_crm_entry.return_value = {
            "customer_name": "Test Customer",
            "interaction_type": "Email",
            "summary": "Customer reported login issues"
        }
        self.mock_agent.route_query.return_value = {
            "department": "Technical Support",
            "priority": "Medium",
            "category": "Account",
            "next_steps": "Provide password reset instructions"
        }
        
        # Create a test client
        self.client = TestClient(app)
    
    def test_summarize_email_endpoint(self):
        """Test the /summarize-email endpoint."""
        # Test data
        email_data = {
            "subject": "Login Issue",
            "body": "I can't log in to my account",
            "sender": "customer@example.com",
            "date": "2023-10-15T10:00:00Z"
        }
        
        # Make the request
        response = self.client.post("/summarize-email", json=email_data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"summary": "Email summary: Customer can't log in"})
        self.mock_agent.summarize_email.assert_called_once_with(
            subject=email_data["subject"],
            body=email_data["body"],
            sender=email_data["sender"],
            date=email_data["date"],
            attachments=None
        )
    
    def test_categorize_ticket_endpoint(self):
        """Test the /categorize-ticket endpoint."""
        # Test data
        ticket_data = {
            "title": "Login Issue",
            "description": "I can't log in to my account",
            "customer_id": "CUST12345"
        }
        
        # Make the request
        response = self.client.post("/categorize-ticket", json=ticket_data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "Technical")
        self.assertEqual(response.json()["priority"], "High")
        self.mock_agent.categorize_ticket.assert_called_once_with(
            title=ticket_data["title"],
            description=ticket_data["description"],
            customer_id=ticket_data["customer_id"],
            priority=None,
            category=None
        )
    
    def test_create_crm_entry_endpoint(self):
        """Test the /create-crm-entry endpoint."""
        # Test data
        entry_data = {
            "customer_name": "Test Customer",
            "interaction_details": "Customer reported login issues",
            "additional_info": {"source": "email"}
        }
        
        # Make the request
        response = self.client.post("/create-crm-entry", json=entry_data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["crm_entry"]["customer_name"], "Test Customer")
        self.mock_agent.create_crm_entry.assert_called_once_with(
            customer_name=entry_data["customer_name"],
            interaction_details=entry_data["interaction_details"],
            additional_info=entry_data["additional_info"]
        )
    
    def test_route_query_endpoint(self):
        """Test the /route-query endpoint."""
        # Test data
        query_data = {
            "query": "How do I reset my password?",
            "customer_id": "CUST12345"
        }
        
        # Make the request
        response = self.client.post("/route-query", json=query_data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["department"], "Technical Support")
        self.assertEqual(response.json()["category"], "Account")
        self.mock_agent.route_query.assert_called_once_with(
            query=query_data["query"],
            customer_id=query_data["customer_id"],
            context=None
        )

if __name__ == '__main__':
    unittest.main()