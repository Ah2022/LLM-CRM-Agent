"""
Configuration settings for the LLM Customer Service Agent.

This module loads environment variables and provides configuration
settings for the application.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # LLM Settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    
    # Agent Settings
    AGENT_VERBOSE: bool = os.getenv("AGENT_VERBOSE", "False").lower() == "true"
    
    # Email Service Settings
    EMAIL_SERVICE_TYPE: str = os.getenv("EMAIL_SERVICE_TYPE", "gmail")  # gmail, outlook, etc.
    EMAIL_USERNAME: Optional[str] = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_CLIENT_ID: Optional[str] = os.getenv("EMAIL_CLIENT_ID", "")
    EMAIL_CLIENT_SECRET: Optional[str] = os.getenv("EMAIL_CLIENT_SECRET", "")
    EMAIL_TENANT_ID: Optional[str] = os.getenv("EMAIL_TENANT_ID", "")
    EMAIL_BATCH_SIZE: int = int(os.getenv("EMAIL_BATCH_SIZE", "10"))
    
    # CRM Service Settings
    CRM_SERVICE_TYPE: str = os.getenv("CRM_SERVICE_TYPE", "salesforce")  # salesforce, hubspot, etc.
    CRM_API_KEY: Optional[str] = os.getenv("CRM_API_KEY", "")
    CRM_INSTANCE_URL: Optional[str] = os.getenv("CRM_INSTANCE_URL", "")
    CRM_USERNAME: Optional[str] = os.getenv("CRM_USERNAME", "")
    CRM_PASSWORD: Optional[str] = os.getenv("CRM_PASSWORD", "")
    
    # Ticket Service Settings
    TICKET_SERVICE_TYPE: str = os.getenv("TICKET_SERVICE_TYPE", "zendesk")  # zendesk, freshdesk, etc.
    TICKET_API_KEY: Optional[str] = os.getenv("TICKET_API_KEY", "")
    TICKET_SUBDOMAIN: Optional[str] = os.getenv("TICKET_SUBDOMAIN", "")
    TICKET_EMAIL: Optional[str] = os.getenv("TICKET_EMAIL", "")
    
    # RAG Settings
    RAG_ENABLED: bool = os.getenv("RAG_ENABLED", "True").lower() == "true"
    RAG_VECTOR_STORE_TYPE: str = os.getenv("RAG_VECTOR_STORE_TYPE", "chroma")
    RAG_VECTOR_STORE_PATH: str = os.getenv("RAG_VECTOR_STORE_PATH", "./vector_store")
    RAG_EMBEDDING_MODEL: str = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "False").lower() == "true"
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Department and Category Settings
    DEPARTMENTS: List[str] = os.getenv("DEPARTMENTS", "Sales,Support,Billing,Technical,General").split(",")
    TICKET_PRIORITIES: List[str] = os.getenv("TICKET_PRIORITIES", "Low,Medium,High,Critical").split(",")
    TICKET_CATEGORIES: List[str] = os.getenv("TICKET_CATEGORIES", 
                                           "Account,Billing,Product,Technical,Feature Request,Bug").split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings object
settings = Settings()

def get_settings() -> Settings:
    """Return the settings object."""
    return settings