#!/usr/bin/env python3
"""
Test script for Banking Agent Backend API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_data_sources():
    """Test the data sources endpoint"""
    print("\n📊 Testing data sources...")
    try:
        response = requests.get(f"{BASE_URL}/api/datasources")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data sources retrieved: {len(data)} sources")
            for source in data:
                print(f"   - {source['name']} ({source['category']})")
            return True
        else:
            print(f"❌ Data sources failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data sources error: {e}")
        return False

def test_sample_data():
    """Test the sample data endpoint"""
    print("\n📋 Testing sample data...")
    try:
        response = requests.get(f"{BASE_URL}/api/sample/customer_demographics?limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sample data retrieved: {data['count']} records")
            return True
        else:
            print(f"❌ Sample data failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sample data error: {e}")
        return False

def test_text_to_sql():
    """Test the text-to-SQL endpoint"""
    print("\n🤖 Testing text-to-SQL conversion...")
    try:
        payload = {
            "natural_language_query": "Show me customers with income above $100,000",
            "table_name": "customer_demographics",
            "fields": ["customer_id", "first_name", "last_name", "annual_income", "state"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/text-to-sql",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Text-to-SQL successful:")
                print(f"   SQL: {data.get('sql')}")
                print(f"   Execution time: {data.get('execution_time')}ms")
                print(f"   Results: {len(data.get('data', []))} records")
                return True
            else:
                print(f"❌ Text-to-SQL failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Text-to-SQL request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Text-to-SQL error: {e}")
        return False

def test_sql_execution():
    """Test the SQL execution endpoint"""
    print("\n⚡ Testing SQL execution...")
    try:
        payload = {
            "sql": "SELECT * FROM customer_demographics WHERE annual_income > 100000",
            "table_name": "customer_demographics"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ SQL execution successful:")
                print(f"   Execution time: {data.get('execution_time')}ms")
                print(f"   Results: {len(data.get('data', []))} records")
                return True
            else:
                print(f"❌ SQL execution failed: {data.get('error')}")
                return False
        else:
            print(f"❌ SQL execution request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ SQL execution error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Banking Agent Backend API Tests")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_data_sources,
        test_sample_data,
        test_text_to_sql,
        test_sql_execution
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend configuration.")

if __name__ == "__main__":
    main()
