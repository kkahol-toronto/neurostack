#!/usr/bin/env python3
"""
Test script to verify correct credit limit information for Customer ID 5.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the neurostack src to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from chat_service import ChatService
from models import ChatMessageRequest, ChatSession

async def test_credit_limit_response():
    """Test if the AI provides correct credit limit information for Customer ID 5."""
    
    print("🧪 Testing Credit Limit Response for Customer ID 5")
    print("=" * 60)
    
    # Load environment variables
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    
    try:
        # Initialize chat service
        print("🔧 Initializing Chat Service...")
        chat_service = ChatService()
        
        # Create a test request asking about credit limit
        test_request = ChatMessageRequest(
            session_id="test_credit_limit_session",
            customer_id=5,  # Michelle Taylor
            customer_name="Michelle Taylor",
            content="What is the current credit limit for this customer?",
            execution_id="test_execution_credit_limit",
            investigation_results={
                "results": [
                    {
                        "step_id": "credit_analysis",
                        "step_title": "Credit Analysis",
                        "data": {
                            "fico_score": 724,
                            "credit_limit": 32000,
                            "credit_utilization": 20.4
                        }
                    }
                ]
            }
        )
        
        # Create a test session
        test_session = ChatSession(
            session_id="test_credit_limit_session",
            customer_id=5,
            customer_name="Michelle Taylor",
            execution_id="test_execution_credit_limit",
            investigation_results=test_request.investigation_results,
            created_at=asyncio.get_event_loop().time(),
            message_count=0
        )
        
        print("🧠 Testing AI response generation...")
        
        # Generate AI response
        response = await chat_service._generate_ai_response(test_request, test_session)
        
        print("\n📋 AI Response:")
        print("-" * 50)
        print(response.get("content", "No response generated"))
        print("-" * 50)
        
        # Check if the response contains the correct credit limit
        content = response.get("content", "").lower()
        correct_credit_limit = "$32,000" in response.get("content", "") or "32000" in response.get("content", "") or "32,000" in response.get("content", "")
        
        print(f"\n✅ Credit Limit Check:")
        print(f"  Contains $32,000: {'✅ YES' if correct_credit_limit else '❌ NO'}")
        
        if correct_credit_limit:
            print("  ✅ AI is providing the correct credit limit!")
        else:
            print("  ❌ AI is not providing the correct credit limit")
            print("  Expected: $32,000")
        
        return correct_credit_limit
        
    except Exception as e:
        print(f"❌ Error testing credit limit response: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Credit Limit Test")
    print()
    
    success = await test_credit_limit_response()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"  Credit Limit Test: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\n🎉 Credit limit information is now correct!")
    else:
        print("\n⚠️  Credit limit information is still incorrect. Check the response above.")

if __name__ == "__main__":
    asyncio.run(main())
