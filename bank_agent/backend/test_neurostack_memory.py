#!/usr/bin/env python3
"""
Test script to check NeuroStack memory data.
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

async def test_neurostack_memory():
    """Test what data is stored in NeuroStack memory."""
    print("🚀 Testing NeuroStack Memory Data")
    print("=" * 50)
    
    try:
        # Initialize NeuroStack integration
        neurostack = NeuroStackBankingIntegration()
        
        # Test customer ID 5
        customer_id = 5
        print(f"🔍 Testing Customer ID: {customer_id}")
        
        # Get customer data from NeuroStack memory
        customer_data = neurostack.get_customer_by_id_direct(customer_id)
        
        if customer_data:
            print("✅ Customer data found in NeuroStack memory:")
            print(f"  Customer ID: {customer_data.get('customer_id')}")
            print(f"  Name: {customer_data.get('first_name')} {customer_data.get('last_name')}")
            print(f"  Credit Limit: ${customer_data.get('credit_limit'):,.0f}")
            print(f"  FICO Score: {customer_data.get('fico_score')}")
            print(f"  Credit Utilization: {customer_data.get('credit_utilization'):.1f}%")
            print(f"  Annual Income: ${customer_data.get('annual_income'):,.0f}")
            print(f"  Verified Annual Income: ${customer_data.get('verified_annual_income'):,.0f}")
            print(f"  Income (primary): ${customer_data.get('income'):,.0f}")
            print(f"  DTI Ratio: {customer_data.get('dti_ratio'):.1f}%")
            print(f"  Payment History: {customer_data.get('payment_history')}")
            print(f"  Employment Status: {customer_data.get('employment_status')}")
            print(f"  Customer Segment: {customer_data.get('customer_segment')}")
            print(f"  State: {customer_data.get('state')}")
            print(f"  City: {customer_data.get('city')}")
        else:
            print("❌ No customer data found in NeuroStack memory")
        
        # Also test the enhanced customer data
        print("\n🔍 Testing Enhanced Customer Data:")
        enhanced_customers = neurostack.get_enhanced_customer_data()
        customer_5_enhanced = next((c for c in enhanced_customers if c.get('customer_id') == customer_id), None)
        
        if customer_5_enhanced:
            print("✅ Enhanced customer data found:")
            print(f"  Customer ID: {customer_5_enhanced.get('customer_id')}")
            print(f"  Name: {customer_5_enhanced.get('first_name')} {customer_5_enhanced.get('last_name')}")
            print(f"  Credit Limit: ${customer_5_enhanced.get('credit_limit'):,.0f}")
            print(f"  FICO Score: {customer_5_enhanced.get('fico_score')}")
            print(f"  Credit Utilization: {customer_5_enhanced.get('credit_utilization'):.1f}%")
            print(f"  Annual Income: ${customer_5_enhanced.get('annual_income'):,.0f}")
            print(f"  Verified Annual Income: ${customer_5_enhanced.get('verified_annual_income'):,.0f}")
            print(f"  Income (primary): ${customer_5_enhanced.get('income'):,.0f}")
            print(f"  DTI Ratio: {customer_5_enhanced.get('dti_ratio'):.1f}%")
            print(f"  Payment History: {customer_5_enhanced.get('payment_history')}")
        else:
            print("❌ No enhanced customer data found")
        
    except Exception as e:
        print(f"❌ Error testing NeuroStack memory: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_neurostack_memory())
