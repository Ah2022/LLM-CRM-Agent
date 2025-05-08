"""
Email Summarizer Tool

This module provides a tool for summarizing emails using LLMs.
"""

from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class EmailInput(BaseModel):
    """Input schema for the email summarizer."""
    subject: str = Field(..., description="The email subject line")
    body: str = Field(..., description="The full email body text")
    sender: str = Field(..., description="The email sender's name or address")
    date: str = Field(..., description="The date and time when the email was sent")
    attachments: Optional[List[str]] = Field(None, description="List of attachment filenames, if any")

class EmailSummarizer(BaseTool):
    """
    A tool for summarizing emails into concise, actionable points.
    
    This tool uses an LLM to extract key information from emails, identify
    action items, and generate a concise summary.
    """
    
    name = "email_summarizer"
    description = "Summarizes emails into key points and action items"
    args_schema: Type[BaseModel] = EmailInput
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """Initialize the email summarizer with an optional LLM."""
        super().__init__()
        self.llm = llm or ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.1,  # Lower temperature for more focused summaries
            api_key=settings.OPENAI_API_KEY
        )
        
        # Create the summarization prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert email summarizer for a busy professional.
Your task is to extract the most important information from emails and present it in a clear, concise format.

For each email, provide:
1. A one-sentence TLDR summary
2. Key points (2-4 bullet points)
3. Any action items or requests (if present)
4. Any deadlines or important dates (if present)

Be concise but comprehensive. Focus on extracting actionable information and the core message.
Ignore pleasantries and standard email formalities unless they contain important context.
"""),
            HumanMessage(content="""Please summarize the following email:

Subject: {subject}
From: {sender}
Date: {date}
Attachments: {attachments}

Email Body:
{body}
""")
        ])
        
        logger.info("Email summarizer tool initialized")
    
    def _run(self, subject: str, body: str, sender: str, date: str, 
             attachments: Optional[List[str]] = None) -> str:
        """
        Run the email summarization.
        
        Args:
            subject: The email subject line
            body: The full email body text
            sender: The email sender's name or address
            date: The date and time when the email was sent
            attachments: List of attachment filenames, if any
            
        Returns:
            A concise summary of the email
        """
        try:
            # Format attachments for display
            attachments_str = "None"
            if attachments and len(attachments) > 0:
                attachments_str = ", ".join(attachments)
            
            # Format the prompt with email details
            formatted_prompt = self.prompt.format_messages(
                subject=subject,
                body=body,
                sender=sender,
                date=date,
                attachments=attachments_str
            )
            
            # Get the summary from the LLM
            response = self.llm.invoke(formatted_prompt)
            summary = response.content
            
            logger.info(f"Successfully summarized email from {sender}")
            return summary
            
        except Exception as e:
            error_msg = f"Error summarizing email: {str(e)}"
            logger.error(error_msg)
            return f"Failed to summarize email: {error_msg}"
    
    def summarize_email(self, email_data: Dict[str, Any]) -> str:
        """
        Summarize an email using the provided email data.
        
        Args:
            email_data: Dictionary containing email details (subject, body, sender, date, attachments)
            
        Returns:
            A concise summary of the email
        """
        return self._run(
            subject=email_data["subject"],
            body=email_data["body"],
            sender=email_data["sender"],
            date=email_data["date"],
            attachments=email_data.get("attachments")
        )