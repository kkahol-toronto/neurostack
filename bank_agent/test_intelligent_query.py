#!/usr/bin/env python3
"""
Test script for intelligent multi-table query functionality
"""

import requests
import json

def test_intelligent_queries():
    """Test intelligent table selection with various queries"""
    
    print("🧠 Testing Intelligent Multi-Table Query")
    print("=" * 50)
    
    # All available tables
    all_tables = [
        {"table_name": "customer_demographics", "fields": ["customer_id", "first_name", "last_name", "annual_income"]},
        {"table_name": "internal_banking_data", "fields": ["customer_id", "utilization_rate", "current_credit_limit"]},
        {"table_name": "credit_bureau_data", "fields": ["customer_id", "fico_score_8", "total_accounts_bureau"]},
        {"table_name": "fraud_kyc_compliance", "fields": ["customer_id", "overall_fraud_risk_score", "risk_level"]},
        {"table_name": "income_ability_to_pay", "fields": ["customer_id", "verified_annual_income", "debt_to_income_ratio"]},
        {"table_name": "open_banking_data", "fields": ["customer_id", "open_banking_consent", "avg_monthly_income"]},
        {"table_name": "state_economic_indicators", "fields": ["state_code", "unemployment_rate", "macro_risk_score"]}
    ]
    
    # Test queries that should trigger different table selections
    test_queries = [
        {
            "query": "Show me customers with high income",
            "expected_tables": ["customer_demographics"],
            "description": "Single table - demographics only"
        },
        {
            "query": "Find customers with high income and low credit utilization",
            "expected_tables": ["customer_demographics", "internal_banking_data"],
            "description": "Two tables - demographics + banking"
        },
        {
            "query": "Show me customers with good credit scores and low fraud risk",
            "expected_tables": ["customer_demographics", "credit_bureau_data", "fraud_kyc_compliance"],
            "description": "Three tables - demographics + credit + fraud"
        },
        {
            "query": "Find customers with high debt to income ratio",
            "expected_tables": ["income_ability_to_pay"],
            "description": "Single table - income/ability to pay"
        },
        {
            "query": "Show me economic indicators for states with high unemployment",
            "expected_tables": ["state_economic_indicators"],
            "description": "Single table - economic indicators"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print(f"Expected tables: {test_case['expected_tables']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/text-to-sql",
                json={
                    "natural_language_query": test_case["query"],
                    "tables": all_tables
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Success!")
                    print(f"Generated SQL: {result['sql']}")
                    print(f"Execution time: {result.get('execution_time', 0):.2f}ms")
                    
                    # Check if expected tables are used in the SQL
                    sql_lower = result['sql'].lower()
                    used_tables = []
                    for table in test_case['expected_tables']:
                        if table.replace('_', ' ') in sql_lower or table in sql_lower:
                            used_tables.append(table)
                    
                    if used_tables:
                        print(f"🔍 Tables used: {used_tables}")
                        if len(used_tables) >= len(test_case['expected_tables']):
                            print("✅ Correct table selection!")
                        else:
                            print("⚠️  Some expected tables not used")
                    else:
                        print("❌ No expected tables found in SQL")
                        
                else:
                    print("❌ Failed to generate SQL")
                    print(f"Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_intelligent_queries()
    print("\n🎉 Testing completed!")
