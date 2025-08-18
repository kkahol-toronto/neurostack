#!/usr/bin/env python3
"""
Test script for multi-table text-to-SQL functionality
"""

import requests
import json

def test_multi_table_text_to_sql():
    """Test the multi-table text-to-SQL endpoint"""
    
    # Test data
    test_cases = [
        {
            "name": "Customer Demographics + Banking Data",
            "query": "Show me customers with high income and low credit utilization",
            "tables": [
                {
                    "table_name": "customer_demographics",
                    "fields": ["customer_id", "first_name", "last_name", "annual_income", "employment_status"]
                },
                {
                    "table_name": "internal_banking_data", 
                    "fields": ["customer_id", "utilization_rate", "current_credit_limit", "tenure_months"]
                }
            ]
        },
        {
            "name": "Customer Demographics + Credit Bureau Data",
            "query": "Find customers with high income and good credit scores",
            "tables": [
                {
                    "table_name": "customer_demographics",
                    "fields": ["customer_id", "first_name", "last_name", "annual_income"]
                },
                {
                    "table_name": "credit_bureau_data",
                    "fields": ["customer_id", "fico_score_8", "total_accounts_bureau"]
                }
            ]
        },
        {
            "name": "All Three Tables",
            "query": "Show me high-risk customers with low income and high fraud scores",
            "tables": [
                {
                    "table_name": "customer_demographics",
                    "fields": ["customer_id", "first_name", "last_name", "annual_income"]
                },
                {
                    "table_name": "internal_banking_data",
                    "fields": ["customer_id", "utilization_rate", "current_balance"]
                },
                {
                    "table_name": "fraud_kyc_compliance",
                    "fields": ["customer_id", "overall_fraud_risk_score", "risk_level"]
                }
            ]
        }
    ]
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Multi-Table Text-to-SQL Functionality")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print(f"Tables: {[t['table_name'] for t in test_case['tables']]}")
        
        try:
            # Make the API request
            response = requests.post(
                f"{base_url}/api/text-to-sql",
                json={
                    "natural_language_query": test_case["query"],
                    "tables": test_case["tables"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print("✅ Success!")
                    print(f"Generated SQL: {result['sql']}")
                    print(f"Execution time: {result.get('execution_time', 0):.2f}ms")
                    
                    # Check if it's a JOIN query
                    if "JOIN" in result['sql'].upper():
                        print("🔗 Multi-table JOIN detected!")
                    else:
                        print("⚠️  Single table query (may need refinement)")
                else:
                    print("❌ Failed to generate SQL")
                    print(f"Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print("-" * 40)

def test_backward_compatibility():
    """Test backward compatibility with single table queries"""
    
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 40)
    
    # Test single table query (old format)
    try:
        response = requests.post(
            "http://localhost:8000/api/text-to-sql",
            json={
                "natural_language_query": "Show me customers with income above $100,000",
                "table_name": "customer_demographics",
                "fields": ["customer_id", "first_name", "last_name", "annual_income"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Backward compatibility works!")
                print(f"Generated SQL: {result['sql']}")
            else:
                print("❌ Backward compatibility failed")
                print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    # Test multi-table functionality
    test_multi_table_text_to_sql()
    
    # Test backward compatibility
    test_backward_compatibility()
    
    print("\n🎉 Testing completed!")
