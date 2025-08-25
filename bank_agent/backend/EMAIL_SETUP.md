# Email Setup for Banking Agent

This document explains how to set up email functionality for sending credit decision emails to customers.

## Overview

The banking agent includes a comprehensive email system that allows operators to:
1. **Finalize credit decisions** with approval/rejection details
2. **Generate professional email content** automatically
3. **Send emails directly** to customers or copy content for manual sending
4. **Track email history** and decision documentation

## Features

### Finalize Decision Tab
- **Decision Type**: Approve or Reject options
- **Approved Amount**: Enter the approved credit limit increase (for approvals)
- **Decision Reason**: Detailed explanation for the decision
- **Customer Email**: Pre-filled from customer profile when available
- **Email Generation**: Automatic professional email content generation
- **Email Sending**: Direct sending or copy to clipboard

### Email Templates
The system generates professional email templates for both approvals and rejections:

**Approval Email Template:**
```
Dear [Customer Name],

Thank you for your credit limit increase request. After careful review of your application and credit profile, I am pleased to inform you that your request has been APPROVED.

Decision Details:
- Approved Amount: $[Amount]
- Decision Date: [Date]

Reason for Approval:
[Detailed reason]

Your new credit limit will be effective immediately. You can view your updated credit limit in your online banking portal or mobile app.

If you have any questions about this decision, please don't hesitate to contact our customer service team.

Best regards,
Banking Team
```

**Rejection Email Template:**
```
Dear [Customer Name],

Thank you for your credit limit increase request. After careful review of your application and credit profile, I regret to inform you that your request has been DECLINED.

Decision Details:
- Decision: Declined
- Decision Date: [Date]

Reason for Decline:
[Detailed reason]

We understand this may be disappointing, and we encourage you to continue building your credit profile. You may be eligible for a credit limit increase in the future as your financial situation improves.

If you have any questions about this decision or would like to discuss ways to improve your credit profile, please don't hesitate to contact our customer service team.

Best regards,
Banking Team
```

## Setup Instructions

### 1. Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=neurostackagent@gmail.com
SENDER_PASSWORD=your_app_password_here
```

### 2. Gmail App Password Setup

To use Gmail for sending emails, you need to create an App Password:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this password in `SENDER_PASSWORD`

### 3. Alternative Email Providers

You can use other SMTP providers by changing the environment variables:

**Outlook/Hotmail:**
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Custom SMTP Server:**
```bash
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

## Usage

### 1. Access the Finalize Decision Tab
- Navigate to the "Data Simulation Studio"
- Click on the "Finalize Decision" tab (5th tab)

### 2. Fill in Decision Details
- **Select Decision**: Choose "Approve" or "Reject"
- **Enter Amount**: For approvals, specify the approved amount
- **Provide Reason**: Detailed explanation for the decision
- **Customer Email**: Will be pre-filled if available in customer profile

### 3. Generate Email Content
- Click "Generate Email" to create professional email content
- Review and edit the generated subject and body if needed

### 4. Send Email
- Click "Send Email" to send directly to the customer
- The system will use the configured SMTP settings
- If SMTP is not configured, email content will be logged for manual sending

## API Endpoints

### Send Email
```http
POST /api/email/send
Content-Type: application/json

{
  "to": "customer@example.com",
  "subject": "Credit Limit Decision",
  "body": "Email body content",
  "decision": "approved",
  "approvedAmount": 5000.0,
  "reason": "Decision reason",
  "customerName": "John Doe",
  "customerId": 123
}
```

### Generate Email Content
```http
POST /api/email/generate
Content-Type: application/json

{
  "customerName": "John Doe",
  "decision": "approved",
  "approvedAmount": 5000.0,
  "reason": "Decision reason",
  "decisionDate": "2024-01-15"
}
```

## Security Considerations

1. **App Passwords**: Use app passwords instead of regular passwords for Gmail
2. **Environment Variables**: Never commit email credentials to version control
3. **Rate Limiting**: Be aware of email sending limits (Gmail: 500/day for regular accounts)
4. **Data Privacy**: Ensure customer email addresses are handled securely

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your email and app password
   - Ensure 2FA is enabled for Gmail
   - Check SMTP server and port settings

2. **Email Not Sending**
   - Check network connectivity
   - Verify SMTP server is accessible
   - Review email service logs

3. **Pre-filled Email Not Working**
   - Ensure customer profile contains email field
   - Check data source configuration
   - Verify customer data is loaded

### Testing

Run the email service test:
```bash
python test_email_service.py
```

This will test both email sending and content generation functionality.

## Future Enhancements

- **Email Templates**: Customizable email templates
- **Email History**: Track sent emails and decisions
- **Bulk Operations**: Send multiple decision emails
- **Email Scheduling**: Schedule emails for specific times
- **Attachment Support**: Include PDF reports or documents
- **Email Tracking**: Track email opens and clicks
