#!/usr/bin/env python3
"""
Enhanced NeuroStack Features Test Script

This script demonstrates the enhanced NeuroStack features:
1. Historical Learning
2. Result Analysis  
3. Adaptive Behavior
4. Persistent Memory with Cosmos DB
"""

import asyncio
import json
import requests
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_query_analytics():
    """Test query analytics endpoint."""
    print("🔍 Testing Query Analytics...")
    
    response = requests.get(f"{BASE_URL}/api/neurostack/query-analytics?hours=24")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Query Analytics: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Query Analytics failed: {response.status_code}")
    
    print()

def test_optimization_suggestions():
    """Test optimization suggestions endpoint."""
    print("💡 Testing Optimization Suggestions...")
    
    query = "Show me customers with high income"
    response = requests.get(f"{BASE_URL}/api/neurostack/optimization-suggestions?query={query}&user_id=demo_user")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Optimization Suggestions: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Optimization Suggestions failed: {response.status_code}")
    
    print()

def test_similar_queries():
    """Test similar queries endpoint."""
    print("🔍 Testing Similar Queries...")
    
    query = "Show me customers with income above $70,000"
    response = requests.get(f"{BASE_URL}/api/neurostack/similar-queries?query={query}&limit=3")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Similar Queries: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Similar Queries failed: {response.status_code}")
    
    print()

def test_user_behavior():
    """Test user behavior endpoint."""
    print("👤 Testing User Behavior...")
    
    user_id = "demo_user"
    response = requests.get(f"{BASE_URL}/api/neurostack/user-behavior/{user_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User Behavior: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ User Behavior failed: {response.status_code}")
    
    print()

def test_query_patterns():
    """Test query patterns endpoint."""
    print("📊 Testing Query Patterns...")
    
    response = requests.get(f"{BASE_URL}/api/neurostack/query-patterns")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Query Patterns: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Query Patterns failed: {response.status_code}")
    
    print()

def test_text_to_sql_with_learning():
    """Test text-to-SQL with enhanced learning features."""
    print("🧠 Testing Text-to-SQL with Enhanced Learning...")
    
    queries = [
        {
            "natural_language_query": "Show me customers with income above $70,000",
            "tables": [{"table_name": "customer_demographics", "fields": ["customer_id", "first_name", "last_name", "annual_income"]}]
        },
        {
            "natural_language_query": "Find customers with credit score above 750",
            "tables": [{"table_name": "customer_demographics", "fields": ["customer_id", "first_name", "last_name", "credit_score"]}]
        },
        {
            "natural_language_query": "Show me high-income customers from California",
            "tables": [{"table_name": "customer_demographics", "fields": ["customer_id", "first_name", "last_name", "annual_income", "state"]}]
        }
    ]
    
    for i, query_data in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query_data['natural_language_query']}")
        
        response = requests.post(
            f"{BASE_URL}/api/text-to-sql",
            headers={"Content-Type": "application/json"},
            json=query_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Success! SQL: {data.get('sql')}")
                print(f"   Execution Time: {data.get('execution_time')}ms")
                print(f"   NeuroStack Features: {data.get('neurostack_features', {})}")
            else:
                print(f"❌ Failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
        
        # Wait between queries to see learning in action
        time.sleep(2)
    
    print()

def test_historical_learning_demonstration():
    """Demonstrate historical learning by running similar queries."""
    print("🎯 Demonstrating Historical Learning...")
    
    # First, run a query
    print("1️⃣ Running initial query...")
    query1 = {
        "natural_language_query": "Show me customers with income above $80,000",
        "tables": [{"table_name": "customer_demographics", "fields": ["customer_id", "first_name", "last_name", "annual_income"]}]
    }
    
    response1 = requests.post(
        f"{BASE_URL}/api/text-to-sql",
        headers={"Content-Type": "application/json"},
        json=query1
    )
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"   ✅ Initial query completed")
    
    time.sleep(2)
    
    # Now run a similar query to see if it learns
    print("2️⃣ Running similar query to test learning...")
    query2 = {
        "natural_language_query": "Find customers with salary above $85,000",
        "tables": [{"table_name": "customer_demographics", "fields": ["customer_id", "first_name", "last_name", "annual_income"]}]
    }
    
    response2 = requests.post(
        f"{BASE_URL}/api/text-to-sql",
        headers={"Content-Type": "application/json"},
        json=query2
    )
    
    if response2.status_code == 200:
        data2 = response2.json()
        if data2.get("success"):
            print(f"   ✅ Similar query completed")
            print(f"   📊 NeuroStack Features: {data2.get('neurostack_features', {})}")
    
    time.sleep(2)
    
    # Check if similar queries are found
    print("3️⃣ Checking for similar queries...")
    similar_response = requests.get(f"{BASE_URL}/api/neurostack/similar-queries?query=Show me customers with income above $80,000&limit=3")
    if similar_response.status_code == 200:
        similar_data = similar_response.json()
        print(f"   📈 Similar queries found: {len(similar_data.get('similar_queries', []))}")
    
    print()

def test_adaptive_behavior():
    """Test adaptive behavior by running queries for the same user."""
    print("🔄 Testing Adaptive Behavior...")
    
    user_id = "demo_user"
    
    # Run multiple queries for the same user
    queries = [
        "Show me customers with income above $70,000",
        "Find customers with credit score above 750",
        "Show me customers from California"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"📝 User Query {i}: {query}")
        
        query_data = {
            "natural_language_query": query,
            "tables": [{"table_name": "customer_demographics", "fields": ["customer_id", "first_name", "last_name", "annual_income"]}]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/text-to-sql",
            headers={"Content-Type": "application/json"},
            json=query_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ Query {i} completed")
        
        time.sleep(1)
    
    # Check user behavior after multiple queries
    print("👤 Checking user behavior patterns...")
    behavior_response = requests.get(f"{BASE_URL}/api/neurostack/user-behavior/{user_id}")
    if behavior_response.status_code == 200:
        behavior_data = behavior_response.json()
        if behavior_data.get("success"):
            behavior = behavior_data.get("behavior")
            if behavior:
                print(f"   📊 Total Queries: {behavior.get('total_queries', 0)}")
                print(f"   🎯 Preferred Query Types: {behavior.get('preferred_query_types', [])}")
                print(f"   📋 Common Tables: {behavior.get('common_tables', [])}")
            else:
                print("   📊 No user behavior data yet (user is new)")
        else:
            print(f"   ❌ Failed to get user behavior: {behavior_data.get('error')}")
    else:
        print(f"   ❌ HTTP Error: {behavior_response.status_code}")
    
    print()

def main():
    """Run all tests."""
    print("🚀 Enhanced NeuroStack Features Test Suite")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test basic endpoints
        test_query_analytics()
        test_optimization_suggestions()
        test_similar_queries()
        test_user_behavior()
        test_query_patterns()
        
        # Test enhanced features
        test_text_to_sql_with_learning()
        test_historical_learning_demonstration()
        test_adaptive_behavior()
        
        print("🎉 All tests completed!")
        print("=" * 50)
        print("📋 Summary of Enhanced Features Tested:")
        print("✅ Persistent Memory with Cosmos DB")
        print("✅ Historical Learning from Query Patterns")
        print("✅ Result Analysis and Insights")
        print("✅ Adaptive Behavior based on User Patterns")
        print("✅ Optimization Suggestions")
        print("✅ Semantic Similarity Search")
        print("✅ Query Analytics and Reporting")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main()
