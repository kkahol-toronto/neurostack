#!/usr/bin/env python3
"""
Simple test for multi-table text-to-SQL functionality
"""

import requests
import json

def test_simple_multi_table():
    """Test a simple multi-table query"""
    
    print("🧪 Testing Simple Multi-Table Query")
    print("=" * 40)
    
    # Test data
    payload = {
        "natural_language_query": "Show me customers with high income and low credit utilization",
        "tables": [
            {
                "table_name": "customer_demographics",
                "fields": ["customer_id", "first_name", "last_name", "annual_income"]
            },
            {
                "table_name": "internal_banking_data", 
                "fields": ["customer_id", "utilization_rate", "current_credit_limit"]
            }
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/text-to-sql",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Generated SQL: {result['sql']}")
            print(f"Execution time: {result.get('execution_time', 0):.2f}ms")
            
            if "JOIN" in result['sql'].upper():
                print("🔗 Multi-table JOIN detected!")
            else:
                print("⚠️  Single table query")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_single_table():
    """Test a single table query for backward compatibility"""
    
    print("\n🔄 Testing Single Table Query (Backward Compatibility)")
    print("=" * 50)
    
    payload = {
        "natural_language_query": "Show me customers with income above $100,000",
        "table_name": "customer_demographics",
        "fields": ["customer_id", "first_name", "last_name", "annual_income"]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/text-to-sql",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Generated SQL: {result['sql']}")
            print(f"Execution time: {result.get('execution_time', 0):.2f}ms")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_simple_multi_table()
    test_single_table()
    print("\n🎉 Testing completed!")
