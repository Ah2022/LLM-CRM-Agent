"""
Tests for the LLM Customer Service Agent tools.

This module contains unit tests for the various tools used by the agent,
including the email summarizer, CRM entry generator, ticket router, and RAG tool.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.tools.summarizer import EmailSummarizer
from app.tools.crm_entry import CRMEntryGenerator
from app.tools.ticket_router import TicketRouter
from app.tools.rag_tool import RAGTool
from app.config import settings

class TestEmailSummarizer(unittest.TestCase):
    """Test cases for the EmailSummarizer tool."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the LLM to avoid actual API calls during tests
        self.llm_patcher = patch('app.tools.summarizer.ChatOpenAI')
        self.mock_llm = self.llm_patcher.start()
        
        # Create a mock response for the LLM
        mock_response = MagicMock()
        mock_response.content = """
TLDR: Customer is having login issues and needs help resetting their password.

Key points:
- Customer has been unable to login for two days
- They've tried resetting their password twice without success
- They're getting an "Invalid credentials" error

Action items:
- Verify customer's account status
- Assist with manual password reset
- Follow up to ensure they can access their account

Deadlines: Customer needs this resolved ASAP as they can't access their account.
"""
        self.mock_llm.return_value.invoke.return_value = mock_response
        
        # Create an instance of the summarizer for testing
        self.summarizer = EmailSummarizer(self.mock_llm.return_value)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.llm_patcher.stop()
    
    def test_summarize_email(self):
        """Test that the summarizer can summarize an email correctly."""
        # Test data
        email_data = {
            "subject": "Login Issues",
            "body": "Hello Support Team,\n\nI've been trying to log in to my account for the past two days but keep getting an 'Invalid credentials' error even though I'm sure my password is correct. I've tried resetting my password twice but still can't get in.\n\nCan you please help me resolve this issue? My account is associated with this email address.\n\nThank you,\nJohn Smith",
            "sender": "john.smith@example.com",
            "date": "2023-10-15T10:00:00Z",
            "attachments": []
        }
        
        # Call the method
        summary = self.summarizer.summarize_email(email_data)
        
        # Assertions
        self.assertIn("TLDR", summary)
        self.assertIn("Key points", summary)
        self.assertIn("Action items", summary)
        self.mock_llm.return_value.invoke.assert_called_once()

class TestCRMEntryGenerator(unittest.TestCase):
    """Test cases for the CRMEntryGenerator tool."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the LLM to avoid actual API calls during tests
        self.llm_patcher = patch('app.tools.crm_entry.ChatOpenAI')
        self.mock_llm = self.llm_patcher.start()
        
        # Create a mock response for the LLM
        mock_response = MagicMock()
        mock_response.content = """
{
  "customer_name": "John Smith",
  "interaction_type": "Email",
  "interaction_date": "2023-10-15T10:00:00Z",
  "summary": "Customer reported login issues with their account",
  "customer_needs": "Access to their account",
  "pain_points": "Unable to login despite multiple password reset attempts",
  "action_items": "Manually reset password and verify account status",
  "follow_up_required": "Yes",
  "follow_up_date": "2023-10-16",
  "priority": "High",
  "sentiment": "Negative",
  "products_discussed": "Customer Portal",
  "notes": "Customer has been a loyal user for 2 years and is frustrated by this issue"
}
"""
        self.mock_llm.return_value.invoke.return_value = mock_response
        
        # Create an instance of the generator for testing
        self.generator = CRMEntryGenerator(self.mock_llm.return_value)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.llm_patcher.stop()
    
    def test_create_crm_entry(self):
        """Test that the generator can create a CRM entry correctly."""
        # Test data
        interaction_data = {
            "customer_name": "John Smith",
            "interaction_details": "Customer emailed about login issues. They've been trying to log in for two days but keep getting an 'Invalid credentials' error despite multiple password reset attempts.",
            "additional_info": {
                "email_id": "email_12345",
                "customer_id": "CUST12345",
                "account_type": "Premium"
            }
        }
        
        # Call the method
        crm_entry = self.generator.create_crm_entry(interaction_data)
        
        # Assertions
        self.assertEqual(crm_entry["customer_name"], "John Smith")
        self.assertEqual(crm_entry["interaction_type"], "Email")
        self.assertEqual(crm_entry["priority"], "High")
        self.mock_llm.return_value.invoke.assert_called_once()

class TestTicketRouter(unittest.TestCase):
    """Test cases for the TicketRouter tool."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the LLM to avoid actual API calls during tests
        self.llm_patcher = patch('app.tools.ticket_router.ChatOpenAI')
        self.mock_llm = self.llm_patcher.start()
        
        # Create mock responses for the LLM
        self.categorization_response = MagicMock()
        self.categorization_response.content = """
{
  "category": "Technical",
  "priority": "High",
  "department": "Support",
  "estimated_response_time": "24 hours",
  "key_issues": ["Login issue", "Password reset not working"],
  "suggested_approach": "Verify account status and reset password manually"
}
"""
        
        self.routing_response = MagicMock()
        self.routing_response.content = """
{
  "department": "Technical Support",
  "priority": "Medium",
  "category": "Account",
  "intent": "Password reset assistance",
  "key_questions": ["How do I reset my password?"],
  "next_steps": "Provide password reset instructions or escalate to account specialist"
}
"""
        
        self.support_detection_response = MagicMock()
        self.support_detection_response.content = "Yes"
        
        # Create an instance of the router for testing
        self.router = TicketRouter(self.mock_llm.return_value)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.llm_patcher.stop()
    
    def test_categorize_ticket(self):
        """Test that the router can categorize a ticket correctly."""
        # Set up the mock response
        self.mock_llm.return_value.invoke.return_value = self.categorization_response
        
        # Test data
        ticket_data = {
            "title": "Login Issue",
            "description": "Cannot log in to my account despite multiple password reset attempts",
            "customer_id": "CUST12345"
        }
        
        # Call the method
        result = self.router.categorize_ticket(ticket_data)
        
        # Assertions
        self.assertEqual(result["category"], "Technical")
        self.assertEqual(result["priority"], "High")
        self.assertEqual(result["department"], "Support")
        self.mock_llm.return_value.invoke.assert_called_once()
    
    def test_route_query(self):
        """Test that the router can route a query correctly."""
        # Set up the mock response
        self.mock_llm.return_value.invoke.return_value = self.routing_response
        
        # Test data
        query_data = {
            "query": "How do I reset my password?",
            "customer_id": "CUST12345"
        }
        
        # Call the method
        result = self.router.route_query(query_data)
        
        # Assertions
        self.assertEqual(result["department"], "Technical Support")
        self.assertEqual(result["category"], "Account")
        self.assertEqual(result["intent"], "Password reset assistance")
        self.mock_llm.return_value.invoke.assert_called_once()
    
    def test_is_support_request(self):
        """Test that the router can detect support requests correctly."""
        # Set up the mock response
        self.mock_llm.return_value.invoke.return_value = self.support_detection_response
        
        # Test data
        subject = "Login Issue"
        message = "I can't log in to my account. Please help."
        
        # Call the method
        result = self.router.is_support_request(subject, message)
        
        # Assertions
        self.assertTrue(result)
        self.mock_llm.return_value.invoke.assert_called_once()

class TestRAGTool(unittest.TestCase):
    """Test cases for the RAGTool."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the LLM and embeddings to avoid actual API calls during tests
        self.llm_patcher = patch('app.tools.rag_tool.ChatOpenAI')
        self.embeddings_patcher = patch('app.tools.rag_tool.OpenAIEmbeddings')
        self.chroma_patcher = patch('app.tools.rag_tool.Chroma')
        
        self.mock_llm = self.llm_patcher.start()
        self.mock_embeddings = self.embeddings_patcher.start()
        self.mock_chroma = self.chroma_patcher.start()
        
        # Create a mock response for the LLM
        mock_response = MagicMock()
        mock_response.content = """
Based on the provided context, here's what I can tell you about resetting your password:

1. You can reset your password by clicking the "Forgot Password" link on the login page.
2. You will receive an email with a password reset link that is valid for 24 hours.
3. If you don't receive the email, check your spam folder or contact support.

This information comes from Document 1 in the context, which appears to be from the help documentation.
"""
        self.mock_llm.return_value.invoke.return_value = mock_response
        
        # Mock the vector store
        mock_vector_store = MagicMock()
        mock_vector_store._collection.count.return_value = 10
        
        # Create mock documents for similarity search
        mock_doc = MagicMock()
        mock_doc.page_content = "To reset your password, click the 'Forgot Password' link on the login page. You will receive an email with a reset link valid for 24 hours. If you don't receive the email, check your spam folder or contact support."
        mock_vector_store.similarity_search.return_value = [mock_doc]
        
        self.mock_chroma.return_value = mock_vector_store
        
        # Create an instance of the RAG tool for testing
        self.rag_tool = RAGTool(self.mock_llm.return_value)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.llm_patcher.stop()
        self.embeddings_patcher.stop()
        self.chroma_patcher.stop()
    
    def test_retrieve_information(self):
        """Test that the RAG tool can retrieve information correctly."""
        # Test data
        query_data = {
            "query": "How do I reset my password?",
            "max_results": 1
        }
        
        # Call the method
        result = self.rag_tool.retrieve_information(query_data)
        
        # Assertions
        self.assertIn("reset your password", result)
        self.assertIn("Forgot Password", result)
        self.mock_llm.return_value.invoke.assert_called_once()
        self.rag_tool.vector_store.similarity_search.assert_called_once_with("How do I reset my password?", k=1)

if __name__ == '__main__':
    unittest.main()