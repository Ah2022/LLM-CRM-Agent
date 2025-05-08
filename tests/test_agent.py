"""
Tests for the CustomerServiceAgent class.

This module contains unit tests for the CustomerServiceAgent class
to ensure it correctly handles various customer service tasks.
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
from app.config import settings

class TestCustomerServiceAgent(unittest.TestCase):
    """Test cases for the CustomerServiceAgent class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the LLM to avoid actual API calls during tests
        self.llm_patcher = patch('app.agent.ChatOpenAI')
        self.mock_llm = self.llm_patcher.start()
        
        # Mock the tools to avoid actual processing during tests
        self.email_summarizer_patcher = patch('app.tools.summarizer.EmailSummarizer')
        self.crm_generator_patcher = patch('app.tools.crm_entry.CRMEntryGenerator')
        self.ticket_router_patcher = patch('app.tools.ticket_router.TicketRouter')
        self.rag_tool_patcher = patch('app.tools.rag_tool.RAGTool')
        
        self.mock_email_summarizer = self.email_summarizer_patcher.start()
        self.mock_crm_generator = self.crm_generator_patcher.start()
        self.mock_ticket_router = self.ticket_router_patcher.start()
        self.mock_rag_tool = self.rag_tool_patcher.start()
        
        # Mock the services to avoid actual API calls during tests
        self.email_service_patcher = patch('app.services.email.EmailService')
        self.crm_service_patcher = patch('app.services.crm.CRMService')
        self.ticket_service_patcher = patch('app.services.tickets.TicketService')
        
        self.mock_email_service = self.email_service_patcher.start()
        self.mock_crm_service = self.crm_service_patcher.start()
        self.mock_ticket_service = self.ticket_service_patcher.start()
        
        # Mock the memory to avoid file operations during tests
        self.memory_patcher = patch('app.memory.AgentMemory')
        self.mock_memory = self.memory_patcher.start()
        
        # Create an instance of the agent for testing
        self.agent = CustomerServiceAgent()
        
        # Set up mock return values
        self.agent.email_summarizer.summarize_email.return_value = "Mock email summary"
        self.agent.ticket_router.categorize_ticket.return_value = {
            "category": "Technical",
            "priority": "High",
            "department": "Support",
            "estimated_response_time": "24 hours",
            "key_issues": ["Login issue", "Password reset not working"],
            "suggested_approach": "Verify account status and reset password manually"
        }
        self.agent.crm_generator.create_crm_entry.return_value = {
            "customer_name": "Test Customer",
            "interaction_type": "Email",
            "interaction_date": datetime.now().isoformat(),
            "summary": "Customer reported login issues",
            "action_items": ["Reset password", "Follow up in 24 hours"],
            "priority": "Medium"
        }
        self.agent.ticket_router.route_query.return_value = {
            "department": "Technical Support",
            "priority": "Medium",
            "category": "Account",
            "next_steps": "Escalate to account specialist"
        }
        self.agent.ticket_router.is_support_request.return_value = True
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.llm_patcher.stop()
        self.email_summarizer_patcher.stop()
        self.crm_generator_patcher.stop()
        self.ticket_router_patcher.stop()
        self.rag_tool_patcher.stop()
        self.email_service_patcher.stop()
        self.crm_service_patcher.stop()
        self.ticket_service_patcher.stop()
        self.memory_patcher.stop()
    
    def test_summarize_email(self):
        """Test that the agent can summarize an email correctly."""
        # Test data
        subject = "Test Subject"
        body = "Test Body"
        sender = "test@example.com"
        date = "2023-10-15T10:00:00Z"
        
        # Call the method
        summary = self.agent.summarize_email(subject, body, sender, date)
        
        # Assertions
        self.assertEqual(summary, "Mock email summary")
        self.agent.email_summarizer.summarize_email.assert_called_once()
        call_args = self.agent.email_summarizer.summarize_email.call_args[0][0]
        self.assertEqual(call_args["subject"], subject)
        self.assertEqual(call_args["body"], body)
        self.assertEqual(call_args["sender"], sender)
        self.assertEqual(call_args["date"], date)
    
    def test_categorize_ticket(self):
        """Test that the agent can categorize a ticket correctly."""
        # Test data
        title = "Login Issue"
        description = "Cannot log in to my account"
        customer_id = "CUST12345"
        
        # Call the method
        result = self.agent.categorize_ticket(title, description, customer_id)
        
        # Assertions
        self.assertEqual(result["category"], "Technical")
        self.assertEqual(result["priority"], "High")
        self.agent.ticket_router.categorize_ticket.assert_called_once()
        call_args = self.agent.ticket_router.categorize_ticket.call_args[0][0]
        self.assertEqual(call_args["title"], title)
        self.assertEqual(call_args["description"], description)
        self.assertEqual(call_args["customer_id"], customer_id)
    
    def test_create_crm_entry(self):
        """Test that the agent can create a CRM entry correctly."""
        # Test data
        customer_name = "Test Customer"
        interaction_details = "Customer reported login issues"
        additional_info = {"source": "email", "ticket_id": "TICKET123"}
        
        # Call the method
        result = self.agent.create_crm_entry(customer_name, interaction_details, additional_info)
        
        # Assertions
        self.assertEqual(result["customer_name"], "Test Customer")
        self.assertEqual(result["interaction_type"], "Email")
        self.agent.crm_generator.create_crm_entry.assert_called_once()
        call_args = self.agent.crm_generator.create_crm_entry.call_args[0][0]
        self.assertEqual(call_args["customer_name"], customer_name)
        self.assertEqual(call_args["interaction_details"], interaction_details)
        self.assertEqual(call_args["additional_info"], additional_info)
    
    def test_route_query(self):
        """Test that the agent can route a query correctly."""
        # Test data
        query = "How do I reset my password?"
        customer_id = "CUST12345"
        context = {"previous_tickets": ["TICKET123"]}
        
        # Call the method
        result = self.agent.route_query(query, customer_id, context)
        
        # Assertions
        self.assertEqual(result["department"], "Technical Support")
        self.assertEqual(result["category"], "Account")
        self.agent.ticket_router.route_query.assert_called_once()
        call_args = self.agent.ticket_router.route_query.call_args[0][0]
        self.assertEqual(call_args["query"], query)
        self.assertEqual(call_args["customer_id"], customer_id)
        self.assertEqual(call_args["context"], context)
    
    @patch('asyncio.run')
    def test_process_email_batch(self, mock_run):
        """Test that the agent can process a batch of emails correctly."""
        # Set up the mock email service to return test emails
        mock_emails = [
            {
                "id": "email_1",
                "subject": "Login Issue",
                "body": "I can't log in to my account",
                "sender": "customer@example.com",
                "date": datetime.now().isoformat(),
                "customer_id": "CUST12345"
            }
        ]
        self.agent.email_service.get_unprocessed_emails = MagicMock(return_value=mock_emails)
        self.agent.email_service.mark_as_processed = MagicMock(return_value=True)
        self.agent.ticket_service.create_ticket = MagicMock(return_value="TICKET123")
        self.agent.crm_service.create_entry = MagicMock(return_value="ENTRY123")
        
        # Call the method (which is async, so we need to handle that in the test)
        asyncio.run(self.agent.process_email_batch())
        
        # Assertions
        self.agent.email_service.get_unprocessed_emails.assert_called_once()
        self.agent.email_summarizer.summarize_email.assert_called_once()
        self.agent.ticket_router.is_support_request.assert_called_once()
        self.agent.ticket_router.categorize_ticket.assert_called_once()
        self.agent.ticket_service.create_ticket.assert_called_once()
        self.agent.crm_generator.create_crm_entry.assert_called_once()
        self.agent.crm_service.create_entry.assert_called_once()
        self.agent.email_service.mark_as_processed.assert_called_once_with("email_1")

if __name__ == '__main__':
    unittest.main()