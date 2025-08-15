# Azure CLI Quick Reference for NeuroStack

This is a quick reference for Azure CLI commands used in setting up NeuroStack resources.

## Prerequisites

### Install Azure CLI
```bash
# macOS
brew install azure-cli

# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows
# Download from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
```

### Login to Azure
```bash
az login
```

### Set Default Subscription
```bash
# List subscriptions
az account list --output table

# Set default subscription
az account set --subscription "Your Subscription Name or ID"
```

## Resource Group Management

### Create Resource Group
```bash
az group create \
  --name "neurostack-rg" \
  --location "eastus"
```

### List Resource Groups
```bash
az group list --output table
```

### Delete Resource Group (Cleanup)
```bash
az group delete --name "neurostack-rg" --yes
```

## Azure API Management (APIM)

### Create APIM Instance
```bash
az apim create \
  --name "neurostack-apim" \
  --resource-group "neurostack-rg" \
  --publisher-name "Your Name" \
  --publisher-email "your-email@domain.com" \
  --sku-name "Developer"
```

### Get APIM Endpoint
```bash
az apim show \
  --name "neurostack-apim" \
  --resource-group "neurostack-rg" \
  --query "gatewayUrl" \
  --output tsv
```

### Get APIM Key
```bash
az apim list-keys \
  --name "neurostack-apim" \
  --resource-group "neurostack-rg" \
  --query "primaryKey" \
  --output tsv
```

### List APIM APIs
```bash
az apim api list \
  --service-name "neurostack-apim" \
  --resource-group "neurostack-rg"
```

## Azure OpenAI

### Create OpenAI Resource
```bash
az cognitiveservices account create \
  --name "neurostack-openai" \
  --resource-group "neurostack-rg" \
  --kind "OpenAI" \
  --sku "S0" \
  --location "eastus"
```

### Get OpenAI Endpoint
```bash
az cognitiveservices account show \
  --name "neurostack-openai" \
  --resource-group "neurostack-rg" \
  --query "properties.endpoint" \
  --output tsv
```

### Get OpenAI Key
```bash
az cognitiveservices account keys list \
  --name "neurostack-openai" \
  --resource-group "neurostack-rg" \
  --query "key1" \
  --output tsv
```

### List Model Deployments
```bash
az cognitiveservices account deployment list \
  --name "neurostack-openai" \
  --resource-group "neurostack-rg"
```

## Azure Cognitive Services

### Create Cognitive Services
```bash
az cognitiveservices account create \
  --name "neurostack-cognitive" \
  --resource-group "neurostack-rg" \
  --kind "CognitiveServices" \
  --sku "S0" \
  --location "eastus"
```

### Get Cognitive Services Endpoint
```bash
az cognitiveservices account show \
  --name "neurostack-cognitive" \
  --resource-group "neurostack-rg" \
  --query "properties.endpoint" \
  --output tsv
```

### Get Cognitive Services Key
```bash
az cognitiveservices account keys list \
  --name "neurostack-cognitive" \
  --resource-group "neurostack-rg" \
  --query "key1" \
  --output tsv
```

## Azure Functions

### Create Storage Account (Required for Functions)
```bash
az storage account create \
  --name "neurostackfuncstorage" \
  --resource-group "neurostack-rg" \
  --location "eastus" \
  --sku "Standard_LRS"
```

### Create Function App
```bash
az functionapp create \
  --name "neurostack-function" \
  --resource-group "neurostack-rg" \
  --consumption-plan-location "eastus" \
  --runtime "python" \
  --runtime-version "3.11" \
  --functions-version "4" \
  --storage-account "neurostackfuncstorage"
```

### Get Function URL
```bash
az functionapp show \
  --name "neurostack-function" \
  --resource-group "neurostack-rg" \
  --query "defaultHostName" \
  --output tsv
```

### Get Function Key
```bash
az functionapp keys list \
  --name "neurostack-function" \
  --resource-group "neurostack-rg" \
  --query "functionKeys.default" \
  --output tsv
```

### Deploy Function Code
```bash
# From your function code directory
az functionapp deployment source config-zip \
  --resource-group "neurostack-rg" \
  --name "neurostack-function" \
  --src "function-app.zip"
```

## Azure Storage

### Create Storage Account
```bash
az storage account create \
  --name "neurostackstorage" \
  --resource-group "neurostack-rg" \
  --location "eastus" \
  --sku "Standard_LRS"
```

### Get Storage Connection String
```bash
az storage account show-connection-string \
  --name "neurostackstorage" \
  --resource-group "neurostack-rg" \
  --query "connectionString" \
  --output tsv
```

### Create Storage Container
```bash
az storage container create \
  --name "neurostack-data" \
  --account-name "neurostackstorage"
```

### List Storage Containers
```bash
az storage container list \
  --account-name "neurostackstorage"
```

## Azure Service Bus

### Create Service Bus Namespace
```bash
az servicebus namespace create \
  --name "neurostack-bus" \
  --resource-group "neurostack-rg" \
  --location "eastus" \
  --sku "Standard"
```

### Get Service Bus Connection String
```bash
az servicebus namespace authorization-rule keys list \
  --namespace-name "neurostack-bus" \
  --resource-group "neurostack-rg" \
  --name "RootManageSharedAccessKey" \
  --query "primaryConnectionString" \
  --output tsv
```

### Create Service Bus Queue
```bash
az servicebus queue create \
  --namespace-name "neurostack-bus" \
  --resource-group "neurostack-rg" \
  --name "neurostack-queue"
```

### Create Service Bus Topic
```bash
az servicebus topic create \
  --namespace-name "neurostack-bus" \
  --resource-group "neurostack-rg" \
  --name "neurostack-topic"
```

## Monitoring and Logs

### List All Resources
```bash
az resource list \
  --resource-group "neurostack-rg" \
  --output table
```

### Get Resource Details
```bash
az resource show \
  --name "resource-name" \
  --resource-group "neurostack-rg" \
  --resource-type "Microsoft.CognitiveServices/accounts"
```

### View Activity Logs
```bash
az monitor activity-log list \
  --resource-group "neurostack-rg" \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-12-31T23:59:59Z"
```

## Cost Management

### Get Resource Costs
```bash
az consumption usage list \
  --billing-period-name "202401" \
  --resource-group "neurostack-rg"
```

### Set Budget Alert
```bash
az monitor action-group create \
  --name "neurostack-budget-alert" \
  --resource-group "neurostack-rg" \
  --short-name "budget-alert" \
  --action email "your-email@domain.com"
```

## Cleanup Commands

### Delete Specific Resource
```bash
az resource delete \
  --name "resource-name" \
  --resource-group "neurostack-rg" \
  --resource-type "Microsoft.CognitiveServices/accounts"
```

### Delete All Resources in Group
```bash
az group delete \
  --name "neurostack-rg" \
  --yes \
  --no-wait
```

## Useful Aliases

Add these to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
# Quick resource group operations
alias az-rg-list='az group list --output table'
alias az-rg-create='az group create --name "neurostack-rg" --location "eastus"'
alias az-rg-delete='az group delete --name "neurostack-rg" --yes'

# Quick resource operations
alias az-resources='az resource list --resource-group "neurostack-rg" --output table'
alias az-costs='az consumption usage list --resource-group "neurostack-rg"'

# Quick service operations
alias az-apim-url='az apim show --name "neurostack-apim" --resource-group "neurostack-rg" --query "gatewayUrl" --output tsv'
alias az-openai-key='az cognitiveservices account keys list --name "neurostack-openai" --resource-group "neurostack-rg" --query "key1" --output tsv'
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   az login
   az account set --subscription "Your Subscription"
   ```

2. **Resource Not Found**
   ```bash
   # Check if resource exists
   az resource show --name "resource-name" --resource-group "neurostack-rg"
   ```

3. **Permission Denied**
   ```bash
   # Check your role assignments
   az role assignment list --assignee "your-email@domain.com"
   ```

4. **Quota Exceeded**
   ```bash
   # Check current usage
   az vm list-usage --location "eastus"
   ```

### Get Help
```bash
# General help
az --help

# Command-specific help
az apim create --help

# Interactive mode
az interactive
```
