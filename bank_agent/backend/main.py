from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import asyncio
import re
from datetime import datetime
import logging
from dotenv import load_dotenv
import httpx

# Azure OpenAI imports
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential

# Load environment variables from root directory
load_dotenv(dotenv_path="/Users/kanavkahol/work/neurostack/.env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Banking Agent Backend",
    description="FastAPI backend for banking agent with Azure OpenAI text-to-SQL capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TextToSQLRequest(BaseModel):
    natural_language_query: str
    table_name: str
    fields: List[str]
    sample_data: Optional[List[Dict[str, Any]]] = None

class SQLQueryRequest(BaseModel):
    sql: str
    table_name: Optional[str] = None

class QueryResult(BaseModel):
    success: bool
    sql: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None

class DataSource(BaseModel):
    id: str
    name: str
    description: str
    category: str
    is_enabled: bool
    table_name: str
    fields: List[str]
    sample_query: Optional[str] = None

# Azure OpenAI client initialization
def get_azure_openai_client():
    """Initialize Azure OpenAI client with environment variables"""
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not endpoint or not api_key:
            raise ValueError("Azure OpenAI endpoint and key must be set in environment variables")
        
        # Check if this is an APIM endpoint
        if "azure-api.net" in endpoint:
            # For APIM endpoints, we need to use the subscription key header
            # The endpoint should be the base APIM URL
            base_endpoint = endpoint.replace("/ai/", "")
            client = AzureOpenAI(
                azure_endpoint=base_endpoint,
                api_key=api_key,
                api_version=api_version,
                default_headers={
                    "Ocp-Apim-Subscription-Key": api_key
                }
            )
        else:
            # Standard Azure OpenAI endpoint
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
        
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI client: {e}")
        raise

# Mock database for demo purposes
MOCK_DATABASES = {
    "customer_demographics": [
        {"customer_id": 1, "first_name": "John", "last_name": "Doe", "annual_income": 75000, "state": "CA"},
        {"customer_id": 2, "first_name": "Jane", "last_name": "Smith", "annual_income": 95000, "state": "NY"},
        {"customer_id": 3, "first_name": "Bob", "last_name": "Johnson", "annual_income": 65000, "state": "TX"},
    ],
    "internal_banking_data": [
        {"customer_id": 1, "current_credit_limit": 15000, "current_balance": 5000, "utilization_rate": 0.33},
        {"customer_id": 2, "current_credit_limit": 25000, "current_balance": 20000, "utilization_rate": 0.80},
        {"customer_id": 3, "current_credit_limit": 10000, "current_balance": 3000, "utilization_rate": 0.30},
    ],
    "credit_bureau_data": [
        {"customer_id": 1, "fico_score_8": 720, "fico_score_9": 725, "total_accounts_bureau": 8},
        {"customer_id": 2, "fico_score_8": 680, "fico_score_9": 685, "total_accounts_bureau": 12},
        {"customer_id": 3, "fico_score_8": 750, "fico_score_9": 755, "total_accounts_bureau": 5},
    ],
    "fraud_kyc_compliance": [
        {"customer_id": 1, "overall_fraud_risk_score": 3.2, "risk_level": "low", "kyc_score": 85, "identity_verification_status": "verified"},
        {"customer_id": 2, "overall_fraud_risk_score": 8.5, "risk_level": "high", "kyc_score": 45, "identity_verification_status": "pending"},
        {"customer_id": 3, "overall_fraud_risk_score": 1.8, "risk_level": "low", "kyc_score": 92, "identity_verification_status": "verified"},
        {"customer_id": 4, "overall_fraud_risk_score": 9.2, "risk_level": "high", "kyc_score": 30, "identity_verification_status": "failed"},
        {"customer_id": 5, "overall_fraud_risk_score": 7.8, "risk_level": "high", "kyc_score": 55, "identity_verification_status": "pending"},
    ]
}

# Sample data sources
SAMPLE_DATA_SOURCES = [
    {
        "id": "customer_demographics",
        "name": "Customer Demographics",
        "description": "Basic customer information including age, income, employment status, and location.",
        "category": "demographics",
        "is_enabled": True,
        "table_name": "customer_demographics",
        "fields": ["customer_id", "first_name", "last_name", "date_of_birth", "annual_income", "employment_status", "customer_segment", "state"],
        "sample_query": "Show me customers with income above $100,000"
    },
    {
        "id": "internal_banking_data",
        "name": "Internal Banking Data",
        "description": "Banking relationship data including payment history, credit utilization, account relationships, and tenure.",
        "category": "banking",
        "is_enabled": True,
        "table_name": "internal_banking_data",
        "fields": ["customer_id", "current_credit_limit", "current_balance", "utilization_rate", "on_time_payments_12m", "late_payments_12m", "tenure_months"],
        "sample_query": "Find customers with utilization rate above 80%"
    },
    {
        "id": "credit_bureau_data",
        "name": "Credit Bureau Data",
        "description": "External credit information including FICO scores, external accounts, delinquencies, and credit history.",
        "category": "credit_bureau",
        "is_enabled": True,
        "table_name": "credit_bureau_data",
        "fields": ["customer_id", "fico_score_8", "fico_score_9", "total_accounts_bureau", "external_utilization_rate", "delinquencies_30_plus_12m"],
        "sample_query": "List customers with FICO score below 650"
    },
    {
        "id": "fraud_kyc_compliance",
        "name": "Fraud/KYC/Compliance",
        "description": "Fraud detection, KYC verification, and compliance monitoring data.",
        "category": "fraud",
        "is_enabled": True,
        "table_name": "fraud_kyc_compliance",
        "fields": ["customer_id", "overall_fraud_risk_score", "risk_level", "kyc_score", "identity_verification_status"],
        "sample_query": "Identify high-risk customers with fraud score above 7"
    }
]

async def convert_text_to_sql(natural_language_query: str, table_name: str, fields: List[str]) -> str:
    """Convert natural language query to SQL using Azure OpenAI"""
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not deployment_name:
            raise ValueError("Azure OpenAI deployment name must be set in environment variables")
        
        # Build the prompt
        prompt = f"""
You are a SQL expert. Convert the following natural language query to a MySQL SELECT statement.

Table: {table_name}
Available fields: {', '.join(fields)}

Natural language query: "{natural_language_query}"

Convert this to a MySQL SELECT statement. Use appropriate WHERE clauses, ORDER BY, and LIMIT as needed.
Only return the SQL query, no explanations or markdown formatting.

SQL Query:
"""
        
        # Check if this is an APIM endpoint
        if "azure-api.net" in endpoint:
            # Use direct HTTP request for APIM
            
            # For APIM, we need to use the correct path format
            # Remove any trailing slashes and ensure proper format
            base_endpoint = endpoint.rstrip('/')
            url = f"{base_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
            
            headers = {
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": api_key,
                "User-Agent": "BankingAgent/1.0"
            }
            
            data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Convert natural language queries to MySQL SQL statements. Only return the SQL query, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Making request to APIM: {url}")
                logger.info(f"Deployment: {deployment_name}")
                logger.info(f"API Version: {api_version}")
                
                try:
                    response = await client.post(url, json=data, headers=headers)
                    logger.info(f"Response status: {response.status_code}")
                    
                    if response.status_code != 200:
                        logger.error(f"APIM Error: {response.text}")
                        # Try to get more details from the error response
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('message', response.text)
                        except:
                            error_msg = response.text
                        raise Exception(f"APIM returned status {response.status_code}: {error_msg}")
                    
                    result = response.json()
                    sql_query = result["choices"][0]["message"]["content"].strip()
                    
                except httpx.TimeoutException:
                    logger.error("APIM request timed out")
                    raise Exception("APIM request timed out after 30 seconds")
                except httpx.RequestError as e:
                    logger.error(f"APIM request error: {e}")
                    raise Exception(f"APIM request failed: {str(e)}")
        else:
            # Use Azure OpenAI SDK for standard endpoints
            client = get_azure_openai_client()
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Convert natural language queries to MySQL SQL statements. Only return the SQL query, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            sql_query = response.choices[0].message.content.strip()
        
        logger.info(f"Generated SQL: {sql_query}")
        return sql_query
        
    except Exception as e:
        logger.error(f"Error converting text to SQL: {e}")
        
        # Fallback to mock SQL generation for demo purposes
        logger.warning("Falling back to mock SQL generation")
        try:
            sql_query = generate_mock_sql(natural_language_query, table_name, fields)
            logger.info(f"Generated mock SQL: {sql_query}")
            return sql_query
        except Exception as fallback_error:
            logger.error(f"Mock SQL generation also failed: {fallback_error}")
            raise HTTPException(status_code=500, detail=f"Failed to convert text to SQL: {str(e)}")

def generate_mock_sql(natural_language_query: str, table_name: str, fields: List[str]) -> str:
    """Generate mock SQL for demo purposes when Azure OpenAI is not available"""
    query_lower = natural_language_query.lower()
    
    # Simple keyword-based SQL generation
    if "income" in query_lower and ("above" in query_lower or ">" in query_lower):
        # Extract number from query
        numbers = re.findall(r'\d+', natural_language_query)
        threshold = int(numbers[0]) if numbers else 50000
        
        return f"SELECT {', '.join(fields[:4])} FROM {table_name} WHERE annual_income > {threshold} ORDER BY annual_income DESC"
    
    elif "fico" in query_lower and ("below" in query_lower or "<" in query_lower):
        numbers = re.findall(r'\d+', natural_language_query)
        threshold = int(numbers[0]) if numbers else 650
        
        return f"SELECT {', '.join(fields[:4])} FROM {table_name} WHERE fico_score_8 < {threshold} ORDER BY fico_score_8 ASC"
    
    elif "utilization" in query_lower and ("above" in query_lower or ">" in query_lower):
        numbers = re.findall(r'\d+', natural_language_query)
        threshold = int(numbers[0]) if numbers else 80
        
        return f"SELECT {', '.join(fields[:4])} FROM {table_name} WHERE utilization_rate > {threshold/100} ORDER BY utilization_rate DESC"
    
    elif "fraud" in query_lower and ("above" in query_lower or ">" in query_lower):
        numbers = re.findall(r'\d+', natural_language_query)
        threshold = int(numbers[0]) if numbers else 7
        
        return f"SELECT {', '.join(fields[:4])} FROM {table_name} WHERE risk_level = 'high' AND overall_fraud_risk_score > {threshold} ORDER BY overall_fraud_risk_score DESC"
    
    elif "risk" in query_lower and "high" in query_lower:
        return f"SELECT {', '.join(fields[:4])} FROM {table_name} WHERE risk_level = 'high' ORDER BY overall_fraud_risk_score DESC"
    
    else:
        # Default query
        return f"SELECT {', '.join(fields[:4])} FROM {table_name} LIMIT 10"

def execute_mock_sql(sql_query: str, table_name: str) -> List[Dict[str, Any]]:
    """Execute SQL query against mock database"""
    try:
        if table_name not in MOCK_DATABASES:
            return []
        
        data = MOCK_DATABASES[table_name].copy()
        sql_lower = sql_query.lower()
        
        # Simple SQL parsing for demo purposes
        # Filter by WHERE conditions
        if "where" in sql_lower:
            # Handle fraud risk score filtering
            if "overall_fraud_risk_score >" in sql_lower:
                import re
                numbers = re.findall(r'overall_fraud_risk_score > (\d+(?:\.\d+)?)', sql_lower)
                if numbers:
                    threshold = float(numbers[0])
                    data = [row for row in data if row.get('overall_fraud_risk_score', 0) > threshold]
            
            # Handle risk level filtering
            if "risk_level = 'high'" in sql_lower:
                data = [row for row in data if row.get('risk_level') == 'high']
            
            # Handle income filtering
            if "annual_income >" in sql_lower:
                import re
                numbers = re.findall(r'annual_income > (\d+)', sql_lower)
                if numbers:
                    threshold = int(numbers[0])
                    data = [row for row in data if row.get('annual_income', 0) > threshold]
            
            # Handle FICO score filtering
            if "fico_score_8 <" in sql_lower:
                import re
                numbers = re.findall(r'fico_score_8 < (\d+)', sql_lower)
                if numbers:
                    threshold = int(numbers[0])
                    data = [row for row in data if row.get('fico_score_8', 0) < threshold]
            
            # Handle utilization rate filtering
            if "utilization_rate >" in sql_lower:
                import re
                numbers = re.findall(r'utilization_rate > ([\d.]+)', sql_lower)
                if numbers:
                    threshold = float(numbers[0])
                    data = [row for row in data if row.get('utilization_rate', 0) > threshold]
        
        # Handle ORDER BY
        if "order by" in sql_lower:
            if "overall_fraud_risk_score desc" in sql_lower:
                data.sort(key=lambda x: x.get('overall_fraud_risk_score', 0), reverse=True)
            elif "annual_income desc" in sql_lower:
                data.sort(key=lambda x: x.get('annual_income', 0), reverse=True)
            elif "fico_score_8 asc" in sql_lower:
                data.sort(key=lambda x: x.get('fico_score_8', 0))
            elif "utilization_rate desc" in sql_lower:
                data.sort(key=lambda x: x.get('utilization_rate', 0), reverse=True)
        
        # Handle LIMIT
        if "limit" in sql_lower:
            import re
            numbers = re.findall(r'limit (\d+)', sql_lower)
            if numbers:
                limit = int(numbers[0])
                data = data[:limit]
        
        return data
        
    except Exception as e:
        logger.error(f"Error executing mock SQL: {e}")
        return []

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Banking Agent Backend API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "azure_openai_configured": bool(os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_KEY"))
    }

@app.post("/api/text-to-sql", response_model=QueryResult)
async def text_to_sql(request: TextToSQLRequest):
    """Convert natural language to SQL and execute it"""
    start_time = datetime.now()
    
    try:
        # Convert text to SQL
        sql_query = await convert_text_to_sql(
            request.natural_language_query,
            request.table_name,
            request.fields
        )
        
        # Execute the SQL query (mock execution for demo)
        data = execute_mock_sql(sql_query, request.table_name)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        return QueryResult(
            success=True,
            sql=sql_query,
            data=data,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error in text-to-sql endpoint: {e}")
        return QueryResult(
            success=False,
            error=str(e)
        )

@app.post("/api/query", response_model=QueryResult)
async def execute_sql(request: SQLQueryRequest):
    """Execute a SQL query directly"""
    start_time = datetime.now()
    
    try:
        # For demo purposes, we'll use a default table if not specified
        table_name = request.table_name or "customer_demographics"
        
        # Execute the SQL query (mock execution for demo)
        data = execute_mock_sql(request.sql, table_name)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QueryResult(
            success=True,
            sql=request.sql,
            data=data,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error executing SQL: {e}")
        return QueryResult(
            success=False,
            error=str(e)
        )

@app.get("/api/datasources", response_model=List[DataSource])
async def get_data_sources():
    """Get available data sources"""
    return SAMPLE_DATA_SOURCES

@app.get("/api/sample/{table_name}")
async def get_sample_data(table_name: str, limit: int = 5):
    """Get sample data from a specific table"""
    try:
        if table_name in MOCK_DATABASES:
            data = MOCK_DATABASES[table_name][:limit]
            return {"data": data, "count": len(data)}
        else:
            return {"data": [], "count": 0, "error": f"Table {table_name} not found"}
    except Exception as e:
        logger.error(f"Error getting sample data: {e}")
        return {"data": [], "count": 0, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Banking Agent Backend on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=debug)
