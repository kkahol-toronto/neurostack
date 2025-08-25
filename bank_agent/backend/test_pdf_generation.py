#!/usr/bin/env python3
"""
Test script for PDF generation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_service import pdf_service
import json

def test_pdf_generation():
    """Test PDF generation with sample data"""
    
    # Sample data for testing
    test_data = {
        "customerId": 999,
        "customerName": "Test Customer",
        "decision": "approved",
        "approvedAmount": 5000.0,
        "reason": "Good credit history and stable income",
        "emailData": {
            "to": "test@example.com",
            "subject": "Credit Limit Decision - Test Customer",
            "body": "Dear Test Customer,\n\nYour credit limit increase request has been approved.\n\nBest regards,\nBanking Team"
        },
        "investigationResults": [
            {
                "step_title": "Credit Score Analysis",
                "status": "completed",
                "execution_time": 2.5,
                "insights": [
                    "Credit score: 750 (Excellent)",
                    "Payment history: 100% on-time payments",
                    "Credit utilization: 25%"
                ],
                "recommendations": [
                    "Approve credit limit increase",
                    "Monitor credit utilization",
                    "Consider additional products"
                ],
                "visualizations": [
                    {
                        "title": "Credit Score Trend",
                        "subtitle": "Last 12 months",
                        "data": {
                            "current_score": 750,
                            "previous_score": 735,
                            "improvement": 15
                        }
                    }
                ],
                "data": {
                    "customer_profile": {
                        "name": "Test Customer",
                        "credit_score": 750,
                        "current_limit": 10000,
                        "requested_increase": 5000,
                        "income": 75000,
                        "employment_years": 5
                    }
                }
            }
        ],
        "chatHistory": [
            {
                "message_type": "user",
                "content": "What is the customer's credit score?",
                "timestamp": "2025-08-25 10:30:00"
            },
            {
                "message_type": "assistant",
                "content": "The customer's credit score is 750, which is considered excellent. This score indicates a very low risk of default.",
                "timestamp": "2025-08-25 10:30:15"
            }
        ],
        "execution": {
            "execution_id": "test-exec-123",
            "start_time": "2025-08-25 10:00:00",
            "end_time": "2025-08-25 10:05:00"
        },
        "timestamp": "2025-08-25T10:05:00Z"
    }
    
    print("🧪 Testing PDF Generation...")
    print("=" * 50)
    
    try:
        # Generate PDF
        result = pdf_service.generate_decision_documentation(test_data)
        
        if result["success"]:
            print(f"✅ PDF generated successfully!")
            print(f"📄 Filename: {result['filename']}")
            print(f"🔗 URL: {result['pdf_url']}")
            print(f"📝 Summary: {result['summary']}")
            
            # Check if file exists
            file_path = os.path.join("reports", result['filename'])
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"📊 File size: {file_size:,} bytes")
                print(f"✅ File exists and is accessible")
            else:
                print(f"❌ File not found at {file_path}")
                
        else:
            print(f"❌ PDF generation failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
