"""
Email Service for Banking Agent

Handles sending credit decision emails to customers.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "neurostackagent@gmail.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        
    async def send_credit_decision_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send credit decision email to customer
        
        Args:
            email_data: Dictionary containing email details
                - to: Customer email address
                - subject: Email subject
                - body: Email body
                - decision: 'approved' or 'rejected'
                - approvedAmount: Amount approved (if applicable)
                - reason: Decision reason
                - customerName: Customer name
                - customerId: Customer ID
                
        Returns:
            Dictionary with success status and message
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = email_data['to']
            msg['Subject'] = email_data['subject']
            
            # Add body
            msg.attach(MIMEText(email_data['body'], 'plain'))
            
            # Send email
            if self.sender_password:  # Only send if password is configured
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
                
                logger.info(f"Email sent successfully to {email_data['to']}")
                return {
                    "success": True,
                    "message": "Email sent successfully",
                    "email_id": f"email_{email_data['customerId']}_{int(os.urandom(4).hex(), 16)}"
                }
            else:
                # Log email data for manual sending
                logger.info(f"Email data logged (SMTP not configured): {email_data}")
                return {
                    "success": True,
                    "message": "Email data logged for manual sending",
                    "email_data": email_data
                }
                
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }
    
    def generate_email_content(self, decision_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate email content based on decision data
        
        Args:
            decision_data: Decision information
            
        Returns:
            Dictionary with subject and body
        """
        customer_name = decision_data.get('customerName', 'Valued Customer')
        decision = decision_data.get('decision', 'rejected')
        
        if decision == 'approved':
            approved_amount = decision_data.get('approvedAmount', 0)
            subject = f"Credit Limit Increase Approved - {customer_name}"
            body = f"""Dear {customer_name},

Thank you for your credit limit increase request. After careful review of your application and credit profile, I am pleased to inform you that your request has been APPROVED.

Decision Details:
- Approved Amount: ${approved_amount:,}
- Decision Date: {decision_data.get('decisionDate', 'Today')}

Reason for Approval:
{decision_data.get('reason', 'Based on your excellent credit profile and payment history.')}

Your new credit limit will be effective immediately. You can view your updated credit limit in your online banking portal or mobile app.

If you have any questions about this decision, please don't hesitate to contact our customer service team.

Best regards,
Banking Team"""
        else:
            subject = f"Credit Limit Decision - {customer_name}"
            body = f"""Dear {customer_name},

Thank you for your credit limit increase request. After careful review of your application and credit profile, I regret to inform you that your request has been DECLINED.

Decision Details:
- Decision: Declined
- Decision Date: {decision_data.get('decisionDate', 'Today')}

Reason for Decline:
{decision_data.get('reason', 'Based on our current lending criteria and your credit profile.')}

We understand this may be disappointing, and we encourage you to continue building your credit profile. You may be eligible for a credit limit increase in the future as your financial situation improves.

If you have any questions about this decision or would like to discuss ways to improve your credit profile, please don't hesitate to contact our customer service team.

Best regards,
Banking Team"""
        
        return {
            "subject": subject,
            "body": body
        }

# Global email service instance
email_service = EmailService()
