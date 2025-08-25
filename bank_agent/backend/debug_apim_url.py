#!/usr/bin/env python3
"""
Debug script to test APIM URL construction.
"""

import asyncio
import os
import httpx
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

async def test_apim_urls():
    """Test different URL constructions for APIM."""
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    print("🔍 Testing APIM URL Constructions")
    print("=" * 50)
    print(f"Base endpoint: {endpoint}")
    print(f"Deployment: {deployment_name}")
    print(f"API Version: {api_version}")
    print()
    
    # Test different URL constructions
    test_cases = [
        {
            "name": "Original (with /ai/)",
            "url": f"{endpoint.rstrip('/')}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        },
        {
            "name": "Without /ai/",
            "url": f"{endpoint.replace('/ai/', '').rstrip('/')}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        },
        {
            "name": "Direct to /ai/",
            "url": f"{endpoint.rstrip('/')}/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        },
        {
            "name": "Base only",
            "url": f"{endpoint.replace('/ai/', '').rstrip('/')}/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        }
    ]
    
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
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    for test_case in test_cases:
        print(f"🧪 Testing: {test_case['name']}")
        print(f"  URL: {test_case['url']}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(test_case['url'], json=data, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    print(f"  ✅ SUCCESS: {content}")
                else:
                    print(f"  ❌ FAILED: Status {response.status_code}")
                    print(f"     Error: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_apim_urls())
