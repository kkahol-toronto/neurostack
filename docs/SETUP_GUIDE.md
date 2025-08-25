# NeuroStack Setup Guide

This guide will walk you through setting up NeuroStack for development, including all required Azure resources and local services.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Environment](#local-development-environment)
3. [Azure Resources Setup](#azure-resources-setup)
4. [Local Services Setup](#local-services-setup)
5. [Environment Configuration](#environment-configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- **Python 3.11+** installed on your system
- **Git** for version control
- **Azure CLI** installed and authenticated
- **Docker** (optional, for local services)
- **Azure Subscription** with billing enabled

## Local Development Environment

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd neurostack
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
pip install python-dotenv
```

## Azure Resources Setup

### 🎯 **Minimum Required Setup**

For basic NeuroStack development, you only need:

1. **Azure OpenAI Service** - For LLM capabilities
2. **Basic Environment Settings** - LOG_LEVEL, etc.

Everything else is optional and can be added as needed.

### 1. Azure OpenAI Service - Required

**Purpose**: Provides LLM capabilities (GPT models)

#### Option A: Direct Connection (Recommended for Development)

1. **Create Azure OpenAI Resource**:
   ```bash
   az cognitiveservices account create \
     --name "your-openai-name" \
     --resource-group "your-resource-group" \
     --kind "OpenAI" \
     --sku "S0" \
     --location "eastus"
   ```

2. **Get OpenAI Endpoint**:
   ```bash
   az cognitiveservices account show --name "your-openai-name" --resource-group "your-resource-group" --query "properties.endpoint" -o tsv
   ```
   - **Result**: `https://your-openai-name.openai.azure.com/`
   - **Use as**: `AZURE_OPENAI_ENDPOINT`

3. **Get OpenAI Key**:
   ```bash
   az cognitiveservices account keys list --name "your-openai-name" --resource-group "your-resource-group" --query "key1" -o tsv
   ```
   - **Use as**: `AZURE_OPENAI_KEY`

4. **Deploy GPT Model**:
   - Go to Azure Portal → Your OpenAI Resource → Model deployments
   - Deploy `gpt-4.1` or `gpt-5.0`
   - Note the deployment name (e.g., `gpt-4.1`)

#### Option B: Azure API Management (APIM) - Enterprise Only

**Purpose**: Acts as a gateway for load balancing, rate limiting, and monitoring

**When to use APIM**:
- Multiple Azure OpenAI instances
- Enterprise rate limiting requirements
- Centralized API management
- Advanced monitoring and analytics

**Setup Steps**:

1. **Create APIM Instance**:
   ```bash
   az apim create \
     --name "your-apim-name" \
     --resource-group "your-resource-group" \
     --publisher-name "Your Name" \
     --publisher-email "your-email@domain.com" \
     --sku-name "Developer"
   ```

2. **Get APIM Endpoint**:
   ```bash
   az apim show --name "your-apim-name" --resource-group "your-resource-group" --query "gatewayUrl" -o tsv
   ```
   - **Result**: `https://your-apim-name.azure-api.net`
   - **Use as**: `AZURE_OPENAI_ENDPOINT`

3. **Get APIM Key**:
   ```bash
   az apim list-keys --name "your-apim-name" --resource-group "your-resource-group" --query "primaryKey" -o tsv
   ```
   - **Use as**: `AZURE_OPENAI_KEY`

4. **Configure APIM to Route to OpenAI**:
   - In APIM, create an API that routes to your OpenAI endpoint
   - Base URL: `https://your-openai-name.openai.azure.com/`
   - Add `/openai/deployments/{deployment-name}/chat/completions` operation

### 2. Azure Cognitive Services - Optional

**Purpose**: Provides embeddings and other AI services

#### Option A: Direct Connection (Recommended for Development)

1. **Create Cognitive Services Resource**:
   ```bash
   az cognitiveservices account create \
     --name "your-cognitive-name" \
     --resource-group "your-resource-group" \
     --kind "CognitiveServices" \
     --sku "S0" \
     --location "eastus"
   ```

2. **Get Endpoint and Key**:
   ```bash
   # Get endpoint
   az cognitiveservices account show --name "your-cognitive-name" --resource-group "your-resource-group" --query "properties.endpoint" -o tsv
   
   # Get key
   az cognitiveservices account keys list --name "your-cognitive-name" --resource-group "your-resource-group" --query "key1" -o tsv
   ```

#### Option B: Through APIM (Enterprise Only)

If you're using APIM, configure it to route to your Cognitive Services endpoint.



### 4. Azure Functions - Optional (Advanced)

**Purpose**: Serverless computing for agent workflows

**When you need it**:
- Deploying agents as serverless functions
- Scaling agent workloads automatically
- Event-driven agent execution

#### Setup Steps:

1. **Create Function App**:
   ```bash
   az functionapp create \
     --name "neurostack-function" \
     --resource-group "your-resource-group" \
     --consumption-plan-location "eastus" \
     --runtime "python" \
     --runtime-version "3.11" \
     --functions-version "4" \
     --storage-account "yourstorageaccount"
   ```

2. **Get Function URL**:
   ```bash
   az functionapp show --name "neurostack-function" --resource-group "your-resource-group" --query "defaultHostName" -o tsv
   ```
   - **Result**: `neurostack-function.azurewebsites.net`
   - **Use as**: `AZURE_FUNCTIONS_URL`

3. **Get Function Key**:
   ```bash
   az functionapp keys list --name "neurostack-function" --resource-group "your-resource-group" --query "functionKeys.default" -o tsv
   ```
   - **Use as**: `AZURE_FUNCTIONS_KEY`

### 5. Azure Storage - Optional (File Operations)

**Purpose**: File storage for agents and data

**When you need it**:
- Storing and retrieving files (documents, images, etc.)
- Agent file processing workflows
- Data persistence for large files

#### Setup Steps:

1. **Create Storage Account**:
   ```bash
   az storage account create \
     --name "neurostackstorage" \
     --resource-group "your-resource-group" \
     --location "eastus" \
     --sku "Standard_LRS"
   ```

2. **Get Connection String**:
   ```bash
   az storage account show-connection-string --name "neurostackstorage" --resource-group "your-resource-group" --query "connectionString" -o tsv
   ```
   - **Use as**: `AZURE_STORAGE_CONNECTION_STRING`

3. **Create Container**:
   ```bash
   az storage container create --name "neurostack-data" --account-name "neurostackstorage"
   ```
   - **Use as**: `AZURE_STORAGE_CONTAINER=neurostack-data`

### 6. Azure Service Bus - Optional (Advanced Messaging)

**Purpose**: Messaging between agents

**When you need it**:
- Multi-agent communication systems
- Event-driven architectures
- Distributed agent workflows

#### Setup Steps:

1. **Create Service Bus Namespace**:
   ```bash
   az servicebus namespace create \
     --name "neurostack-bus" \
     --resource-group "your-resource-group" \
     --location "eastus" \
     --sku "Standard"
   ```

2. **Get Connection String**:
   ```bash
   az servicebus namespace authorization-rule keys list \
     --namespace-name "neurostack-bus" \
     --resource-group "your-resource-group" \
     --name "RootManageSharedAccessKey" \
     --query "primaryConnectionString" -o tsv
   ```
   - **Use as**: `AZURE_SERVICE_BUS_CONNECTION_STRING`
   - **Use as**: `AZURE_SERVICE_BUS_NAMESPACE=neurostack-bus`

## Local Services Setup

### 1. Redis - Optional (Performance Enhancement)

**Purpose**: Caching and session management

**When you need it**:
- High-performance caching for agent responses
- Session management for web applications
- Performance optimization for frequent operations

#### Option A: Docker (Recommended)

```bash
# Pull and run Redis container
docker run -d --name redis-neurostack -p 6379:6379 redis:7-alpine

# Test connection
docker exec -it redis-neurostack redis-cli ping
# Should return: PONG
```

#### Option B: Local Installation

**macOS**:
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Windows**:
- Download from https://redis.io/download
- Or use WSL2 with Ubuntu

#### Verify Redis Connection:
```bash
redis-cli ping
# Should return: PONG
```

### 2. PostgreSQL - Optional (Data Persistence)

**Purpose**: Persistent data storage

**When you need it**:
- Storing agent conversation history
- Persistent memory across sessions
- Multi-user data isolation

#### Option A: Docker (Recommended)

```bash
# Create PostgreSQL container
docker run -d --name postgres-neurostack \
  -e POSTGRES_DB=neurostack \
  -e POSTGRES_USER=neurostack \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15

# Test connection
docker exec -it postgres-neurostack psql -U neurostack -d neurostack -c "SELECT version();"
```

#### Option B: Local Installation

**macOS**:
```bash
brew install postgresql@15
brew services start postgresql@15

# Create database and user
createdb neurostack
psql postgres -c "CREATE USER neurostack WITH PASSWORD 'your_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE neurostack TO neurostack;"
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Switch to postgres user and create database
sudo -u postgres psql -c "CREATE DATABASE neurostack;"
sudo -u postgres psql -c "CREATE USER neurostack WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE neurostack TO neurostack;"
```

**Windows**:
- Download from https://www.postgresql.org/download/windows/
- Or use WSL2 with Ubuntu

## Environment Configuration

### 1. Create Environment File

Copy the template and configure your values:

```bash
cp env.template .env
```

### 2. Configure Environment Variables

#### Minimum Required Configuration

For basic NeuroStack development, you only need these:

```bash
# Core Configuration (Required)
LOG_LEVEL=INFO
DEBUG=true

# Azure OpenAI (Required) - Direct Connection
AZURE_OPENAI_ENDPOINT=https://your-openai-name.openai.azure.com/
AZURE_OPENAI_KEY=your_openai_key_here
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

#### Optional Enhanced Configuration

Add these as needed for advanced features:

```bash
# RAG Configuration (Optional)
RAG_MAX_CONTEXT_TOKENS=4000
SYSTEM_PROMPT="You are a helpful AI assistant powered by NeuroStack."

# Azure Cognitive Services (Optional) - Direct Connection
AZURE_COGNITIVE_SERVICES_ENDPOINT=https://your-cognitive-name.cognitiveservices.azure.com/
AZURE_COGNITIVE_SERVICES_KEY=your_cognitive_key_here

# Alternative: If using APIM (Enterprise)
# AZURE_OPENAI_ENDPOINT=https://your-apim-name.azure-api.net/ai/
# AZURE_OPENAI_KEY=your_apim_key_here
# AZURE_COGNITIVE_SERVICES_ENDPOINT=https://your-apim-name.azure-api.net/cognitive/
# AZURE_COGNITIVE_SERVICES_KEY=your_apim_key_here

# Azure Functions (Optional) - Serverless computing
AZURE_FUNCTIONS_URL=https://neurostack-function.azurewebsites.net
AZURE_FUNCTIONS_KEY=your_function_key_here

# Azure Storage (Optional) - File storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=neurostackstorage;AccountKey=your_key;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=neurostack-data

# Azure Service Bus (Optional) - Messaging
AZURE_SERVICE_BUS_CONNECTION_STRING=Endpoint=sb://neurostack-bus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=your_key
AZURE_SERVICE_BUS_NAMESPACE=neurostack-bus

# Local Services (Optional) - Performance & Persistence
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://neurostack:your_password@localhost:5432/neurostack
```

## Verification

### 1. Run Setup Check

```bash
python debug/check_neurostack_setup.py
```

Expected output:
```
🎉 READY FOR NEUROSTACK DEVELOPMENT!
   ✅ Azure OpenAI configured
   ✅ Basic settings configured
   🚀 Optional services: [list of configured services]
```

### 2. Test NeuroStack Import

```bash
python -c "from neurostack import Agent, AgentConfig; print('✅ NeuroStack imports successfully')"
```

### 3. Run Example

```bash
python examples/simple_agent_example.py
```

Expected output:
```
🎉 Example completed successfully!
```

## Troubleshooting

### Common Issues

#### 1. Azure OpenAI Connection Issues

**Error**: `401 Unauthorized`
- **Direct Connection**: Check your Azure OpenAI key and endpoint URL
- **APIM Connection**: Check your APIM key and ensure APIM is properly routing to your OpenAI resource

**Error**: `404 Not Found`
- **Solution**: Verify the model deployment name in your OpenAI resource
- **Check**: Ensure the deployment is active and accessible

**Error**: `Invalid endpoint`
- **Direct Connection**: Use format: `https://your-openai-name.openai.azure.com/`
- **APIM Connection**: Use format: `https://your-apim-name.azure-api.net/ai/`

#### 2. Redis Connection Issues

**Error**: `Connection refused`
- **Solution**: Start Redis service
- **Docker**: `docker start redis-neurostack`
- **Local**: `brew services start redis` (macOS) or `sudo systemctl start redis-server` (Linux)

#### 3. PostgreSQL Connection Issues

**Error**: `password authentication failed`
- **Solution**: Check username/password in DATABASE_URL
- **Verify**: Ensure user has proper permissions

**Error**: `connection refused`
- **Solution**: Start PostgreSQL service
- **Docker**: `docker start postgres-neurostack`
- **Local**: `brew services start postgresql` (macOS) or `sudo systemctl start postgresql` (Linux)

#### 4. Azure Functions Issues

**Error**: `Function not found`
- **Solution**: Deploy your functions to the Function App
- **Check**: Verify the function URL and key are correct

### Getting Help

1. **Check Logs**: Set `LOG_LEVEL=DEBUG` for detailed logging
2. **Verify Environment**: Run `python debug/check_neurostack_setup.py`
3. **Test Individual Services**: Use the test scripts in the `examples/` folder
4. **Azure Portal**: Check resource health and metrics in Azure Portal

## Next Steps

Once your setup is complete:

1. **Explore Examples**: Check out the examples in the `examples/` folder
2. **Build Your First Agent**: Start with a simple agent using the base classes
3. **Integrate Services**: Gradually add Azure services as needed
4. **Scale Up**: Use Azure Functions and Service Bus for production workloads

## Cost Optimization

### Azure Resources Cost Management

1. **Use Consumption Plans**: Functions and some services offer pay-per-use pricing
2. **Monitor Usage**: Set up Azure Cost Alerts
3. **Development vs Production**: Use different resource groups for different environments
4. **Clean Up**: Delete unused resources to avoid charges

### Local Development Tips

1. **Use Docker**: Easier to manage local services
2. **Environment Isolation**: Keep development and production configurations separate
3. **Regular Updates**: Keep dependencies and services updated

---

**Need Help?** Check the troubleshooting section or create an issue in the repository.
