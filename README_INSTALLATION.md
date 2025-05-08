# Installation Guide for LLM Customer Service Agent

This guide provides detailed instructions for installing and setting up the LLM Customer Service Agent project.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- OpenAI API key (for LLM functionality)
- (Optional) API keys for email, CRM, and ticket services

## Installation Options

There are two ways to install the project:

1. **Automated Installation** (Recommended)
2. **Manual Installation**

## Option 1: Automated Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/llm-customer-service-agent.git
cd llm-customer-service-agent
```

### Step 2: Run the Installation Script

```bash
python install_requirements.py
```

This script will:
- Install all required packages from requirements.txt
- Add the project directory to your Python path
- Verify the installation by checking imports

### Step 3: Test the Installation

```bash
python test_installation.py
```

This will verify that:
- The project directory is in your Python path
- All required modules can be imported
- Key components can be initialized

## Option 2: Manual Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/llm-customer-service-agent.git
cd llm-customer-service-agent
```

### Step 2: Create and Activate a Virtual Environment (Optional but Recommended)

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Packages

```bash
pip install -r requirements.txt
```

### Step 4: Add Project to Python Path

#### Option A: Using PYTHONPATH Environment Variable

##### On Windows:
```bash
set PYTHONPATH=%PYTHONPATH%;%CD%
```

##### On macOS/Linux:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

#### Option B: Creating a .pth File

Create a file named `llm_customer_service.pth` in your Python site-packages directory with the absolute path to your project directory.

```python
# Example Python code to create the .pth file
import site
import os

with open(os.path.join(site.getsitepackages()[0], "llm_customer_service.pth"), "w") as f:
    f.write(os.path.abspath("."))
```

### Step 5: Test the Installation

```bash
python test_installation.py
```

## Configuration

### Setting up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your API keys and configuration:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   LLM_MODEL=gpt-4
   LLM_TEMPERATURE=0.2
   ...
   ```

## Troubleshooting

### Common Issues

#### ImportError: No module named 'app'

This means the project directory is not in your Python path. Solutions:
- Run `python install_requirements.py` to fix this automatically
- Add the project directory to PYTHONPATH manually
- Create a .pth file manually as described above

#### ModuleNotFoundError for a specific package

This means a required package is not installed. Solution:
```bash
pip install -r requirements.txt
```

#### Permission Errors When Adding to Path

If you get permission errors when running the installation script:
- Run your terminal/command prompt as administrator
- Use the manual installation method with PYTHONPATH

## Running the Application

After installation, you can run the application:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## Using Docker (Alternative)

If you prefer to use Docker:

```bash
docker build -t llm-customer-service-agent .
docker run -p 8000:8000 --env-file .env llm-customer-service-agent
```

## Next Steps

After installation:
1. Configure your API keys in the `.env` file
2. Run the application
3. Explore the API endpoints at http://localhost:8000/docs