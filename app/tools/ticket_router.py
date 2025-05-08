"""
Ticket Router Tool

This module provides a tool for categorizing, prioritizing, and routing
support tickets using LLMs.
"""

from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
import logging
import json

from app.config import settings

logger = logging.getLogger(__name__)

class TicketInput(BaseModel):
    """Input schema for ticket categorization."""
    title: str = Field(..., description="The ticket title")
    description: str = Field(..., description="The ticket description")
    customer_id: Optional[str] = Field(None, description="The customer ID")
    priority: Optional[str] = Field(None, description="Suggested priority")
    category: Optional[str] = Field(None, description="Suggested category")

class QueryInput(BaseModel):
    """Input schema for query routing."""
    query: str = Field(..., description="The customer query text")
    customer_id: Optional[str] = Field(None, description="The customer ID")
    context: Optional[Dict[str, Any]] = Field({}, description="Additional context information")

class TicketRouter(BaseTool):
    """
    A tool for categorizing, prioritizing, and routing support tickets.
    
    This tool uses an LLM to analyze support tickets and customer queries,
    determine their category and priority, and route them to the appropriate
    department.
    """
    
    name = "ticket_router"
    description = "Categorizes, prioritizes, and routes support tickets and customer queries"
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """Initialize the ticket router with an optional LLM."""
        super().__init__()
        self.llm = llm or ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.1,  # Lower temperature for more consistent categorization
            api_key=settings.OPENAI_API_KEY
        )
        
        # Define available departments, priorities, and categories from settings
        self.departments = settings.DEPARTMENTS
        self.priorities = settings.TICKET_PRIORITIES
        self.categories = settings.TICKET_CATEGORIES
        
        # Create the ticket categorization prompt template
        self.categorization_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are an expert support ticket analyst for a customer service team.
Your task is to analyze support tickets and categorize them appropriately.

For each ticket, determine:
1. Category: Select the most appropriate category from: {', '.join(self.categories)}
2. Priority: Assign a priority level from: {', '.join(self.priorities)}
3. Department: Route to the appropriate department from: {', '.join(self.departments)}
4. Estimated Response Time: Provide an estimated time to respond based on the priority
5. Key Issues: Identify the main issues or questions in the ticket (2-3 bullet points)
6. Suggested Approach: Briefly suggest how to handle this ticket

Format your response as a JSON object with these fields. Be objective and consistent in your categorization.
Base your analysis solely on the content of the ticket, not on assumptions.
"""),
            HumanMessage(content="""Please categorize the following support ticket:

Title: {title}
Description: {description}
Customer ID: {customer_id}
Suggested Priority: {priority}
Suggested Category: {category}
""")
        ])
        
        # Create the query routing prompt template
        self.routing_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are an expert customer query router for a customer service team.
Your task is to analyze customer queries and route them to the appropriate department.

For each query, determine:
1. Department: Route to the appropriate department from: {', '.join(self.departments)}
2. Priority: Assign a priority level from: {', '.join(self.priorities)}
3. Category: Select the most appropriate category from: {', '.join(self.categories)}
4. Intent: Identify the primary customer intent or need
5. Key Questions: Extract the main questions or requests
6. Next Steps: Suggest the next steps for handling this query

Format your response as a JSON object with these fields. Be objective and consistent in your routing.
Base your analysis solely on the content of the query, not on assumptions.
"""),
            HumanMessage(content="""Please route the following customer query:

Query: {query}
Customer ID: {customer_id}
Additional Context: {context}
""")
        ])
        
        # Create the support request detection prompt
        self.support_detection_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert at identifying support requests in customer communications.
Your task is to determine if an email or message contains a support request that requires a ticket to be created.

A support request typically:
1. Describes a problem, issue, or challenge the customer is facing
2. Asks for help or assistance with a product or service
3. Reports a bug, error, or malfunction
4. Requests a feature or enhancement
5. Expresses dissatisfaction or frustration

Respond with "Yes" if the message contains a support request, or "No" if it does not.
"""),
            HumanMessage(content="""Please determine if the following message contains a support request:

Subject: {subject}
Message: {message}
""")
        ])
        
        logger.info("Ticket router tool initialized")
    
    def _run_categorization(self, title: str, description: str, 
                           customer_id: Optional[str] = None,
                           priority: Optional[str] = None,
                           category: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the ticket categorization.
        
        Args:
            title: The ticket title
            description: The ticket description
            customer_id: The customer ID (optional)
            priority: Suggested priority (optional)
            category: Suggested category (optional)
            
        Returns:
            A dictionary with categorization results
        """
        try:
            # Format the prompt with ticket details
            formatted_prompt = self.categorization_prompt.format_messages(
                title=title,
                description=description,
                customer_id=customer_id or "N/A",
                priority=priority or "Not specified",
                category=category or "Not specified"
            )
            
            # Get the categorization from the LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Parse the JSON response
            try:
                # Try to extract JSON from the response
                content = response.content
                
                # Check if the response is already valid JSON
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    # If not, try to extract JSON from the text
                    import re
                    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        result = json.loads(json_str)
                    else:
                        # If no JSON block found, assume the whole response is JSON with possible text around it
                        # Find the first { and the last }
                        start_idx = content.find('{')
                        end_idx = content.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            json_str = content[start_idx:end_idx+1]
                            result = json.loads(json_str)
                        else:
                            raise ValueError("Could not extract valid JSON from the response")
                
                logger.info(f"Successfully categorized ticket: {title}")
                return result
                
            except Exception as json_error:
                logger.error(f"Error parsing ticket categorization JSON: {str(json_error)}")
                # If JSON parsing fails, return a basic structure with the raw text
                return {
                    "title": title,
                    "category": category or "Unknown",
                    "priority": priority or "Medium",
                    "department": "Support",
                    "raw_response": response.content,
                    "error": "Failed to parse structured categorization"
                }
            
        except Exception as e:
            error_msg = f"Error categorizing ticket: {str(e)}"
            logger.error(error_msg)
            return {
                "title": title,
                "category": category or "Unknown",
                "priority": priority or "Medium",
                "department": "Support",
                "error": error_msg
            }
    
    def _run_routing(self, query: str, customer_id: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the query routing.
        
        Args:
            query: The customer query text
            customer_id: The customer ID (optional)
            context: Additional context information (optional)
            
        Returns:
            A dictionary with routing results
        """
        try:
            # Format context for display
            context_str = "None"
            if context and len(context) > 0:
                context_str = json.dumps(context, indent=2)
            
            # Format the prompt with query details
            formatted_prompt = self.routing_prompt.format_messages(
                query=query,
                customer_id=customer_id or "N/A",
                context=context_str
            )
            
            # Get the routing from the LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Parse the JSON response
            try:
                # Try to extract JSON from the response
                content = response.content
                
                # Check if the response is already valid JSON
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    # If not, try to extract JSON from the text
                    import re
                    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        result = json.loads(json_str)
                    else:
                        # If no JSON block found, assume the whole response is JSON with possible text around it
                        # Find the first { and the last }
                        start_idx = content.find('{')
                        end_idx = content.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            json_str = content[start_idx:end_idx+1]
                            result = json.loads(json_str)
                        else:
                            raise ValueError("Could not extract valid JSON from the response")
                
                logger.info(f"Successfully routed customer query")
                return result
                
            except Exception as json_error:
                logger.error(f"Error parsing query routing JSON: {str(json_error)}")
                # If JSON parsing fails, return a basic structure with the raw text
                return {
                    "department": "Support",
                    "priority": "Medium",
                    "category": "General",
                    "raw_response": response.content,
                    "error": "Failed to parse structured routing"
                }
            
        except Exception as e:
            error_msg = f"Error routing query: {str(e)}"
            logger.error(error_msg)
            return {
                "department": "Support",
                "priority": "Medium",
                "category": "General",
                "error": error_msg
            }
    
    def is_support_request(self, subject: str, message: str) -> bool:
        """
        Determine if a message contains a support request.
        
        Args:
            subject: The message subject
            message: The message body
            
        Returns:
            True if the message contains a support request, False otherwise
        """
        try:
            # Format the prompt with message details
            formatted_prompt = self.support_detection_prompt.format_messages(
                subject=subject,
                message=message
            )
            
            # Get the detection result from the LLM
            response = self.llm.invoke(formatted_prompt)
            content = response.content.strip().lower()
            
            # Check if the response indicates a support request
            is_support = "yes" in content and not "no" in content[:3]
            
            logger.info(f"Support request detection: {is_support} for subject: {subject}")
            return is_support
            
        except Exception as e:
            logger.error(f"Error detecting support request: {str(e)}")
            # Default to treating it as a support request if detection fails
            return True
    
    def categorize_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize a support ticket using the provided ticket data.
        
        Args:
            ticket_data: Dictionary containing ticket details
            
        Returns:
            A dictionary with categorization results
        """
        return self._run_categorization(
            title=ticket_data["title"],
            description=ticket_data["description"],
            customer_id=ticket_data.get("customer_id"),
            priority=ticket_data.get("priority"),
            category=ticket_data.get("category")
        )
    
    def route_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a customer query using the provided query data.
        
        Args:
            query_data: Dictionary containing query details
            
        Returns:
            A dictionary with routing results
        """
        return self._run_routing(
            query=query_data["query"],
            customer_id=query_data.get("customer_id"),
            context=query_data.get("context", {})
        )