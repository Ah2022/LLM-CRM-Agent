"""
LangChain Agent for Customer Service Automation

This module implements a LangChain-based agent that can perform various
customer service tasks using LLMs and specialized tools.
"""

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema.messages import SystemMessage
from langchain.chat_models import ChatOpenAI
from typing import List, Dict, Any, Optional
import logging

from app.tools.summarizer import EmailSummarizer
from app.tools.crm_entry import CRMEntryGenerator
from app.tools.ticket_router import TicketRouter
from app.tools.rag_tool import RAGTool
from app.services.email import EmailService
from app.services.crm import CRMService
from app.services.tickets import TicketService
from app.config import settings
from app.memory import AgentMemory

logger = logging.getLogger(__name__)

class CustomerServiceAgent:
    """
    An LLM-powered agent for automating customer service tasks.
    
    This agent can:
    - Summarize emails
    - Categorize and prioritize support tickets
    - Generate CRM entries
    - Route customer queries to appropriate departments
    """
    
    def __init__(self):
        """Initialize the customer service agent with its tools and LLM."""
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize tools
        self.email_summarizer = EmailSummarizer(self.llm)
        self.crm_generator = CRMEntryGenerator(self.llm)
        self.ticket_router = TicketRouter(self.llm)
        self.rag_tool = RAGTool(self.llm)
        
        # Initialize services
        self.email_service = EmailService()
        self.crm_service = CRMService()
        self.ticket_service = TicketService()
        
        # Set up tools for the agent
        self.tools = [
            self.email_summarizer,
            self.crm_generator,
            self.ticket_router,
            self.rag_tool
        ]
        
        # Set up agent memory
        self.memory = AgentMemory()
        
        # Set up the agent with a system prompt
        system_prompt = f"""You are a professional customer service AI assistant.
Your job is to help with various customer service tasks including:
1. Summarizing emails into concise, actionable points
2. Categorizing and prioritizing support tickets
3. Creating detailed CRM entries from customer interactions
4. Routing customer queries to the appropriate department

Always be professional, accurate, and helpful. When summarizing or categorizing,
focus on extracting the key information and intent. When creating CRM entries,
be comprehensive but concise.
"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=settings.AGENT_VERBOSE,
            handle_parsing_errors=True
        )
        
        logger.info("Customer Service Agent initialized successfully")
    
    def summarize_email(self, subject: str, body: str, sender: str, 
                        date: str, attachments: Optional[List[str]] = None) -> str:
        """
        Summarize an email into key points and action items.
        
        Args:
            subject: Email subject line
            body: Email body text
            sender: Email sender
            date: Email date
            attachments: List of attachment names (optional)
            
        Returns:
            A concise summary of the email
        """
        logger.info(f"Summarizing email from {sender} with subject: {subject}")
        
        # Prepare the input for the email summarizer
        email_data = {
            "subject": subject,
            "body": body,
            "sender": sender,
            "date": date,
            "attachments": attachments or []
        }
        
        # Use the email summarizer tool directly
        summary = self.email_summarizer.summarize_email(email_data)
        
        logger.info(f"Email summarized successfully")
        return summary
    
    def categorize_ticket(self, title: str, description: str, 
                         customer_id: Optional[str] = None,
                         priority: Optional[str] = None,
                         category: Optional[str] = None) -> Dict[str, Any]:
        """
        Categorize and prioritize a support ticket.
        
        Args:
            title: Ticket title
            description: Ticket description
            customer_id: Customer ID (optional)
            priority: Suggested priority (optional)
            category: Suggested category (optional)
            
        Returns:
            Dict with categorization results including department, priority, and estimated response time
        """
        logger.info(f"Categorizing ticket: {title}")
        
        # Prepare the ticket data
        ticket_data = {
            "title": title,
            "description": description,
            "customer_id": customer_id,
            "priority": priority,
            "category": category
        }
        
        # Use the ticket router tool directly
        result = self.ticket_router.categorize_ticket(ticket_data)
        
        logger.info(f"Ticket categorized as {result.get('category')} with {result.get('priority')} priority")
        return result
    
    def create_crm_entry(self, customer_name: str, interaction_details: str,
                        additional_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a structured CRM entry from customer interaction details.
        
        Args:
            customer_name: Name of the customer
            interaction_details: Details of the customer interaction
            additional_info: Additional context or information (optional)
            
        Returns:
            A structured CRM entry
        """
        logger.info(f"Creating CRM entry for customer: {customer_name}")
        
        # Prepare the interaction data
        interaction_data = {
            "customer_name": customer_name,
            "interaction_details": interaction_details,
            "additional_info": additional_info or {}
        }
        
        # Use the CRM entry generator tool directly
        crm_entry = self.crm_generator.create_crm_entry(interaction_data)
        
        logger.info(f"CRM entry created successfully")
        return crm_entry
    
    def route_query(self, query: str, customer_id: Optional[str] = None,
                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route a customer query to the appropriate department.
        
        Args:
            query: The customer's query text
            customer_id: Customer ID for context (optional)
            context: Additional context information (optional)
            
        Returns:
            Routing information including department, priority, and next steps
        """
        logger.info(f"Routing customer query: {query[:50]}...")
        
        # Prepare the query data
        query_data = {
            "query": query,
            "customer_id": customer_id,
            "context": context or {}
        }
        
        # Use the ticket router tool for routing
        routing = self.ticket_router.route_query(query_data)
        
        logger.info(f"Query routed to {routing.get('department')}")
        return routing
    
    async def process_email_batch(self):
        """
        Process a batch of emails from the email service.
        
        This method fetches unprocessed emails, summarizes them,
        and takes appropriate actions based on email content.
        """
        logger.info("Starting batch email processing")
        
        # Fetch unprocessed emails
        emails = await self.email_service.get_unprocessed_emails()
        
        for email in emails:
            try:
                # Summarize the email
                summary = self.summarize_email(
                    subject=email["subject"],
                    body=email["body"],
                    sender=email["sender"],
                    date=email["date"],
                    attachments=email.get("attachments")
                )
                
                # Determine if this is a support request
                if self.ticket_router.is_support_request(email["subject"], email["body"]):
                    # Create a support ticket
                    ticket_data = self.categorize_ticket(
                        title=email["subject"],
                        description=email["body"],
                        customer_id=email.get("customer_id")
                    )
                    
                    # Submit the ticket to the ticket service
                    await self.ticket_service.create_ticket(
                        title=email["subject"],
                        description=email["body"],
                        category=ticket_data["category"],
                        priority=ticket_data["priority"],
                        customer_id=email.get("customer_id")
                    )
                
                # Create a CRM entry for this interaction
                crm_entry = self.create_crm_entry(
                    customer_name=email["sender"],
                    interaction_details=f"Email: {email['subject']}\n\nSummary: {summary}",
                    additional_info={"email_id": email["id"]}
                )
                
                # Submit the CRM entry
                await self.crm_service.create_entry(crm_entry)
                
                # Mark the email as processed
                await self.email_service.mark_as_processed(email["id"])
                
            except Exception as e:
                logger.error(f"Error processing email {email.get('id')}: {str(e)}")
        
        logger.info(f"Batch email processing completed. Processed {len(emails)} emails")