#!/usr/bin/env python3
"""
Test script to verify frontend integration with authentication
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_frontend_integration():
    print("🧪 Testing Frontend Integration with Authentication")
    print("=" * 60)
    
    # Test 1: Register a new user
    print("\n1️⃣ Testing User Registration...")
    register_data = {
        "username": "frontend_test_user",
        "email": "frontend@test.com",
        "first_name": "Frontend",
        "last_name": "Tester",
        "password": "test123",
        "role": "analyst",
        "department": "Frontend Testing"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 200:
            print("✅ User registration successful")
        else:
            print(f"❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Test 2: Login
    print("\n2️⃣ Testing User Login...")
    login_data = {
        "username": "frontend_test_user",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            print("✅ Login successful")
            print(f"   Token: {token[:20]}...")
            print(f"   User ID: {user_id}")
            print(f"   Role: {data.get('role')}")
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 3: Test authenticated API calls
    print("\n3️⃣ Testing Authenticated API Calls...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test text-to-sql with authentication
    query_data = {
        "natural_language_query": "Show me customers with high income",
        "table_name": "customers",
        "fields": ["customer_id", "first_name", "last_name", "income"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/text-to-sql", json=query_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Text-to-SQL with authentication successful")
            print(f"   SQL: {data.get('sql', 'N/A')}")
            print(f"   Results: {len(data.get('data', []))} records")
        else:
            print(f"❌ Text-to-SQL failed: {response.text}")
    except Exception as e:
        print(f"❌ Text-to-SQL error: {e}")
    
    # Test 4: Get user behavior
    print("\n4️⃣ Testing User Behavior Tracking...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/{user_id}/behavior", headers=headers)
        if response.status_code == 200:
            behavior = response.json()
            print("✅ User behavior retrieved successfully")
            print(f"   Total queries: {behavior.get('total_queries', 0)}")
            print(f"   Role: {behavior.get('role', 'N/A')}")
            print(f"   Department: {behavior.get('department', 'N/A')}")
        else:
            print(f"❌ User behavior failed: {response.text}")
    except Exception as e:
        print(f"❌ User behavior error: {e}")
    
    # Test 5: Test without authentication (should fail)
    print("\n5️⃣ Testing API without Authentication (should fail)...")
    try:
        response = requests.post(f"{BASE_URL}/api/text-to-sql", json=query_data)
        if response.status_code == 401:
            print("✅ API correctly requires authentication")
        else:
            print(f"❌ API should require authentication but didn't: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 6: Test admin functionality
    print("\n6️⃣ Testing Admin Login...")
    admin_login = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=admin_login)
        if response.status_code == 200:
            admin_data = response.json()
            admin_token = admin_data.get("access_token")
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Test admin can list users
            response = requests.get(f"{BASE_URL}/api/users", headers=admin_headers)
            if response.status_code == 200:
                users = response.json()
                print("✅ Admin can list users")
                print(f"   Total users: {len(users)}")
                for user in users:
                    print(f"   - {user.get('username')} ({user.get('role')})")
            else:
                print(f"❌ Admin user listing failed: {response.text}")
        else:
            print(f"❌ Admin login failed: {response.text}")
    except Exception as e:
        print(f"❌ Admin test error: {e}")
    
    print("\n🎉 Frontend Integration Test Complete!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Try logging in with the demo users:")
    print("   - admin / admin123")
    print("   - analyst / analyst123") 
    print("   - manager / manager123")
    print("3. Or register a new user")
    print("4. Test the enhanced NeuroStack features with authentication!")

if __name__ == "__main__":
    test_frontend_integration()
