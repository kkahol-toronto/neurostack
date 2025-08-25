"""
Test script for NeuroStack Banking Integration.

This script tests the integration between FastAPI and NeuroStack
to ensure all components are working correctly.
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neurostack_integration import (
    get_neurostack_integration,
    execute_neurostack_text_to_sql,
    execute_neurostack_customer_search,
    execute_neurostack_data_analysis,
    execute_neurostack_customer_verification
)


async def test_neurostack_initialization():
    """Test NeuroStack integration initialization."""
    print("🧠 Testing NeuroStack Integration Initialization...")
    
    try:
        integration = await get_neurostack_integration()
        print("✅ NeuroStack integration initialized successfully")
        
        # Test available tools
        tools = integration.get_available_tools()
        print(f"✅ Available tools: {tools}")
        
        # Test tool schemas
        schemas = integration.get_tool_schemas()
        print(f"✅ Tool schemas loaded: {len(schemas)} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ NeuroStack initialization failed: {str(e)}")
        return False


async def test_text_to_sql():
    """Test text-to-SQL functionality with NeuroStack."""
    print("\n🔍 Testing Text-to-SQL with NeuroStack...")
    
    try:
        # Test query
        natural_query = "Show me customers with income above $70,000"
        tables = [
            {
                "table_name": "customer_demographics",
                "fields": ["customer_id", "first_name", "last_name", "annual_income", "state"]
            }
        ]
        
        result = await execute_neurostack_text_to_sql(
            natural_query=natural_query,
            tables=tables,
            user_id="test_user"
        )
        
        print(f"✅ Text-to-SQL result: {result['success']}")
        if result['success']:
            print(f"   SQL: {result.get('sql', 'N/A')}")
            print(f"   NeuroStack features: {result.get('neurostack_features', {})}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Text-to-SQL test failed: {str(e)}")
        return False


async def test_customer_search():
    """Test customer search with NeuroStack."""
    print("\n👥 Testing Customer Search with NeuroStack...")
    
    try:
        # Test search
        query = "John"
        
        result = await execute_neurostack_customer_search(
            query=query,
            search_type="semantic",
            user_id="test_user"
        )
        
        print(f"✅ Customer search result: {result['success']}")
        if result['success']:
            print(f"   Found {result.get('count', 0)} customers")
            print(f"   NeuroStack features: {result.get('neurostack_features', {})}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Customer search test failed: {str(e)}")
        return False


async def test_data_analysis():
    """Test data analysis with NeuroStack."""
    print("\n📊 Testing Data Analysis with NeuroStack...")
    
    try:
        # Test analysis
        result = await execute_neurostack_data_analysis(
            analysis_type="customer_patterns",
            data_source="customer_demographics",
            user_id="test_user"
        )
        
        print(f"✅ Data analysis result: {result['success']}")
        if result['success']:
            print(f"   Analysis type: {result.get('analysis_type', 'N/A')}")
            print(f"   Insights: {result.get('insights', 'N/A')[:100]}...")
            print(f"   NeuroStack features: {result.get('neurostack_features', {})}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Data analysis test failed: {str(e)}")
        return False


async def test_customer_verification():
    """Test customer verification with NeuroStack."""
    print("\n🔐 Testing Customer Verification with NeuroStack...")
    
    try:
        # Test verification
        result = await execute_neurostack_customer_verification(
            customer_id=1,
            verification_type="security_questions",
            user_id="test_user"
        )
        
        print(f"✅ Customer verification result: {result['success']}")
        if result['success']:
            print(f"   Questions generated: {len(result.get('questions', []))}")
            print(f"   NeuroStack features: {result.get('neurostack_features', {})}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Customer verification test failed: {str(e)}")
        return False


async def test_memory_features():
    """Test memory features."""
    print("\n🧠 Testing Memory Features...")
    
    try:
        integration = await get_neurostack_integration()
        
        # Test recent activity
        activity = await integration.get_recent_activity(hours=24)
        print(f"✅ Recent activity retrieved: {len(activity.get('summary', {}))} categories")
        
        # Test similar queries
        similar_queries = await integration.get_similar_queries("customer income", limit=3)
        print(f"✅ Similar queries found: {len(similar_queries)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory features test failed: {str(e)}")
        return False


async def test_enhanced_customer_data():
    """Test enhanced customer data generation."""
    print("\n👤 Testing Enhanced Customer Data...")
    
    try:
        integration = await get_neurostack_integration()
        
        # Get enhanced customer data
        customers = integration.get_enhanced_customer_data()
        print(f"✅ Enhanced customer data generated: {len(customers)} customers")
        
        # Check for enhanced fields
        if customers:
            customer = customers[0]
            enhanced_fields = [
                "occupation", "education_level", "marital_status", 
                "credit_score", "investment_preferences", "banking_goals"
            ]
            
            found_fields = [field for field in enhanced_fields if field in customer]
            print(f"✅ Enhanced fields found: {len(found_fields)}/{len(enhanced_fields)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced customer data test failed: {str(e)}")
        return False


async def run_all_tests():
    """Run all NeuroStack integration tests."""
    print("🚀 Starting NeuroStack Banking Integration Tests\n")
    
    tests = [
        ("Initialization", test_neurostack_initialization),
        ("Enhanced Customer Data", test_enhanced_customer_data),
        ("Text-to-SQL", test_text_to_sql),
        ("Customer Search", test_customer_search),
        ("Data Analysis", test_data_analysis),
        ("Customer Verification", test_customer_verification),
        ("Memory Features", test_memory_features),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! NeuroStack integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n✅ NeuroStack Banking Integration is ready for use!")
        sys.exit(0)
    else:
        print("\n❌ NeuroStack Banking Integration needs attention.")
        sys.exit(1)



