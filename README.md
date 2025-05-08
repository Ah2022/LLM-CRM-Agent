# LLM Customer Service Agent

An AI-powered customer service automation system that leverages LangChain and Large Language Models (LLMs) to automate repetitive workflows in customer service operations.

## Features

- **Email Summarization**: Automatically summarize inbound emails into concise, actionable points
- **Support Ticket Handling**: Pre-screen and categorize support tickets by priority, department, and issue type
- **CRM Entry Creation**: Generate structured CRM entries from customer interactions
- **Query Routing**: Intelligently route customer queries to the appropriate department
- **RAG Capabilities**: Retrieve relevant information from a knowledge base to enhance responses (optional)

## Architecture

```
llm-customer-service-agent/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app entry
│   ├── agent.py              # LangChain agent setup
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── summarizer.py     # Email summarizer
│   │   ├── crm_entry.py      # CRM entry generator
│   │   ├── ticket_router.py  # Support ticket routing
│   │   └── rag_tool.py       # RAG tool
│   ├── services/
│   │   ├── email.py          # Gmail/Graph API connector
│   │   ├── crm.py            # Salesforce/HubSpot integration
│   │   └── tickets.py        # Zendesk, Freshdesk API
│   ├── config.py             # Env vars & settings
│   └── memory.py             # Agent memory setup
├── tests/
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_integration.py
├── .env                      # API keys & secrets
├── Dockerfile
├── requirements.txt
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- (Optional) API keys for email, CRM, and ticket services

### Installation

#### Quick Installation (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-customer-service-agent.git
   cd llm-customer-service-agent
   ```

2. Run the installation script:
   - On Windows: Double-click `install.bat` or run it from the command line
   - On macOS/Linux: Run `bash install.sh` in the terminal

The installation script will:
- Install all required packages
- Add the project to your Python path
- Verify the installation

#### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-customer-service-agent.git
   cd llm-customer-service-agent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add the project to your Python path:
   ```bash
   # On Windows
   set PYTHONPATH=%PYTHONPATH%;%CD%

   # On macOS/Linux
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

5. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration values

For detailed installation instructions, troubleshooting, and alternative methods, see [README_INSTALLATION.md](README_INSTALLATION.md).

### Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t llm-customer-service-agent .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env llm-customer-service-agent
   ```

## API Endpoints

- `GET /`: Health check endpoint
- `POST /summarize-email`: Summarize an email
- `POST /categorize-ticket`: Categorize and prioritize a support ticket
- `POST /create-crm-entry`: Generate a CRM entry from customer interaction
- `POST /route-query`: Route a customer query to the appropriate department
- `POST /process-email-batch`: Process a batch of emails (background task)

## Configuration

The application can be configured using environment variables in the `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key
- `LLM_MODEL`: The LLM model to use (default: gpt-4)
- `LLM_TEMPERATURE`: Temperature setting for the LLM (default: 0.2)
- `EMAIL_SERVICE_TYPE`: Email service to use (gmail, outlook)
- `CRM_SERVICE_TYPE`: CRM service to use (salesforce, hubspot)
- `TICKET_SERVICE_TYPE`: Ticket service to use (zendesk, freshdesk)
- `RAG_ENABLED`: Enable/disable RAG functionality

See the `.env` file for all available configuration options.

## Testing

Run the tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Extending the Agent

### Adding a New Tool

1. Create a new tool file in `app/tools/`
2. Implement a class that extends `BaseTool` from LangChain
3. Register the tool in `app/agent.py`

### Adding a New Service Integration

1. Create a new service file in `app/services/`
2. Implement the service class with appropriate methods
3. Update the configuration in `app/config.py`
4. Use the service in the agent or tools as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the LLM framework
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [OpenAI](https://openai.com/) for the LLM models
