#!/usr/bin/env python3
"""
Test script to diagnose APIM connection issues
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="/Users/kanavkahol/work/neurostack/.env")

async def test_apim_connection():
    """Test APIM connection and configuration"""
    print("🔍 Testing APIM Connection...")
    print("=" * 50)
    
    # Get environment variables
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    print(f"📍 Endpoint: {endpoint}")
    print(f"🔑 API Key: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else 'NOT SET'}")
    print(f"🤖 Deployment: {deployment_name}")
    print(f"📅 API Version: {api_version}")
    print()
    
    if not all([endpoint, api_key, deployment_name]):
        print("❌ Missing required environment variables!")
        return False
    
    # Test basic connectivity
    try:
        base_endpoint = endpoint.rstrip('/')
        test_url = f"{base_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": api_key,
            "User-Agent": "BankingAgent/1.0"
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Say 'Hello World'"
                }
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        print(f"🌐 Testing URL: {test_url}")
        print(f"📋 Headers: {headers}")
        print(f"📄 Data: {data}")
        print()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(test_url, json=data, headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            print(f"📄 Response Body: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✅ APIM connection successful!")
                return True
            else:
                print(f"❌ APIM connection failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ APIM connection error: {e}")
        return False

async def test_mock_fallback():
    """Test the mock SQL generation fallback"""
    print("\n🧪 Testing Mock SQL Generation Fallback...")
    print("=" * 50)
    
    # Import the function from main.py
    import sys
    sys.path.append('.')
    
    try:
        from main import generate_mock_sql
        
        test_cases = [
            ("Show me customers with income above $100,000", "customer_demographics", ["customer_id", "first_name", "last_name", "annual_income"]),
            ("Find customers with FICO score below 650", "credit_bureau_data", ["customer_id", "fico_score_8", "fico_score_9"]),
            ("Show me customers with utilization rate above 80%", "internal_banking_data", ["customer_id", "utilization_rate", "current_balance"])
        ]
        
        for query, table, fields in test_cases:
            sql = generate_mock_sql(query, table, fields)
            print(f"📝 Query: {query}")
            print(f"🔍 Generated SQL: {sql}")
            print()
            
        print("✅ Mock SQL generation working!")
        return True
        
    except Exception as e:
        print(f"❌ Mock SQL generation error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Banking Agent APIM Diagnostics")
    print("=" * 50)
    
    # Test APIM connection
    apim_ok = await test_apim_connection()
    
    # Test mock fallback
    mock_ok = await test_mock_fallback()
    
    print("\n📊 Test Results:")
    print(f"APIM Connection: {'✅ PASS' if apim_ok else '❌ FAIL'}")
    print(f"Mock Fallback: {'✅ PASS' if mock_ok else '❌ FAIL'}")
    
    if not apim_ok:
        print("\n💡 Recommendations:")
        print("1. Check your .env file configuration")
        print("2. Verify APIM endpoint URL format")
        print("3. Ensure deployment name is correct")
        print("4. Check API key permissions")
        print("5. The app will use mock SQL generation as fallback")

if __name__ == "__main__":
    asyncio.run(main())
