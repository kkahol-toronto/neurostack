#!/usr/bin/env python3
"""
Email Setup Helper Script

This script helps you configure email settings for the banking agent.
"""

import os
import sys
from dotenv import load_dotenv

def setup_email_config():
    """Interactive setup for email configuration."""
    print("🚀 Email Configuration Setup")
    print("=" * 50)
    
    # Load existing .env file if it exists
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    load_dotenv(env_path)
    
    print("📧 Current Email Configuration:")
    print(f"SMTP Server: {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}")
    print(f"SMTP Port: {os.getenv('SMTP_PORT', '587')}")
    print(f"Sender Email: {os.getenv('SENDER_EMAIL', 'neurostackagent@gmail.com')}")
    print(f"Sender Password: {'***CONFIGURED***' if os.getenv('SENDER_PASSWORD') else 'NOT SET'}")
    
    print("\n🔧 To enable email sending, you need to:")
    print("1. Enable 2-Factor Authentication on neurostackagent@gmail.com")
    print("2. Generate an App Password:")
    print("   - Go to: https://myaccount.google.com/")
    print("   - Security → 2-Step Verification → App passwords")
    print("   - Select 'Mail' and generate password")
    print("3. Add the app password to your .env file")
    
    print("\n📝 Add these lines to your .env file:")
    print("```bash")
    print("# Email Configuration")
    print("SMTP_SERVER=smtp.gmail.com")
    print("SMTP_PORT=587")
    print("SENDER_EMAIL=neurostackagent@gmail.com")
    print("SENDER_PASSWORD=your_16_character_app_password_here")
    print("```")
    
    # Test current configuration
    print("\n🧪 Testing Current Configuration:")
    try:
        from email_service import email_service
        import asyncio
        
        async def test_email():
            test_data = {
                "to": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email from the banking agent.",
                "decision": "approved",
                "approvedAmount": 1000.0,
                "reason": "Test reason",
                "customerName": "Test Customer",
                "customerId": 999
            }
            
            result = await email_service.send_credit_decision_email(test_data)
            print(f"Result: {result}")
            
            if result.get("success"):
                if "Email sent successfully" in result.get("message", ""):
                    print("✅ Email sending is WORKING!")
                else:
                    print("⚠️ Email data logged (SMTP not configured)")
                    print("   Add SENDER_PASSWORD to .env file to enable actual sending")
            else:
                print(f"❌ Email sending failed: {result.get('error')}")
        
        asyncio.run(test_email())
        
    except Exception as e:
        print(f"❌ Error testing email: {e}")

if __name__ == "__main__":
    setup_email_config()
