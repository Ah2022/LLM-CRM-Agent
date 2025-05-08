"""
CRM Entry Generator Tool

This module provides a tool for generating structured CRM entries from
customer interaction details using LLMs.
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

class CRMEntryInput(BaseModel):
    """Input schema for the CRM entry generator."""
    customer_name: str = Field(..., description="The name of the customer")
    interaction_details: str = Field(..., description="Details of the customer interaction")
    additional_info: Optional[Dict[str, Any]] = Field({}, description="Additional context or information")

class CRMEntryGenerator(BaseTool):
    """
    A tool for generating structured CRM entries from customer interactions.
    
    This tool uses an LLM to extract relevant information from customer
    interactions and format it into structured CRM entries.
    """
    
    name = "crm_entry_generator"
    description = "Generates structured CRM entries from customer interaction details"
    args_schema: Type[BaseModel] = CRMEntryInput
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """Initialize the CRM entry generator with an optional LLM."""
        super().__init__()
        self.llm = llm or ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.2,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Create the CRM entry generation prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert CRM specialist who creates detailed, structured entries from customer interactions.
Your task is to analyze customer interaction details and generate a comprehensive CRM entry that captures all relevant information.

For each interaction, create a structured CRM entry with the following fields:
1. Customer Name: The name of the customer
2. Interaction Type: The type of interaction (email, call, chat, etc.)
3. Interaction Date: The date of the interaction (extract from context if available)
4. Summary: A brief summary of the interaction
5. Customer Needs: What the customer is looking for or needs
6. Pain Points: Any issues or challenges the customer is facing
7. Action Items: Tasks that need to be completed as a result of this interaction
8. Follow-up Required: Whether follow-up is needed (Yes/No)
9. Follow-up Date: When to follow up (if applicable)
10. Priority: The priority level of this interaction (Low, Medium, High)
11. Sentiment: The customer's sentiment (Positive, Neutral, Negative)
12. Products/Services Discussed: Any products or services mentioned in the interaction
13. Notes: Any additional relevant information

Format your response as a JSON object with these fields. Be comprehensive but concise.
Extract as much information as possible from the provided details, but don't invent information that isn't present.
If a field cannot be determined from the provided information, use "N/A" or null as appropriate.
"""),
            HumanMessage(content="""Please generate a CRM entry for the following customer interaction:

Customer Name: {customer_name}
Interaction Details:
{interaction_details}

Additional Information:
{additional_info}
""")
        ])
        
        logger.info("CRM entry generator tool initialized")
    
    def _run(self, customer_name: str, interaction_details: str, 
             additional_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the CRM entry generation.
        
        Args:
            customer_name: The name of the customer
            interaction_details: Details of the customer interaction
            additional_info: Additional context or information
            
        Returns:
            A structured CRM entry as a dictionary
        """
        try:
            # Format additional info for display
            additional_info_str = "None"
            if additional_info and len(additional_info) > 0:
                additional_info_str = json.dumps(additional_info, indent=2)
            
            # Format the prompt with interaction details
            formatted_prompt = self.prompt.format_messages(
                customer_name=customer_name,
                interaction_details=interaction_details,
                additional_info=additional_info_str
            )
            
            # Get the CRM entry from the LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Parse the JSON response
            try:
                # Try to extract JSON from the response
                content = response.content
                
                # Check if the response is already valid JSON
                try:
                    crm_entry = json.loads(content)
                except json.JSONDecodeError:
                    # If not, try to extract JSON from the text
                    import re
                    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        crm_entry = json.loads(json_str)
                    else:
                        # If no JSON block found, assume the whole response is JSON with possible text around it
                        # Find the first { and the last }
                        start_idx = content.find('{')
                        end_idx = content.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            json_str = content[start_idx:end_idx+1]
                            crm_entry = json.loads(json_str)
                        else:
                            raise ValueError("Could not extract valid JSON from the response")
                
                logger.info(f"Successfully generated CRM entry for {customer_name}")
                return crm_entry
                
            except Exception as json_error:
                logger.error(f"Error parsing CRM entry JSON: {str(json_error)}")
                # If JSON parsing fails, return the raw text
                return {
                    "customer_name": customer_name,
                    "raw_entry": response.content,
                    "error": "Failed to parse structured CRM entry"
                }
            
        except Exception as e:
            error_msg = f"Error generating CRM entry: {str(e)}"
            logger.error(error_msg)
            return {
                "customer_name": customer_name,
                "error": error_msg
            }
    
    def create_crm_entry(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a CRM entry using the provided interaction data.
        
        Args:
            interaction_data: Dictionary containing interaction details
            
        Returns:
            A structured CRM entry
        """
        return self._run(
            customer_name=interaction_data["customer_name"],
            interaction_details=interaction_data["interaction_details"],
            additional_info=interaction_data.get("additional_info", {})
        )