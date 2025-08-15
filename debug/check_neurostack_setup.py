#!/usr/bin/env python3
"""
NeuroStack Development Setup Check

This script checks if all required environment variables are configured
for NeuroStack development with Azure OpenAI.
"""

import os
from dotenv import load_dotenv

def check_neurostack_setup():
    print("🔍 NeuroStack Development Setup Check")
    print("=" * 50)
    
    # Load .env file
    load_dotenv()
    
    # Check Azure OpenAI (Primary LLM)
    print("🤖 Azure OpenAI Configuration:")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
    azure_openai_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    # Determine connection type
    connection_type = "Direct" if azure_openai_endpoint and "openai.azure.com" in azure_openai_endpoint else "APIM" if azure_openai_endpoint and "azure-api.net" in azure_openai_endpoint else "Unknown"
    
    print(f"   Endpoint: {'✅' if azure_openai_endpoint else '❌'} {azure_openai_endpoint or 'Not set'}")
    print(f"   Connection Type: {'✅' if connection_type != 'Unknown' else '❌'} {connection_type}")
    print(f"   API Key: {'✅' if azure_openai_key else '❌'} {'Set' if azure_openai_key else 'Not set'}")
    print(f"   API Version: {'✅' if azure_openai_version else '❌'} {azure_openai_version or 'Not set'}")
    
    # Check Azure Cognitive Services
    print("\n🧠 Azure Cognitive Services:")
    cog_endpoint = os.getenv("AZURE_COGNITIVE_SERVICES_ENDPOINT")
    cog_key = os.getenv("AZURE_COGNITIVE_SERVICES_KEY")
    print(f"   Endpoint: {'✅' if cog_endpoint else '❌'} {cog_endpoint or 'Not set'}")
    print(f"   API Key: {'✅' if cog_key else '❌'} {'Set' if cog_key else 'Not set'}")
    
    # Check Azure Functions
    print("\n⚡ Azure Functions:")
    func_url = os.getenv("AZURE_FUNCTIONS_URL")
    func_key = os.getenv("AZURE_FUNCTIONS_KEY")
    print(f"   URL: {'✅' if func_url else '❌'} {func_url or 'Not set'}")
    print(f"   Key: {'✅' if func_key else '❌'} {'Set' if func_key else 'Not set'}")
    
    # Check Azure Storage
    print("\n💾 Azure Storage:")
    storage_conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    storage_container = os.getenv("AZURE_STORAGE_CONTAINER")
    print(f"   Connection: {'✅' if storage_conn else '❌'} {'Set' if storage_conn else 'Not set'}")
    print(f"   Container: {'✅' if storage_container else '❌'} {storage_container or 'Not set'}")
    
    # Check Azure Service Bus
    print("\n🚌 Azure Service Bus:")
    sb_conn = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
    sb_namespace = os.getenv("AZURE_SERVICE_BUS_NAMESPACE")
    print(f"   Connection: {'✅' if sb_conn else '❌'} {'Set' if sb_conn else 'Not set'}")
    print(f"   Namespace: {'✅' if sb_namespace else '❌'} {sb_namespace or 'Not set'}")
    
    # Check Local Services
    print("\n🏠 Local Services:")
    redis_url = os.getenv("REDIS_URL")
    db_url = os.getenv("DATABASE_URL")
    print(f"   Redis: {'✅' if redis_url else '❌'} {redis_url or 'Not set'}")
    print(f"   Database: {'✅' if db_url else '❌'} {'Set' if db_url else 'Not set'}")
    
    # Check Basic Settings
    print("\n⚙️  Basic Settings:")
    log_level = os.getenv("LOG_LEVEL", "Not set")
    debug = os.getenv("DEBUG", "Not set")
    print(f"   LOG_LEVEL: {'✅' if log_level != 'Not set' else '❌'} {log_level}")
    print(f"   DEBUG: {'✅' if debug != 'Not set' else '❌'} {debug}")
    
    # Check RAG Configuration
    print("\n📚 RAG Configuration:")
    rag_tokens = os.getenv("RAG_MAX_CONTEXT_TOKENS")
    system_prompt = os.getenv("SYSTEM_PROMPT")
    print(f"   Max Context Tokens: {'✅' if rag_tokens else '❌'} {rag_tokens or 'Not set'}")
    print(f"   System Prompt: {'✅' if system_prompt else '❌'} {'Set' if system_prompt else 'Not set'}")
    
    # Determine readiness
    print("\n" + "=" * 50)
    
    # Minimum requirements check
    has_azure_openai = azure_openai_endpoint and azure_openai_key
    has_basic_settings = log_level != 'Not set'
    
    if has_azure_openai and has_basic_settings:
        print("🎉 READY FOR NEUROSTACK DEVELOPMENT!")
        print("   ✅ Azure OpenAI configured")
        print("   ✅ Basic settings configured")
        
        # Check optional services
        optional_services = []
        if cog_endpoint and cog_key:
            optional_services.append("Cognitive Services")
        if func_url and func_key:
            optional_services.append("Azure Functions")
        if storage_conn:
            optional_services.append("Azure Storage")
        if sb_conn:
            optional_services.append("Service Bus")
        if redis_url:
            optional_services.append("Redis")
        if db_url:
            optional_services.append("Database")
            
        if optional_services:
            print(f"   🚀 Optional services: {', '.join(optional_services)}")
        else:
            print("   ℹ️  No optional services configured (this is fine for basic development)")
            
    else:
        print("❌ NOT READY - Missing required configuration:")
        if not has_azure_openai:
            print("   ❌ Azure OpenAI endpoint and key required")
        if not has_basic_settings:
            print("   ❌ LOG_LEVEL setting required")
    
    print("\n📋 Next Steps:")
    if has_azure_openai and has_basic_settings:
        print("   1. Run: python examples/simple_agent_example.py")
        print("   2. Test your Azure OpenAI connection")
        print("   3. Start building your NeuroStack agents!")
    else:
        print("   1. Configure Azure OpenAI endpoint and key")
        print("   2. Set LOG_LEVEL=INFO")
        print("   3. Run this check again")
    
    print("\n🔧 Test Commands:")
    print("   python -c \"from neurostack import Agent, AgentConfig; print('✅ NeuroStack imports successfully')\"")
    print("   python examples/simple_agent_example.py")

if __name__ == "__main__":
    check_neurostack_setup()
