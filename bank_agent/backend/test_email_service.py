#!/usr/bin/env python3
"""
Test script for email service functionality.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service import email_service

async def test_email_service():
    """Test the email service functionality."""
    print("🚀 Testing Email Service")
    print("=" * 50)
    
    # Test data
    test_email_data = {
        "to": "test@example.com",
        "subject": "Test Credit Decision",
        "body": "This is a test email for credit decision.",
        "decision": "approved",
        "approvedAmount": 5000.0,
        "reason": "Test approval reason",
        "customerName": "Test Customer",
        "customerId": 123
    }
    
    try:
        print("📧 Testing email sending...")
        result = await email_service.send_credit_decision_email(test_email_data)
        
        print(f"✅ Email service result: {result}")
        
        if result.get("success"):
            print("✅ Email service is working correctly!")
        else:
            print(f"⚠️ Email service returned error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Email service failed: {e}")
        import traceback
        traceback.print_exc()

async def test_email_content_generation():
    """Test email content generation."""
    print("\n📝 Testing Email Content Generation")
    print("=" * 50)
    
    # Test approved decision
    approved_data = {
        "customerName": "John Doe",
        "decision": "approved",
        "approvedAmount": 5000.0,
        "reason": "Excellent credit profile and payment history",
        "decisionDate": "2024-01-15"
    }
    
    try:
        content = email_service.generate_email_content(approved_data)
        print("✅ Approved email content generated:")
        print(f"Subject: {content['subject']}")
        print(f"Body: {content['body'][:200]}...")
        
    except Exception as e:
        print(f"❌ Content generation failed: {e}")
    
    # Test rejected decision
    rejected_data = {
        "customerName": "Jane Smith",
        "decision": "rejected",
        "reason": "Insufficient credit history",
        "decisionDate": "2024-01-15"
    }
    
    try:
        content = email_service.generate_email_content(rejected_data)
        print("\n✅ Rejected email content generated:")
        print(f"Subject: {content['subject']}")
        print(f"Body: {content['body'][:200]}...")
        
    except Exception as e:
        print(f"❌ Content generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_email_service())
    asyncio.run(test_email_content_generation())
