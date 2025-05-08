"""
RAG (Retrieval-Augmented Generation) Tool

This module provides a tool for retrieving relevant information from a
knowledge base to enhance the agent's responses.
"""

from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
import logging
import os
import json

from app.config import settings

logger = logging.getLogger(__name__)

class RAGQueryInput(BaseModel):
    """Input schema for the RAG tool."""
    query: str = Field(..., description="The query to retrieve information for")
    context: Optional[Dict[str, Any]] = Field({}, description="Additional context for the query")
    max_results: Optional[int] = Field(3, description="Maximum number of results to return")

class RAGTool(BaseTool):
    """
    A tool for retrieving relevant information from a knowledge base.
    
    This tool uses a vector store to retrieve documents relevant to a query
    and generates a response based on the retrieved information.
    """
    
    name = "rag_tool"
    description = "Retrieves relevant information from a knowledge base to answer questions"
    args_schema: Type[BaseModel] = RAGQueryInput
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """Initialize the RAG tool with an optional LLM."""
        super().__init__()
        self.llm = llm or ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.2,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.RAG_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize or load the vector store
        self.vector_store = self._initialize_vector_store()
        
        # Create the response generation prompt template
        self.response_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a knowledgeable assistant that provides accurate information based on the retrieved context.
Your task is to answer the user's query using only the information provided in the context.

Guidelines:
1. If the context contains the information needed to answer the query, provide a comprehensive response.
2. If the context only partially addresses the query, provide what information you can and acknowledge the limitations.
3. If the context doesn't contain relevant information, honestly state that you don't have enough information to answer.
4. Do not make up information or use knowledge outside of the provided context.
5. Cite the specific parts of the context that your answer is based on.

Format your response in a clear, concise manner. Use bullet points or numbered lists when appropriate.
"""),
            HumanMessage(content="""Query: {query}

Context:
{context}

Please provide a response based solely on the above context.
""")
        ])
        
        logger.info("RAG tool initialized")
    
    def _initialize_vector_store(self):
        """Initialize or load the vector store."""
        vector_store_path = settings.RAG_VECTOR_STORE_PATH
        
        # Check if the vector store already exists
        if os.path.exists(vector_store_path) and os.path.isdir(vector_store_path) and len(os.listdir(vector_store_path)) > 0:
            # Load existing vector store
            try:
                vector_store = Chroma(
                    persist_directory=vector_store_path,
                    embedding_function=self.embeddings
                )
                logger.info(f"Loaded existing vector store from {vector_store_path}")
                return vector_store
            except Exception as e:
                logger.error(f"Error loading vector store: {str(e)}")
                # If loading fails, create a new one
        
        # Create directory if it doesn't exist
        os.makedirs(vector_store_path, exist_ok=True)
        
        # Create a new vector store
        vector_store = Chroma(
            persist_directory=vector_store_path,
            embedding_function=self.embeddings
        )
        
        logger.info(f"Created new vector store at {vector_store_path}")
        return vector_store
    
    def add_documents(self, documents_path: str):
        """
        Add documents to the vector store.
        
        Args:
            documents_path: Path to a file or directory containing documents to add
        """
        try:
            # Load documents
            if os.path.isdir(documents_path):
                loader = DirectoryLoader(documents_path)
            else:
                loader = TextLoader(documents_path)
            
            documents = loader.load()
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vector_store.add_documents(splits)
            self.vector_store.persist()
            
            logger.info(f"Added {len(splits)} document chunks to the vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def _run(self, query: str, context: Optional[Dict[str, Any]] = None, 
             max_results: int = 3) -> str:
        """
        Run the RAG query.
        
        Args:
            query: The query to retrieve information for
            context: Additional context for the query (optional)
            max_results: Maximum number of results to return
            
        Returns:
            A response based on the retrieved information
        """
        try:
            # Check if RAG is enabled
            if not settings.RAG_ENABLED:
                return "RAG functionality is currently disabled. Please enable it in the settings."
            
            # Check if the vector store has documents
            if self.vector_store._collection.count() == 0:
                return "The knowledge base is empty. Please add documents before using this tool."
            
            # Retrieve relevant documents
            docs = self.vector_store.similarity_search(query, k=max_results)
            
            if not docs:
                return "No relevant information found in the knowledge base."
            
            # Format the retrieved documents as context
            context_text = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
            
            # Format the prompt with query and context
            formatted_prompt = self.response_prompt.format_messages(
                query=query,
                context=context_text
            )
            
            # Generate response based on retrieved information
            response = self.llm.invoke(formatted_prompt)
            
            logger.info(f"Successfully generated RAG response for query: {query[:50]}...")
            return response.content
            
        except Exception as e:
            error_msg = f"Error retrieving information: {str(e)}"
            logger.error(error_msg)
            return f"Failed to retrieve information: {error_msg}"
    
    def retrieve_information(self, query_data: Dict[str, Any]) -> str:
        """
        Retrieve information using the provided query data.
        
        Args:
            query_data: Dictionary containing query details
            
        Returns:
            A response based on the retrieved information
        """
        return self._run(
            query=query_data["query"],
            context=query_data.get("context", {}),
            max_results=query_data.get("max_results", 3)
        )