# Banking Agent Backend

FastAPI backend for the Banking Agent application with Azure OpenAI text-to-SQL capabilities.

## Features

- 🚀 **FastAPI** - Modern, fast web framework
- 🤖 **Azure OpenAI Integration** - Latest Azure OpenAI SDK for text-to-SQL conversion
- 🔄 **CORS Support** - Cross-origin requests for frontend integration
- 📊 **Mock Database** - Demo data for testing and development
- 🔍 **Health Checks** - API health monitoring
- 📚 **Auto-generated API Docs** - Interactive API documentation

## API Endpoints

### Core Endpoints
- `GET /` - Root endpoint with API info
- `GET /health` - Health check with Azure OpenAI status
- `GET /docs` - Interactive API documentation (Swagger UI)

### Data Source Endpoints
- `GET /api/datasources` - Get available data sources
- `GET /api/sample/{table_name}` - Get sample data from a table

### Text-to-SQL Endpoints
- `POST /api/text-to-sql` - Convert natural language to SQL and execute
- `POST /api/query` - Execute SQL query directly

## Setup

### 1. Install Dependencies

```bash
# Make sure you're in your existing virtual environment
source /path/to/your/venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

The backend uses the root `.env` file located at `/Users/kanavkahol/work/neurostack/.env`. Ensure it contains:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://dietra-openai-gateway.azure-api.net/ai/
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

### 3. Azure OpenAI Setup

1. Create an Azure OpenAI resource in the Azure portal
2. Deploy a model (e.g., GPT-4, GPT-3.5-turbo)
3. Get your endpoint URL and API key
4. Update the `.env` file with your credentials

## Running the Backend

### Development Mode
```bash
python start.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using Docker (optional)
```bash
docker build -t banking-agent-backend .
docker run -p 8000:8000 --env-file .env banking-agent-backend
```

## API Usage Examples

### Text-to-SQL Conversion

```bash
curl -X POST "http://localhost:8000/api/text-to-sql" \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language_query": "Show me customers with income above $100,000",
    "table_name": "customer_demographics",
    "fields": ["customer_id", "first_name", "last_name", "annual_income", "state"]
  }'
```

### Execute SQL Query

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM customer_demographics WHERE annual_income > 100000",
    "table_name": "customer_demographics"
  }'
```

### Get Data Sources

```bash
curl -X GET "http://localhost:8000/api/datasources"
```

## Mock Data

The backend includes mock data for demonstration:

- **customer_demographics** - Customer information
- **internal_banking_data** - Banking relationship data
- **credit_bureau_data** - Credit bureau information

## Frontend Integration

The backend is configured to work with the React frontend running on `http://localhost:3000`. CORS is enabled for seamless integration.

## Error Handling

The API includes comprehensive error handling:
- Azure OpenAI connection errors
- Invalid SQL queries
- Missing environment variables
- Database connection issues

## Logging

Logs are configured to show:
- API requests and responses
- Azure OpenAI interactions
- Error details
- Performance metrics

## Development

### Project Structure
```
backend/
├── main.py          # FastAPI application
├── start.py         # Startup script
├── requirements.txt # Python dependencies
├── .env            # Environment variables
└── README.md       # This file
```

### Adding New Endpoints

1. Define Pydantic models for request/response
2. Create the endpoint function
3. Add proper error handling
4. Update this README

### Testing

```bash
# Run with pytest (if tests are added)
pytest

# Manual testing with curl
curl http://localhost:8000/health
```

## Troubleshooting

### Common Issues

1. **Azure OpenAI Connection Error**
   - Check your endpoint URL and API key
   - Verify the deployment name exists
   - Ensure the API version is correct

2. **CORS Errors**
   - Verify the frontend URL is in the allowed origins
   - Check that the backend is running on the correct port

3. **Port Already in Use**
   - Change the PORT in .env file
   - Kill existing processes using the port

### Debug Mode

Set `DEBUG=true` in your `.env` file to enable:
- Auto-reload on code changes
- Detailed error messages
- Development logging

## License

This project is part of the NeuroStack Banking Agent application.
