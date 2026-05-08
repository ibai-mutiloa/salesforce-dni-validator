# Salesforce Identity Validator - Complete Setup Guide

This guide will walk you through setting up the Salesforce Identity Validator microservice for local development, testing, and production deployment.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed on your system
- **Git** for version control
- **Azure account** with Document Intelligence resource
- **Docker & Docker Compose** (optional, for containerization)
- **Salesforce sandbox** or development environment for testing

## Step 1: Obtain Azure Credentials

### Create an Azure Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Document Intelligence" or navigate to **Create a resource** → **AI + Machine Learning** → **Document Intelligence**
3. Fill in the details:
   - **Name**: `identity-validator` (or your preferred name)
   - **Region**: Choose your region (e.g., East US)
   - **Pricing tier**: Standard (S0) recommended for production
4. Click **Review + Create** then **Create**
5. Wait for deployment to complete

### Get Your Credentials

1. Go to your Document Intelligence resource
2. In the left menu, click **Keys and Endpoint**
3. Copy the following:
   - **Endpoint URL** (e.g., `https://your-resource.cognitiveservices.azure.com/`)
   - **Key 1** or **Key 2** (API Key)
4. Save these values - you'll need them for configuration

## Step 2: Clone and Setup Repository

### Clone the Repository

```bash
git clone https://github.com/ibai-mutiloa/salesforce-dni-validator.git
cd SalesforceIdentityValidator
```

### Create Python Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (CMD):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

## Step 3: Configure Environment Variables

### Create .env File

```bash
cp .env.example .env
```

### Edit .env with Your Azure Credentials

Open `.env` and update the values:

```bash
# API Configuration
API_TITLE=Salesforce Identity Validator
API_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO
LOG_FORMAT=json

# Azure Document Intelligence - REQUIRED
AZURE_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
AZURE_API_KEY=your-actual-api-key-from-azure
AZURE_API_VERSION=2024-11-30
AZURE_ANALYZER_ID=prebuilt-idDocument

# Validation Settings
MIN_NAME_MATCH_SCORE=85.0

# Security
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

⚠️ **Important**: Never commit `.env` file to version control. It contains sensitive credentials.

## Step 4: Install Dependencies

### Install Python Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Verify Installation

```bash
pip list
```

You should see these packages installed:
- fastapi (0.104.1+)
- uvicorn (0.24.0+)
- pydantic (2.5.0+)
- azure-ai-documentintelligence (1.0.0+)
- rapidfuzz (3.5.2+)
- pytest (7.4.3+)

## Step 5: Run the Application

### Local Development

```bash
# Method 1: Direct Python execution
python main.py

# Method 2: Using Uvicorn with auto-reload
uvicorn main:app --reload

# Method 3: Custom host/port
uvicorn main:app --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Verify the Server is Running

In another terminal:
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{"status":"healthy","version":"1.0.0","azure_connected":true}
```

## Step 6: Test the API

### Access Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Run Example Tests

**Python Examples:**
```bash
python examples.py
```

**Shell Examples:**
```bash
bash examples.sh
```

### Run Unit Tests

```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_text_processing.py -v

# With coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View in browser
```

## Step 7: Manual API Testing

### Example Validation Request

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/validate-identity" \
  -F "user_id=005xx000000xyz" \
  -F "first_name=Jonathan" \
  -F "last_name=Garcia" \
  -F "document=@/path/to/id_document.pdf"
```

**Using Python:**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/validate-identity',
    data={
        'user_id': '005xx000000xyz',
        'first_name': 'Jonathan',
        'last_name': 'Garcia'
    },
    files={'document': open('id_document.pdf', 'rb')}
)

result = response.json()
print(result)
```

## Docker Setup (Optional)

### Build Docker Image

```bash
docker build -t salesforce-identity-validator:1.0.0 .
```

### Run with Docker

```bash
docker run -d \
  --name identity-validator \
  -p 8000:8000 \
  --env-file .env \
  salesforce-identity-validator:1.0.0
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Development Workflow

### Making Code Changes

1. **Edit files** in your preferred editor
2. **Run tests** to verify changes: `pytest -v`
3. **Check code quality**: Look for syntax errors
4. **Commit changes**: `git add . && git commit -m "Description"`
5. **Push to remote**: `git push origin main`

### Common Development Tasks

**View logs:**
```bash
tail -f debug.log
```

**Debug with print statements:**
```python
# In your code
print(f"DEBUG: value = {value}")
```

**Run specific test:**
```bash
pytest tests/test_validation_service.py::TestIdentityValidationService::test_exact_match_validation -v
```

**Format code (if using black):**
```bash
pip install black
black app/
```

## Troubleshooting

### Issue: "Module 'app' not found"
**Solution**: Make sure you're in the correct directory and virtual environment is activated
```bash
cd SalesforceIdentityValidator
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Issue: "AZURE_ENDPOINT not found"
**Solution**: Ensure `.env` file exists and has correct Azure credentials
```bash
# Check if .env exists
ls -la .env  # or dir .env on Windows

# Verify content
cat .env
```

### Issue: "Connection refused" when calling Azure
**Solution**: Check Azure credentials and endpoint URL
```bash
# Test Azure connectivity
curl -H "Ocp-Apim-Subscription-Key: YOUR_KEY" \
  https://your-resource.cognitiveservices.azure.com/
```

### Issue: Port 8000 already in use
**Solution**: Use a different port
```bash
uvicorn main:app --port 8001
```

### Issue: Test failures
**Solution**: Ensure dependencies are installed and Azure is accessible
```bash
pip install -r requirements.txt --upgrade
pytest -v -s  # -s shows print statements
```

## Next Steps

1. **Integrate with Salesforce**: Connect your Salesforce instance to call the API
2. **Deploy to Production**: Follow the deployment guide in README.md
3. **Monitor Performance**: Set up logging and monitoring
4. **Scale the Service**: Use Docker Compose or Kubernetes for scaling

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Document Intelligence Docs](https://docs.microsoft.com/azure/ai-services/document-intelligence/)
- [RapidFuzz Documentation](https://maxbachmann.github.io/RapidFuzz/)
- [Docker Documentation](https://docs.docker.com/)

## Getting Help

- **Issues**: Check [GitHub Issues](https://github.com/ibai-mutiloa/salesforce-dni-validator/issues)
- **Documentation**: Read [README.md](README.md)
- **Examples**: Check `examples.py`, `examples.sh`, and `examples.js`

---

**Need help?** Make sure your environment variables are correct and test the health endpoint!
