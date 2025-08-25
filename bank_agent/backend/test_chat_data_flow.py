#!/usr/bin/env python3
"""
Test to verify chat service data flow.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_chat_data_flow():
    """Test the chat service data flow."""
    print("🚀 Testing Chat Service Data Flow")
    print("=" * 50)
    
    try:
        # Import chat service
        from chat_service import ChatService
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Create a mock request
        from models import ChatMessageRequest
        request = ChatMessageRequest(
            session_id="test_session",
            customer_id=5,
            customer_name="Michael Gonzales",
            content="What is the current credit limit?",
            message_type="user"
        )
        
        # Create a mock session
        from models import ChatSession
        from datetime import datetime
        session = ChatSession(
            session_id="test_session",
            customer_id=5,
            customer_name="Michael Gonzales",
            message_count=1,
            execution_id="test_execution",
            investigation_results={},
            created_at=datetime.now()
        )
        
        # Test the context building
        print("🔍 Testing context building...")
        context = await chat_service._build_comprehensive_context(request, session)
        
        if context and context.get("customer_profile"):
            profile = context["customer_profile"]
            print("✅ Customer profile from chat service:")
            print(f"  Customer ID: {profile.get('customer_id')}")
            print(f"  Name: {profile.get('name', f'{profile.get('first_name', '')} {profile.get('last_name', '')}')}")
            print(f"  Credit Limit: ${profile.get('credit_limit', 0):,.0f}")
            print(f"  FICO Score: {profile.get('fico_score', 'N/A')}")
            print(f"  Credit Utilization: {profile.get('credit_utilization', 0):.1f}%")
            print(f"  Annual Income: ${profile.get('annual_income', 0):,.0f}")
            print(f"  Verified Annual Income: ${profile.get('verified_annual_income', 0):,.0f}")
            print(f"  Income (primary): ${profile.get('income', 0):,.0f}")
            print(f"  DTI Ratio: {profile.get('dti_ratio', 0):.1f}%")
            print(f"  Payment History: {profile.get('payment_history', 'N/A')}")
            
            # Check if income is correct
            expected_income = 111398.06
            actual_income = profile.get('income')
            if actual_income and abs(actual_income - expected_income) < 1:
                print(f"✅ Income is correct: ${actual_income:,.0f}")
            else:
                print(f"❌ Income is incorrect: ${actual_income:,.0f} (expected: ${expected_income:,.0f})")
        else:
            print("❌ No customer profile in context")
        
    except Exception as e:
        print(f"❌ Error testing chat data flow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_data_flow())
