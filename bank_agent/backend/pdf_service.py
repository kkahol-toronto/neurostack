"""
PDF Generation Service for Banking Agent

Generates comprehensive PDF reports for credit decision documentation.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import base64
import io

logger = logging.getLogger(__name__)

class PDFService:
    """Service for generating PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkgreen
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14
        ))
        
        # Table header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER
        ))
        
        # Table cell style
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT
        ))
    
    def generate_decision_documentation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive decision documentation PDF
        
        Args:
            data: Dictionary containing all decision documentation data
            
        Returns:
            Dictionary with success status, PDF URL, and summary
        """
        try:
            # Create PDF filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"decision_doc_{data['customerId']}_{timestamp}.pdf"
            filepath = os.path.join("reports", filename)
            
            # Ensure reports directory exists
            os.makedirs("reports", exist_ok=True)
            
            # Generate PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Add logo and header
            story.extend(self._create_header(data))
            
            # Add executive summary
            story.extend(self._create_executive_summary(data))
            
            # Add customer information
            story.extend(self._create_customer_info(data))
            
            # Add investigation results
            story.extend(self._create_investigation_results(data))
            
            # Add AI analysis
            story.extend(self._create_ai_analysis(data))
            
            # Add visualizations
            story.extend(self._create_visualizations(data))
            
            # Add chat history
            story.extend(self._create_chat_history(data))
            
            # Add decision details
            story.extend(self._create_decision_details(data))
            
            # Add email communication
            story.extend(self._create_email_communication(data))
            
            # Add footer
            story.extend(self._create_footer(data))
            
            # Build PDF
            doc.build(story)
            
            # Generate summary
            summary = self._generate_summary(data)
            
            return {
                "success": True,
                "pdf_url": f"/reports/{filename}",
                "summary": summary,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate PDF: {str(e)}"
            }
    
    def _create_header(self, data: Dict[str, Any]) -> List:
        """Create PDF header with logo and title"""
        elements = []
        
        # Add logo if exists
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logo.png")
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=1.5*inch, height=1*inch)
                elements.append(img)
            except Exception as e:
                logger.warning(f"Could not add logo: {e}")
        
        # Add title
        title = Paragraph("Credit Decision Documentation", self.styles['CustomTitle'])
        elements.append(title)
        
        # Add subtitle
        subtitle = Paragraph(f"Customer: {data['customerName']} (ID: {data['customerId']})", self.styles['SectionHeader'])
        elements.append(subtitle)
        
        # Add timestamp
        timestamp = Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['CustomBodyText'])
        elements.append(timestamp)
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_executive_summary(self, data: Dict[str, Any]) -> List:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        decision_text = "APPROVED" if data['decision'] == 'approved' else "REJECTED"
        decision_color = colors.green if data['decision'] == 'approved' else colors.red
        
        summary_data = [
            ["Decision", decision_text],
            ["Customer Name", data['customerName']],
            ["Customer ID", str(data['customerId'])],
            ["Decision Date", datetime.now().strftime('%B %d, %Y')],
            ["Reason", data['reason']]
        ]
        
        if data['decision'] == 'approved' and data.get('approvedAmount'):
            summary_data.append(["Approved Amount", f"${data['approvedAmount']:,.2f}"])
        
        # Create summary table
        table = Table(summary_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, 0), decision_color),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_customer_info(self, data: Dict[str, Any]) -> List:
        """Create customer information section"""
        elements = []
        
        elements.append(Paragraph("Customer Information", self.styles['SectionHeader']))
        
        # Extract customer profile from investigation results
        customer_profile = {}
        if data.get('investigationResults'):
            for result in data['investigationResults']:
                if result.get('data', {}).get('customer_profile'):
                    customer_profile = result['data']['customer_profile']
                    break
        
        if customer_profile:
            profile_data = []
            for key, value in customer_profile.items():
                if value is not None:
                    formatted_key = key.replace('_', ' ').title()
                    if isinstance(value, (int, float)) and 'amount' in key.lower() or 'limit' in key.lower():
                        formatted_value = f"${value:,.2f}"
                    elif isinstance(value, (int, float)) and 'score' in key.lower():
                        formatted_value = str(value)
                    else:
                        formatted_value = str(value)
                    profile_data.append([formatted_key, formatted_value])
            
            if profile_data:
                table = Table(profile_data, colWidths=[2*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(table)
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_investigation_results(self, data: Dict[str, Any]) -> List:
        """Create investigation results section"""
        elements = []
        
        elements.append(Paragraph("Investigation Results", self.styles['SectionHeader']))
        
        if data.get('investigationResults'):
            for i, result in enumerate(data['investigationResults'], 1):
                elements.append(Paragraph(f"Step {i}: {result.get('step_title', 'Unknown Step')}", self.styles['SubsectionHeader']))
                
                # Add execution details
                details = [
                    ["Status", result.get('status', 'Unknown')],
                    ["Execution Time", f"{result.get('execution_time', 0):.2f} seconds"]
                ]
                
                table = Table(details, colWidths=[2*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(table)
                
                # Add insights if available
                if result.get('insights'):
                    elements.append(Paragraph("Key Insights:", self.styles['CustomBodyText']))
                    for insight in result['insights']:
                        elements.append(Paragraph(f"• {insight}", self.styles['CustomBodyText']))
                
                elements.append(Spacer(1, 10))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_ai_analysis(self, data: Dict[str, Any]) -> List:
        """Create AI analysis section"""
        elements = []
        
        elements.append(Paragraph("AI Analysis & Recommendations", self.styles['SectionHeader']))
        
        if data.get('investigationResults'):
            for result in data['investigationResults']:
                if result.get('recommendations'):
                    elements.append(Paragraph(f"AI Recommendations from {result.get('step_title', 'Analysis')}:", self.styles['SubsectionHeader']))
                    for rec in result['recommendations']:
                        elements.append(Paragraph(f"• {rec}", self.styles['CustomBodyText']))
                    elements.append(Spacer(1, 10))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_visualizations(self, data: Dict[str, Any]) -> List:
        """Create visualizations section"""
        elements = []
        
        elements.append(Paragraph("Data Visualizations", self.styles['SectionHeader']))
        
        if data.get('investigationResults'):
            for result in data['investigationResults']:
                if result.get('visualizations'):
                    elements.append(Paragraph(f"Visualizations from {result.get('step_title', 'Analysis')}:", self.styles['SubsectionHeader']))
                    
                    for viz in result['visualizations']:
                        elements.append(Paragraph(f"• {viz.get('title', 'Visualization')}: {viz.get('subtitle', '')}", self.styles['CustomBodyText']))
                        
                        # Add visualization data summary
                        if viz.get('data'):
                            data_summary = []
                            for key, value in viz['data'].items():
                                if isinstance(value, (int, float)):
                                    if 'percentage' in key.lower():
                                        formatted_value = f"{value:.1f}%"
                                    elif 'amount' in key.lower() or 'limit' in key.lower():
                                        formatted_value = f"${value:,.2f}"
                                    else:
                                        formatted_value = f"{value:,.0f}"
                                else:
                                    formatted_value = str(value)
                                data_summary.append([key.replace('_', ' ').title(), formatted_value])
                            
                            if data_summary:
                                table = Table(data_summary, colWidths=[2*inch, 2*inch])
                                table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                ]))
                                elements.append(table)
                                elements.append(Spacer(1, 10))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_chat_history(self, data: Dict[str, Any]) -> List:
        """Create chat history section"""
        elements = []
        
        elements.append(Paragraph("Chat History & AI Interactions", self.styles['SectionHeader']))
        
        if data.get('chatHistory'):
            for i, message in enumerate(data['chatHistory'], 1):
                role = message.get('message_type', 'unknown').title()
                content = message.get('content', '')
                timestamp = message.get('timestamp', '')
                
                elements.append(Paragraph(f"{i}. {role} ({timestamp}):", self.styles['SubsectionHeader']))
                elements.append(Paragraph(content, self.styles['CustomBodyText']))
                elements.append(Spacer(1, 8))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_decision_details(self, data: Dict[str, Any]) -> List:
        """Create decision details section"""
        elements = []
        
        elements.append(Paragraph("Final Decision Details", self.styles['SectionHeader']))
        
        decision_data = [
            ["Decision", data['decision'].upper()],
            ["Decision Date", datetime.now().strftime('%B %d, %Y')],
            ["Decision Time", datetime.now().strftime('%I:%M %p')],
            ["Reason", data['reason']]
        ]
        
        if data['decision'] == 'approved' and data.get('approvedAmount'):
            decision_data.append(["Approved Amount", f"${data['approvedAmount']:,.2f}"])
        
        table = Table(decision_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, 0), colors.green if data['decision'] == 'approved' else colors.red),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_email_communication(self, data: Dict[str, Any]) -> List:
        """Create email communication section"""
        elements = []
        
        elements.append(Paragraph("Email Communication", self.styles['SectionHeader']))
        
        if data.get('emailData'):
            email_data = [
                ["To", data['emailData'].get('to', 'N/A')],
                ["Subject", data['emailData'].get('subject', 'N/A')],
                ["Sent Date", datetime.now().strftime('%B %d, %Y at %I:%M %p')]
            ]
            
            table = Table(email_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(table)
            
            # Add email body
            elements.append(Paragraph("Email Content:", self.styles['SubsectionHeader']))
            email_body = data['emailData'].get('body', '')
            # Split email body into paragraphs
            paragraphs = email_body.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), self.styles['CustomBodyText']))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_footer(self, data: Dict[str, Any]) -> List:
        """Create PDF footer"""
        elements = []
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Generated by Banking Agent AI System", self.styles['CustomBodyText']))
        elements.append(Paragraph(f"Report ID: {data['customerId']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", self.styles['CustomBodyText']))
        elements.append(Paragraph("This document contains confidential information and should be handled accordingly.", self.styles['CustomBodyText']))
        
        return elements
    
    def _generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate a summary of the decision documentation"""
        decision = data['decision'].upper()
        customer_name = data['customerName']
        customer_id = data['customerId']
        
        summary = f"Credit decision documentation generated for {customer_name} (ID: {customer_id}). "
        summary += f"Decision: {decision}. "
        
        if data.get('investigationResults'):
            summary += f"Analysis included {len(data['investigationResults'])} investigation steps. "
        
        if data.get('chatHistory'):
            summary += f"Documented {len(data['chatHistory'])} chat interactions. "
        
        summary += f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}."
        
        return summary

# Global PDF service instance
pdf_service = PDFService()
