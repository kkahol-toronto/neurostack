#!/usr/bin/env python3
"""
Demo script for the executeSQL FastAPI endpoint
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_execute_sql():
    """Test the executeSQL endpoint"""
    print("🚀 Testing executeSQL FastAPI Endpoint")
    print("=" * 50)
    
    # Test 1: Direct SQL execution
    print("\n1️⃣ Testing direct SQL execution...")
    payload = {
        "sql": "SELECT customer_id, first_name, last_name, annual_income FROM customer_demographics WHERE annual_income > 70000",
        "table_name": "customer_demographics"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Status: {response.status_code}")
            execution_time = data.get('execution_time', 0)
            if execution_time is not None:
                print(f"📊 Execution time: {execution_time:.2f}ms")
            else:
                print(f"📊 Execution time: N/A")
            print(f"📋 Results: {len(data.get('data', []))} records")
            print(f"🔍 SQL: {data.get('sql')}")
            print(f"📄 Data: {json.dumps(data.get('data', []), indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Text-to-SQL conversion and execution
    print("\n2️⃣ Testing text-to-SQL conversion and execution...")
    payload = {
        "natural_language_query": "Show me customers with high income above $80,000",
        "table_name": "customer_demographics",
        "fields": ["customer_id", "first_name", "last_name", "annual_income", "state"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/text-to-sql",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Status: {response.status_code}")
            execution_time = data.get('execution_time', 0)
            if execution_time is not None:
                print(f"📊 Execution time: {execution_time:.2f}ms")
            else:
                print(f"📊 Execution time: N/A")
            print(f"📋 Results: {len(data.get('data', []))} records")
            print(f"🔍 Generated SQL: {data.get('sql')}")
            print(f"📄 Data: {json.dumps(data.get('data', []), indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Health check
    print("\n3️⃣ Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def show_api_docs():
    """Show API documentation URLs"""
    print("\n📚 API Documentation")
    print("=" * 30)
    print(f"🔗 Swagger UI: {BASE_URL}/docs")
    print(f"🔗 ReDoc: {BASE_URL}/redoc")
    print(f"🔗 OpenAPI JSON: {BASE_URL}/openapi.json")

if __name__ == "__main__":
    test_execute_sql()
    show_api_docs()
