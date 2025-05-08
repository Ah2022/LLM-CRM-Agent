from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

from app.agent import CustomerServiceAgent
from app.config import settings

app = FastAPI(title="LLM Customer Service Agent", 
              description="AI-powered customer service automation")

# Initialize the agent
agent = CustomerServiceAgent()

class EmailRequest(BaseModel):
    subject: str
    body: str
    sender: str
    date: str
    attachments: Optional[List[str]] = None

class TicketRequest(BaseModel):
    title: str
    description: str
    customer_id: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None

class CRMEntryRequest(BaseModel):
    customer_name: str
    interaction_details: str
    additional_info: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    query: str
    customer_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "LLM Customer Service Agent API is running"}

@app.post("/summarize-email")
async def summarize_email(email: EmailRequest):
    """Summarize an incoming email"""
    try:
        summary = agent.summarize_email(
            subject=email.subject,
            body=email.body,
            sender=email.sender,
            date=email.date,
            attachments=email.attachments
        )
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing email: {str(e)}")

@app.post("/categorize-ticket")
async def categorize_ticket(ticket: TicketRequest):
    """Categorize and prioritize a support ticket"""
    try:
        result = agent.categorize_ticket(
            title=ticket.title,
            description=ticket.description,
            customer_id=ticket.customer_id,
            priority=ticket.priority,
            category=ticket.category
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error categorizing ticket: {str(e)}")

@app.post("/create-crm-entry")
async def create_crm_entry(entry: CRMEntryRequest):
    """Generate a CRM entry from customer interaction"""
    try:
        crm_entry = agent.create_crm_entry(
            customer_name=entry.customer_name,
            interaction_details=entry.interaction_details,
            additional_info=entry.additional_info
        )
        return {"crm_entry": crm_entry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating CRM entry: {str(e)}")

@app.post("/route-query")
async def route_query(query_req: QueryRequest):
    """Route a customer query to the appropriate department"""
    try:
        routing = agent.route_query(
            query=query_req.query,
            customer_id=query_req.customer_id,
            context=query_req.context
        )
        return routing
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error routing query: {str(e)}")

@app.post("/process-email-batch")
async def process_email_batch(background_tasks: BackgroundTasks):
    """Process a batch of emails from the configured email service"""
    try:
        background_tasks.add_task(agent.process_email_batch)
        return {"message": "Email batch processing started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting email batch process: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)