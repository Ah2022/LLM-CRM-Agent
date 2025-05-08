"""
Memory module for the LLM Customer Service Agent.

This module provides memory implementations for the agent to maintain
context across interactions.
"""

from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseChatMessageHistory
from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Any, Optional
import logging
import json
import os
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class AgentMemory(ConversationBufferMemory):
    """
    Enhanced conversation memory for the customer service agent.
    
    This memory implementation extends ConversationBufferMemory with
    additional features like persistent storage and context management.
    """
    
    def __init__(self, memory_key: str = "chat_history", return_messages: bool = True):
        """Initialize the agent memory."""
        super().__init__(memory_key=memory_key, return_messages=return_messages)
        self.customer_contexts: Dict[str, Dict[str, Any]] = {}
        self.memory_file_path = "agent_memory.json"
        self._load_memory()
        
        logger.info("Agent memory initialized")
    
    def _load_memory(self):
        """Load memory from disk if available."""
        try:
            if os.path.exists(self.memory_file_path):
                with open(self.memory_file_path, 'r') as f:
                    data = json.load(f)
                    
                    # Load customer contexts
                    self.customer_contexts = data.get("customer_contexts", {})
                    
                    # Load conversation history
                    for message_data in data.get("messages", []):
                        if message_data["type"] == "human":
                            self.chat_memory.add_message(
                                HumanMessage(content=message_data["content"])
                            )
                        elif message_data["type"] == "ai":
                            self.chat_memory.add_message(
                                AIMessage(content=message_data["content"])
                            )
                        elif message_data["type"] == "system":
                            self.chat_memory.add_message(
                                SystemMessage(content=message_data["content"])
                            )
                
                logger.info(f"Loaded memory from {self.memory_file_path}")
        except Exception as e:
            logger.error(f"Error loading memory: {str(e)}")
    
    def _save_memory(self):
        """Save memory to disk."""
        try:
            # Convert messages to serializable format
            messages = []
            for message in self.chat_memory.messages:
                if isinstance(message, HumanMessage):
                    messages.append({"type": "human", "content": message.content})
                elif isinstance(message, AIMessage):
                    messages.append({"type": "ai", "content": message.content})
                elif isinstance(message, SystemMessage):
                    messages.append({"type": "system", "content": message.content})
            
            # Prepare data for saving
            data = {
                "customer_contexts": self.customer_contexts,
                "messages": messages,
                "last_updated": datetime.now().isoformat()
            }
            
            # Save to file
            with open(self.memory_file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved memory to {self.memory_file_path}")
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Save context from this conversation turn.
        
        Args:
            inputs: The inputs for this conversation turn
            outputs: The outputs for this conversation turn
        """
        super().save_context(inputs, outputs)
        self._save_memory()
    
    def clear(self) -> None:
        """Clear memory contents."""
        super().clear()
        self._save_memory()
    
    def get_customer_context(self, customer_id: str) -> Dict[str, Any]:
        """
        Get context for a specific customer.
        
        Args:
            customer_id: The ID of the customer
            
        Returns:
            The customer's context data
        """
        return self.customer_contexts.get(customer_id, {})
    
    def update_customer_context(self, customer_id: str, context_data: Dict[str, Any]) -> None:
        """
        Update context for a specific customer.
        
        Args:
            customer_id: The ID of the customer
            context_data: The context data to update
        """
        if customer_id not in self.customer_contexts:
            self.customer_contexts[customer_id] = {}
        
        # Update the customer context with new data
        self.customer_contexts[customer_id].update(context_data)
        
        # Add timestamp for when this context was last updated
        self.customer_contexts[customer_id]["last_updated"] = datetime.now().isoformat()
        
        # Save the updated memory
        self._save_memory()
        
        logger.info(f"Updated context for customer {customer_id}")
    
    def get_relevant_history(self, customer_id: Optional[str] = None, 
                            max_messages: int = 10) -> List[Dict[str, Any]]:
        """
        Get relevant conversation history, optionally filtered by customer ID.
        
        Args:
            customer_id: Optional customer ID to filter history
            max_messages: Maximum number of messages to return
            
        Returns:
            List of relevant conversation messages
        """
        # Get all messages
        all_messages = self.chat_memory.messages
        
        # If no customer ID is provided, just return the most recent messages
        if not customer_id:
            return all_messages[-max_messages:]
        
        # Filter messages by customer ID if present in additional_kwargs
        relevant_messages = []
        for message in all_messages:
            message_customer_id = message.additional_kwargs.get("customer_id")
            if message_customer_id == customer_id:
                relevant_messages.append(message)
        
        # Return the most recent relevant messages
        return relevant_messages[-max_messages:]