#!/usr/bin/env python3
"""
Test script to verify APIM endpoint usage in reasoning layer.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the neurostack src to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from neurostack.core.reasoning import ReasoningEngine
from neurostack.core.agents import AgentContext

async def test_reasoning_engine_apim():
    """Test if the reasoning engine is using APIM endpoint correctly."""
    
    print("🧪 Testing Reasoning Engine APIM Integration")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Environment Variables:")
    print(f"  AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT', 'NOT SET')}")
    print(f"  AZURE_OPENAI_KEY: {'***' + os.getenv('AZURE_OPENAI_KEY', 'NOT SET')[-4:] if os.getenv('AZURE_OPENAI_KEY') else 'NOT SET'}")
    print(f"  AZURE_OPENAI_DEPLOYMENT_NAME: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'NOT SET')}")
    print(f"  AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION', 'NOT SET')}")
    
    # Check if this is an APIM endpoint
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    is_apim = 'azure-api.net' in endpoint if endpoint else False
    print(f"  Is APIM Endpoint: {is_apim}")
    print()
    
    if not all([os.getenv('AZURE_OPENAI_ENDPOINT'), os.getenv('AZURE_OPENAI_KEY'), os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')]):
        print("❌ Missing required Azure OpenAI environment variables")
        return False
    
    try:
        # Initialize reasoning engine
        print("🔧 Initializing Reasoning Engine...")
        reasoning_engine = ReasoningEngine(model="gpt-4", temperature=0.7)
        
        # Check what type of client was created
        client_type = type(reasoning_engine.llm_client).__name__
        print(f"  Client Type: {client_type}")
        
        if client_type == "AzureOpenAIClient":
            print("✅ Reasoning engine is using Azure OpenAI client")
        else:
            print(f"⚠️  Reasoning engine is using {client_type} instead of AzureOpenAIClient")
        
        # Test a simple prompt
        print("\n🧠 Testing reasoning engine with simple prompt...")
        test_prompt = "What is 2 + 2? Please respond with just the number."
        
        context = AgentContext(
            user_id="test_user",
            tenant_id="test_tenant",
            metadata={"test": True}
        )
        
        response = await reasoning_engine.process(test_prompt, context)
        print(f"  Response: {response}")
        
        if "Error:" in response:
            print("❌ Reasoning engine returned an error")
            return False
        else:
            print("✅ Reasoning engine responded successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error testing reasoning engine: {str(e)}")
        return False

async def test_neurostack_integration_apim():
    """Test if the NeuroStack integration is using APIM endpoint correctly."""
    
    print("\n🧪 Testing NeuroStack Integration APIM")
    print("=" * 50)
    
    try:
        # Import the integration
        from neurostack_integration import NeuroStackBankingIntegration
        
        print("🔧 Initializing NeuroStack Integration...")
        integration = NeuroStackBankingIntegration(tenant_id="test_tenant")
        
        # Test the reasoning engine through the integration
        print("🧠 Testing reasoning through integration...")
        test_prompt = "Say 'Hello World'"
        
        response = await integration.generate_response(test_prompt)
        print(f"  Response: {response}")
        
        if "Error:" in response or "encountered an error" in response:
            print("❌ NeuroStack integration returned an error")
            return False
        else:
            print("✅ NeuroStack integration responded successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error testing NeuroStack integration: {str(e)}")
        return False

async def test_direct_apim_call():
    """Test direct APIM call to compare with NeuroStack integration."""
    
    print("\n🧪 Testing Direct APIM Call")
    print("=" * 50)
    
    try:
        import httpx
        
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        # Use the same URL construction as the reasoning engine
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
                    "role": "user",
                    "content": "Say 'Hello World'"
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        print(f"  URL: {url}")
        print(f"  Headers: {headers}")
        print(f"  Data: {data}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data, headers=headers)
            
            print(f"  Status Code: {response.status_code}")
            print(f"  Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"  ✅ SUCCESS: {content}")
                return True
            else:
                print(f"  ❌ FAILED: {response.text}")
                return False
                
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting APIM Endpoint Tests for Reasoning Layer")
    print()
    
    # Test 1: Direct reasoning engine
    success1 = await test_reasoning_engine_apim()
    
    # Test 2: Direct APIM call
    success2 = await test_direct_apim_call()
    
    # Test 3: NeuroStack integration
    success3 = await test_neurostack_integration_apim()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Reasoning Engine: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"  Direct APIM Call: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"  NeuroStack Integration: {'✅ PASS' if success3 else '❌ FAIL'}")
    
    if success1 and success2 and success3:
        print("\n🎉 All tests passed! APIM endpoint is working correctly in reasoning layer.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    # Load environment variables
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        print(f"📁 Loading environment from: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print("⚠️  No .env file found")
    
    print()
    asyncio.run(main())
