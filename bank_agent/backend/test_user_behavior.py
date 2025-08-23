#!/usr/bin/env python3
"""
Test script to debug user behavior storage issue.
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neurostack_cosmos_memory import get_cosmos_memory_manager
from neurostack_cosmos_memory import QueryResult, UserBehavior
from datetime import datetime
from dataclasses import asdict

async def test_user_behavior():
    """Test user behavior storage and retrieval."""
    print("🧪 Testing User Behavior Storage...")
    
    try:
        # Get memory manager
        cosmos_memory = await get_cosmos_memory_manager()
        print("✅ Memory manager initialized")
        
        # Create a test query result
        test_query_result = QueryResult(
            query_id="test_123",
            natural_query="Show me customers with income above $80,000",
            sql_generated="SELECT * FROM customer_demographics WHERE annual_income > 80000",
            result_count=5,
            execution_time=100.0,
            success=True,
            tables_used=["customer_demographics"],
            query_type="income_analysis",
            user_id="demo_user",
            timestamp=datetime.now(),
            results_summary={"total_rows": 5},
            error_message=None
        )
        
        print(f"✅ Created test query result for user: {test_query_result.user_id}")
        
        # Try to update user behavior directly
        print("🔄 Updating user behavior...")
        await cosmos_memory._update_user_behavior(test_query_result)
        print("✅ User behavior update completed")
        
        # Try to retrieve user behavior
        print("🔍 Retrieving user behavior...")
        behavior = await cosmos_memory.get_user_behavior("demo_user")
        print(f"📊 User behavior: {behavior}")
        
        if behavior:
            print("✅ User behavior found!")
            print(f"   Total queries: {behavior.get('total_queries', 0)}")
            print(f"   Preferred types: {behavior.get('preferred_query_types', [])}")
            print(f"   Common tables: {behavior.get('common_tables', [])}")
        else:
            print("❌ No user behavior found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_behavior())
