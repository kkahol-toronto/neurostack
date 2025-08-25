#!/usr/bin/env python3
"""
Test script for User Management System
Demonstrates registration, login, and user behavior tracking.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_user_management():
    """Test the complete user management flow."""
    print("🚀 User Management System Test")
    print("=" * 50)
    
    # Test 1: Register a new user
    print("\n1️⃣ Testing User Registration...")
    register_data = {
        "username": "testuser",
        "email": "testuser@bank.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123",
        "role": "analyst",
        "department": "Data Analytics"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User registered successfully: {user_data['username']} ({user_data['user_id']})")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return
    
    # Test 2: Login with the new user
    print("\n2️⃣ Testing User Login...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            login_response = response.json()
            token = login_response["access_token"]
            print(f"✅ Login successful: {login_response['username']}")
            print(f"   Token: {token[:20]}...")
            print(f"   Role: {login_response['role']}")
            print(f"   Department: {login_response['department']}")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return
    
    # Test 3: Get user profile
    print("\n3️⃣ Testing Profile Retrieval...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Profile retrieved: {profile['first_name']} {profile['last_name']}")
            print(f"   Email: {profile['email']}")
            print(f"   Created: {profile['created_at']}")
        else:
            print(f"❌ Profile retrieval failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Profile error: {str(e)}")
    
    # Test 4: Run some queries to build user behavior
    print("\n4️⃣ Testing Query Execution with User Tracking...")
    
    queries = [
        {
            "natural_language_query": "Show me customers with income above $80,000",
            "tables": [{"table_name": "customer_demographics", "fields": ["customer_id", "first_name", "last_name", "annual_income"]}]
        },
        {
            "natural_language_query": "Find customers with credit score above 750",
            "tables": [{"table_name": "credit_bureau_data", "fields": ["customer_id", "fico_score_8", "fico_score_9"]}]
        },
        {
            "natural_language_query": "Show me high-risk customers",
            "tables": [{"table_name": "fraud_kyc_compliance", "fields": ["customer_id", "overall_fraud_risk_score", "risk_level"]}]
        }
    ]
    
    for i, query in enumerate(queries, 1):
        try:
            response = requests.post(f"{BASE_URL}/api/text-to-sql", json=query, headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Query {i} executed successfully")
                print(f"      Execution time: {result['execution_time']:.2f}ms")
                print(f"      Results: {len(result['data'])} records")
            else:
                print(f"   ❌ Query {i} failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Query {i} error: {str(e)}")
    
    # Test 5: Get user behavior
    print("\n5️⃣ Testing User Behavior Tracking...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/users/{user_data['user_id']}/behavior", headers=headers)
        if response.status_code == 200:
            behavior = response.json()
            print(f"✅ User behavior retrieved:")
            print(f"   Total queries: {behavior['total_queries']}")
            print(f"   Preferred query types: {behavior['preferred_query_types']}")
            print(f"   Common tables: {behavior['common_tables']}")
            print(f"   Average complexity: {behavior['avg_query_complexity']:.2f}")
            print(f"   Department: {behavior['department']}")
            print(f"   Role: {behavior['role']}")
        else:
            print(f"❌ Behavior retrieval failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Behavior error: {str(e)}")
    
    # Test 6: Test admin functionality (using default admin)
    print("\n6️⃣ Testing Admin Login...")
    admin_login = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=admin_login)
        if response.status_code == 200:
            admin_response = response.json()
            admin_token = admin_response["access_token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            print(f"✅ Admin login successful: {admin_response['username']}")
            
            # List all users
            response = requests.get(f"{BASE_URL}/api/users", headers=admin_headers)
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Admin can list users: {users['total_count']} users found")
                for user in users['users'][:3]:  # Show first 3 users
                    print(f"   - {user['username']} ({user['role']}) - {user['department']}")
            else:
                print(f"❌ User listing failed: {response.status_code}")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin test error: {str(e)}")
    
    print("\n🎉 User Management Test Complete!")
    print("=" * 50)

def test_default_users():
    """Test the default users that are pre-created."""
    print("\n🔧 Testing Default Users...")
    
    default_users = [
        {"username": "admin", "password": "admin123", "role": "admin"},
        {"username": "analyst", "password": "analyst123", "role": "analyst"},
        {"username": "manager", "password": "manager123", "role": "manager"}
    ]
    
    for user in default_users:
        try:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": user["username"],
                "password": user["password"]
            })
            
            if response.status_code == 200:
                login_data = response.json()
                print(f"✅ {user['username']} login successful - Role: {login_data['role']}")
            else:
                print(f"❌ {user['username']} login failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {user['username']} error: {str(e)}")

if __name__ == "__main__":
    print("Starting User Management Tests...")
    test_default_users()
    test_user_management()
