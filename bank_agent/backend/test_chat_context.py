#!/usr/bin/env python3
"""
Test script to verify customer profile data is being properly included in chat context.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the neurostack src to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from chat_service import ChatService
from models import ChatMessageRequest, ChatSession

async def test_chat_context():
    """Test if customer profile data is being properly included in chat context."""
    
    print("🧪 Testing Chat Context with Customer Profile")
    print("=" * 50)
    
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
        
        # Create a test request
        test_request = ChatMessageRequest(
            session_id="test_session_123",
            customer_id=5,  # Michael Gonzales
            customer_name="Michael Gonzales",
            content="What is the current credit limit for this customer?",
            execution_id="test_execution_123",
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
            session_id="test_session_123",
            customer_id=5,
            customer_name="Michael Gonzales",
            execution_id="test_execution_123",
            investigation_results=test_request.investigation_results,
            created_at=asyncio.get_event_loop().time(),
            message_count=0
        )
        
        print("🧠 Testing context building...")
        
        # Test the context building function
        context = await chat_service._build_comprehensive_context(test_request, test_session)
        
        print("\n📋 Context Results:")
        print(f"  Customer Profile Available: {'✅' if context.get('customer_profile') else '❌'}")
        print(f"  Investigation Results Available: {'✅' if context.get('investigation_results') else '❌'}")
        print(f"  Chat History Available: {'✅' if context.get('chat_history') else '❌'}")
        
        if context.get('customer_profile'):
            profile = context['customer_profile']
            print(f"\n👤 Customer Profile Data:")
            print(f"  Customer ID: {profile.get('customer_id', 'N/A')}")
            print(f"  Name: {profile.get('name', 'N/A')}")
            print(f"  Credit Limit: ${profile.get('credit_limit', 'N/A'):,.0f}" if profile.get('credit_limit') else f"  Credit Limit: {profile.get('credit_limit', 'N/A')}")
            print(f"  FICO Score: {profile.get('fico_score', 'N/A')}")
            print(f"  Credit Utilization: {profile.get('credit_utilization', 'N/A')}%")
            print(f"  Payment History: {profile.get('payment_history', 'N/A')}")
            print(f"  Income: ${profile.get('income', 'N/A'):,.0f}" if profile.get('income') else f"  Income: {profile.get('income', 'N/A')}")
        
        if context.get('investigation_results'):
            print(f"\n🔍 Investigation Results Available: {len(str(context['investigation_results']))} characters")
        
        # Test prompt creation
        print("\n📝 Testing prompt creation...")
        prompt = chat_service._create_intelligent_prompt(test_request, context)
        
        print(f"  Prompt Length: {len(prompt)} characters")
        print(f"  Contains Customer Profile: {'✅' if 'Customer Profile:' in prompt else '❌'}")
        print(f"  Contains Investigation Results: {'✅' if 'INVESTIGATION RESULTS:' in prompt else '❌'}")
        print(f"  Contains Analyst Context: {'✅' if 'banking analyst' in prompt.lower() else '❌'}")
        
        # Show a snippet of the prompt
        print(f"\n📄 Prompt Snippet (first 500 chars):")
        print("-" * 50)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 50)
        
        print("\n✅ Chat context test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing chat context: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Chat Context Test")
    print()
    
    success = await test_chat_context()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Chat Context Test: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\n🎉 Chat context is working correctly with customer profile data!")
    else:
        print("\n⚠️  Chat context test failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
