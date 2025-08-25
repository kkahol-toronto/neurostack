#!/usr/bin/env python3
"""
Simple test to check if NeuroStack is working.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neurostack_integration import NeuroStackBankingIntegration

async def test_neurostack():
    """Test if NeuroStack is working correctly."""
    print("🚀 Testing NeuroStack Integration")
    print("=" * 50)
    
    try:
        # Initialize NeuroStack integration
        neurostack = NeuroStackBankingIntegration()
        
        # Test a simple prompt
        simple_prompt = "Hello, this is a test message. Please respond with 'NeuroStack is working correctly.'"
        
        print("🔍 Testing simple prompt generation...")
        response = await neurostack.generate_response(simple_prompt)
        
        print(f"✅ NeuroStack Response: {response}")
        print("✅ NeuroStack is working correctly!")
        
    except Exception as e:
        print(f"❌ NeuroStack failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_neurostack())
