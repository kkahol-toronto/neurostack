import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import CustomerReport, CreateReportRequest, UpdateReportRequest, ReportStatus
import logging

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        # In a real application, this would be a database
        # For now, we'll use in-memory storage with file persistence
        self.reports_file = "customer_reports.json"
        self.reports = self._load_reports()
    
    def _load_reports(self) -> Dict[str, CustomerReport]:
        """Load reports from file storage."""
        try:
            with open(self.reports_file, 'r') as f:
                data = json.load(f)
                reports = {}
                for report_id, report_data in data.items():
                    # Convert string dates back to datetime objects
                    report_data['report_date'] = datetime.fromisoformat(report_data['report_date'])
                    report_data['created_at'] = datetime.fromisoformat(report_data['created_at'])
                    if report_data.get('updated_at'):
                        report_data['updated_at'] = datetime.fromisoformat(report_data['updated_at'])
                    if report_data.get('decision_date'):
                        report_data['decision_date'] = datetime.fromisoformat(report_data['decision_date'])
                    
                    reports[report_id] = CustomerReport(**report_data)
                return reports
        except FileNotFoundError:
            return {}
        except Exception as e:
            logger.error(f"Error loading reports: {e}")
            return {}
    
    def _save_reports(self):
        """Save reports to file storage."""
        try:
            # Convert datetime objects to ISO strings for JSON serialization
            data = {}
            for report_id, report in self.reports.items():
                report_dict = report.dict()
                report_dict['report_date'] = report.report_date.isoformat()
                report_dict['created_at'] = report.created_at.isoformat()
                if report.updated_at:
                    report_dict['updated_at'] = report.updated_at.isoformat()
                if report.decision_date:
                    report_dict['decision_date'] = report.decision_date.isoformat()
                data[report_id] = report_dict
            
            with open(self.reports_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving reports: {e}")
    
    def create_report(self, request: CreateReportRequest, created_by: str) -> CustomerReport:
        """Create a new customer report."""
        try:
            report_id = str(uuid.uuid4())
            now = datetime.now()
            
            report = CustomerReport(
                report_id=report_id,
                customer_id=request.customer_id,
                customer_name=request.customer_name,
                report_date=now,
                inquiry_type=request.inquiry_type,
                inquiry_description=request.inquiry_description,
                ai_summary=request.ai_summary,
                ai_recommendation=request.ai_recommendation,
                suggested_decision=request.suggested_decision,
                current_credit_limit=request.current_credit_limit,
                requested_credit_limit=request.requested_credit_limit,
                credit_limit_increase=request.credit_limit_increase,
                agent_notes=request.agent_notes,
                status=request.status or ReportStatus.PENDING,
                customer_data=request.customer_data,
                created_by=created_by,
                created_at=now
            )
            
            self.reports[report_id] = report
            self._save_reports()
            
            logger.info(f"Created report {report_id} for customer {request.customer_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            raise
    
    def get_report(self, report_id: str) -> Optional[CustomerReport]:
        """Get a report by ID."""
        return self.reports.get(report_id)
    
    def get_reports_by_customer(self, customer_id: int) -> List[CustomerReport]:
        """Get all reports for a specific customer."""
        return [report for report in self.reports.values() if report.customer_id == customer_id]
    
    def get_all_reports(self, limit: Optional[int] = None, offset: int = 0) -> List[CustomerReport]:
        """Get all reports with optional pagination."""
        reports = list(self.reports.values())
        reports.sort(key=lambda x: x.created_at, reverse=True)
        
        if limit:
            return reports[offset:offset + limit]
        return reports[offset:]
    
    def update_report(self, report_id: str, request: UpdateReportRequest, updated_by: str) -> Optional[CustomerReport]:
        """Update an existing report."""
        try:
            if report_id not in self.reports:
                return None
            
            report = self.reports[report_id]
            
            # Update fields if provided
            if request.agent_notes is not None:
                report.agent_notes = request.agent_notes
            
            if request.status is not None:
                report.status = request.status
            
            if request.credit_recommendation is not None:
                report.credit_recommendation = request.credit_recommendation
            
            if request.final_decision is not None:
                report.final_decision = request.final_decision
                report.decision_date = datetime.now()
                report.decision_by = updated_by
            
            if request.current_credit_limit is not None:
                report.current_credit_limit = request.current_credit_limit
            
            if request.requested_credit_limit is not None:
                report.requested_credit_limit = request.requested_credit_limit
            
            if request.credit_limit_increase is not None:
                report.credit_limit_increase = request.credit_limit_increase
            
            report.updated_at = datetime.now()
            
            self._save_reports()
            
            logger.info(f"Updated report {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error updating report: {e}")
            raise
    
    def delete_report(self, report_id: str) -> bool:
        """Delete a report."""
        try:
            if report_id in self.reports:
                del self.reports[report_id]
                self._save_reports()
                logger.info(f"Deleted report {report_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting report: {e}")
            return False
    
    def get_reports_by_status(self, status: ReportStatus) -> List[CustomerReport]:
        """Get reports by status."""
        return [report for report in self.reports.values() if report.status == status]
    
    def get_reports_by_date_range(self, start_date: datetime, end_date: datetime) -> List[CustomerReport]:
        """Get reports within a date range."""
        return [
            report for report in self.reports.values() 
            if start_date <= report.report_date <= end_date
        ]

    def generate_ai_recommendation(self, customer_id: int, customer_data: Dict[str, Any], 
                                 ai_summary: str, inquiry_type: str, inquiry_description: str,
                                 extracted_credit_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate AI recommendation using Neurostack Agent."""
        try:
            # Use Azure OpenAI directly for AI recommendation
            from openai import AzureOpenAI
            import os
            
            # Create a prompt for the Neurostack Agent
            credit_info = ""
            if extracted_credit_data:
                credit_info = f"""
                Extracted Credit Information:
                - Current Credit Limit: ${extracted_credit_data.get('currentCreditLimit', 0):,.2f}
                - Requested Credit Limit: ${extracted_credit_data.get('requestedCreditLimit', 0):,.2f}
                - Credit Limit Increase: ${extracted_credit_data.get('creditLimitIncrease', 0):,.2f}
                - Extraction Method: {extracted_credit_data.get('extractionMethod', 'unknown')}
                """
            
            # Extract key customer data for analysis
            customer_profile = self._extract_customer_profile_for_analysis(customer_data)
            
            prompt = f"""
            As a senior banking credit analyst, provide a comprehensive analysis and recommendation for this credit limit increase request.

            CUSTOMER PROFILE:
            {customer_profile}

            CREDIT REQUEST DETAILS:
            - Inquiry Type: {inquiry_type}
            - Customer Request: {inquiry_description}
            {credit_info}

            Please analyze this request and provide your recommendation in the following JSON format:

            {{
                "financial_analysis": "Detailed analysis including: current credit utilization, payment history, income stability, risk factors, and creditworthiness assessment. Reference specific numbers from the customer profile.",
                "recommendation": "Specific recommendation with clear approval/denial decision. Include reasoning based on the customer's financial profile and risk assessment.",
                "suggested_decision": "Clear decision statement with specific amounts (e.g., 'Approved for credit limit increase from $32,000 to $40,000')"
            }}

            ANALYSIS REQUIREMENTS:
            1. Reference specific data points from the customer profile (utilization rate, payment history, income, etc.)
            2. Assess the risk of the requested increase
            3. Consider the customer's credit behavior and financial stability
            4. Provide a clear, actionable recommendation
            5. Use precise numbers and percentages from the customer data

            Be thorough, professional, and data-driven in your analysis.
            """

            # Call Azure OpenAI for recommendation
            client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            )
            
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "You are a banking AI assistant that provides credit recommendations. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            
            # Try to parse JSON response first
            try:
                import json
                logger.info(f"🤖 Raw AI response: {ai_response}")
                
                # Look for JSON in the response
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = ai_response[json_start:json_end]
                    logger.info(f"🔍 Extracted JSON string: {json_str}")
                    parsed_response = json.loads(json_str)
                    
                    financial_analysis = parsed_response.get('financial_analysis', '')
                    recommendation_text = parsed_response.get('recommendation', '')
                    
                    # Combine the analysis and recommendation
                    recommendation = f"{financial_analysis}\n\n{recommendation_text}"
                    suggested_decision = parsed_response.get('suggested_decision', 'Approved for continued premium banking relationship, with consideration for expanded credit facilities and personalized financial solutions')
                    credit_limits = parsed_response.get('credit_limits', {})
                    
                    logger.info(f"✅ Successfully parsed JSON response from LLM")
                    logger.info(f"✅ Financial analysis length: {len(financial_analysis)}")
                    logger.info(f"✅ Recommendation length: {len(recommendation_text)}")
                    logger.info(f"✅ Combined recommendation length: {len(recommendation)}")
                else:
                    # Fallback to text parsing if no JSON found
                    logger.warning("⚠️ No JSON found in LLM response, using fallback parsing")
                    recommendation = ai_response
                    suggested_decision = self._generate_fallback_decision(customer_data, extracted_credit_data)
                    credit_limits = {}
                    
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"❌ Error parsing JSON response: {e}")
                logger.error(f"❌ AI response that failed to parse: {ai_response}")
                # Fallback to text parsing
                recommendation = ai_response
                suggested_decision = self._generate_fallback_decision(customer_data, extracted_credit_data)
                credit_limits = {}
            
            # If LLM didn't provide credit limits, try simple fallback extraction
            if not credit_limits:
                import re
                inquiry_text = inquiry_description.lower()
                logger.info(f"🔍 LLM didn't provide credit limits, trying fallback extraction from: {inquiry_text}")
                
                # Simple fallback: look for numbers in the text
                credit_pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
                credit_matches = re.findall(credit_pattern, inquiry_text)
                
                if len(credit_matches) >= 2:
                    credit_limits = {
                        "current": float(credit_matches[0].replace(',', '')),
                        "requested": float(credit_matches[1].replace(',', '')),
                        "increase": float(credit_matches[1].replace(',', '')) - float(credit_matches[0].replace(',', ''))
                    }
                    logger.info(f"✅ Fallback extracted credit limits: {credit_limits}")
                elif len(credit_matches) == 1:
                    credit_limits = {
                        "requested": float(credit_matches[0].replace(',', ''))
                    }
                    logger.info(f"✅ Fallback extracted single credit limit: {credit_limits}")
            
            logger.info(f"🔍 Final credit limits being returned: {credit_limits}")
            return {
                "recommendation": recommendation,
                "suggested_decision": suggested_decision,
                "credit_limits": credit_limits
            }
            
        except Exception as e:
            logger.error(f"Error generating AI recommendation: {e}")
            # Return a comprehensive data-driven recommendation
            fallback_decision = self._generate_fallback_decision(customer_data, extracted_credit_data)
            customer_profile = self._extract_customer_profile_for_analysis(customer_data)
            
            # Generate a comprehensive recommendation using customer data
            comprehensive_recommendation = self._generate_comprehensive_recommendation(
                customer_data, inquiry_type, inquiry_description, extracted_credit_data
            )
            
            return {
                "recommendation": comprehensive_recommendation,
                "suggested_decision": fallback_decision,
                "credit_limits": {}
            }

    def extract_credit_limit_info(self, inquiry_description: str, current_credit_limit: float) -> Dict[str, Any]:
        """Extract credit limit information from inquiry description using improved regex and LLM fallback."""
        try:
            import re
            
            text = inquiry_description.lower()
            logger.info(f"🔍 Extracting credit limit info from: '{inquiry_description}'")
            
            # Pattern 1: "increase by X" or "increase limit by X"
            increase_patterns = [
                r'increase\s+limit\s+by\s+(\d+)',
                r'increase\s+by\s+(\d+)',
                r'by\s+(\d+)'
            ]
            
            for pattern in increase_patterns:
                match = re.search(pattern, text)
                if match:
                    amount = float(match.group(1).replace(',', ''))
                    logger.info(f"✅ Found increase amount: {amount} using pattern: {pattern}")
                    return {
                        "increase_amount": amount,
                        "requested_total_limit": None,
                        "extraction_method": "increase_by",
                        "confidence": "high",
                        "reasoning": f"Extracted increase amount of {amount} using pattern matching"
                    }
            
            # Pattern 2: "increased to X" or "limit to be X" or "total limit to be X"
            total_patterns = [
                r'increased\s+to\s+\$?\s*(\d+)',
                r'limit\s+to\s+be\s+\$?\s*(\d+)',
                r'credit\s+limit\s+to\s+be\s+\$?\s*(\d+)',
                r'total\s+(?:credit\s+)?limit\s+to\s+be\s+\$?\s*(\d+)',
                r'to\s+\$?\s*(\d+)',
                r'to\s+(\d+)'
            ]
            
            # Debug: Log all matches for total patterns
            logger.info(f"🔍 Testing total patterns on text: '{text}'")
            for i, pattern in enumerate(total_patterns):
                matches = re.findall(pattern, text)
                logger.info(f"  Pattern {i+1}: '{pattern}' → matches: {matches}")
                if matches:
                    match = re.search(pattern, text)
                    if match:
                        total_limit = float(match.group(1).replace(',', ''))
                        logger.info(f"✅ Found total limit: {total_limit} using pattern: {pattern}")
                        return {
                            "increase_amount": None,
                            "requested_total_limit": total_limit,
                            "extraction_method": "total_limit",
                            "confidence": "high",
                            "reasoning": f"Extracted total limit of {total_limit} using pattern matching"
                        }
            
            for pattern in total_patterns:
                match = re.search(pattern, text)
                if match:
                    total_limit = float(match.group(1).replace(',', ''))
                    logger.info(f"✅ Found total limit: {total_limit} using pattern: {pattern}")
                    return {
                        "increase_amount": None,
                        "requested_total_limit": total_limit,
                        "extraction_method": "total_limit",
                        "confidence": "high",
                        "reasoning": f"Extracted total limit of {total_limit} using pattern matching"
                    }
            
            # Pattern 3: Look for numbers and try to determine if they're increase or total
            number_pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
            numbers = re.findall(number_pattern, text)
            
            if numbers:
                # Try LLM-based extraction for ambiguous cases
                llm_result = self._extract_with_llm(inquiry_description, current_credit_limit)
                if llm_result.get("confidence") == "high":
                    logger.info(f"✅ LLM extraction successful: {llm_result}")
                    return llm_result
                
                # Fallback: assume the largest number is the target
                amounts = [float(num.replace(',', '')) for num in numbers]
                largest_amount = max(amounts)
                
                # If the largest amount is significantly larger than current limit, it's likely a total
                if largest_amount > current_credit_limit * 1.2:
                    logger.info(f"✅ Assuming {largest_amount} is total limit (current: {current_credit_limit})")
                    return {
                        "increase_amount": None,
                        "requested_total_limit": largest_amount,
                        "extraction_method": "total_limit",
                        "confidence": "medium",
                        "reasoning": f"Found number {largest_amount} which is larger than current limit, assuming it's the total limit"
                    }
                else:
                    logger.info(f"✅ Assuming {largest_amount} is increase amount")
                    return {
                        "increase_amount": largest_amount,
                        "requested_total_limit": None,
                        "extraction_method": "increase_by",
                        "confidence": "medium",
                        "reasoning": f"Found number {largest_amount} which is smaller than current limit, assuming it's the increase amount"
                    }
            
            # Final fallback: try LLM extraction
            logger.info("🔄 Trying LLM-based extraction as fallback")
            llm_result = self._extract_with_llm(inquiry_description, current_credit_limit)
            if llm_result.get("confidence") != "low":
                return llm_result
            
            logger.warning("❌ No credit limit information found in description")
            return {
                "increase_amount": None,
                "requested_total_limit": None,
                "extraction_method": "unclear",
                "confidence": "low",
                "reasoning": "No specific amounts found in the description"
            }
                
        except Exception as e:
            logger.error(f"Error extracting credit limit info: {e}")
            return {
                "increase_amount": None,
                "requested_total_limit": None,
                "extraction_method": "unclear",
                "confidence": "low",
                "reasoning": f"Extraction error: {str(e)}"
            }

    def _extract_customer_profile_for_analysis(self, customer_data: Dict[str, Any]) -> str:
        """Extract key customer profile data for AI analysis."""
        try:
            profile_sections = []
            
            # Banking data
            if customer_data.get('internal_banking_data', {}).get('data'):
                banking = customer_data['internal_banking_data']['data']
                profile_sections.append(f"""
BANKING RELATIONSHIP:
- Current Credit Limit: ${banking.get('current_credit_limit', 0):,.2f}
- Current Balance: ${banking.get('current_balance', 0):,.2f}
- Credit Utilization Rate: {banking.get('utilization_rate', 0):.1f}%
- On-Time Payments (12 months): {banking.get('on_time_payments_12m', 0)}
- Late Payments (12 months): {banking.get('late_payments_12m', 0)}
- Account Tenure: {banking.get('tenure_months', 0)} months
""")
            
            # Credit bureau data
            if customer_data.get('credit_bureau_data', {}).get('data'):
                credit = customer_data['credit_bureau_data']['data']
                profile_sections.append(f"""
CREDIT BUREAU DATA:
- FICO Score 8: {credit.get('fico_score_8', 'N/A')}
- FICO Score 9: {credit.get('fico_score_9', 'N/A')}
- Total Accounts: {credit.get('total_accounts_bureau', 'N/A')}
- Delinquencies (30+ days, 12 months): {credit.get('delinquencies_30_plus_12m', 0)}
""")
            
            # Income and ability to pay
            if customer_data.get('income_ability_to_pay', {}).get('data'):
                income = customer_data['income_ability_to_pay']['data']
                profile_sections.append(f"""
INCOME & ABILITY TO PAY:
- Verified Annual Income: ${income.get('verified_annual_income', 0):,.2f}
- Debt-to-Income Ratio: {income.get('debt_to_income_ratio', 0):.1%}
- Total Monthly Debt Payments: ${income.get('total_monthly_debt_payments', 0):,.2f}
- Income Stability Score: {income.get('income_stability_score', 0):.1f}/100
""")
            
            # Demographics
            if customer_data.get('customer_demographics', {}).get('data'):
                demo = customer_data['customer_demographics']['data']
                profile_sections.append(f"""
CUSTOMER DEMOGRAPHICS:
- Customer Segment: {demo.get('customer_segment', 'N/A')}
- Employment Status: {demo.get('employment_status', 'N/A')}
- Job Title: {demo.get('job_title', 'N/A')}
- Employer: {demo.get('employer_name', 'N/A')}
- Customer Since: {demo.get('customer_since', 'N/A')}
- Household Size: {demo.get('household_size', 'N/A')}
""")
            
            # Fraud/KYC data
            if customer_data.get('fraud_kyc_compliance', {}).get('data'):
                fraud = customer_data['fraud_kyc_compliance']['data']
                profile_sections.append(f"""
FRAUD & COMPLIANCE:
- Fraud Risk Score: {fraud.get('overall_fraud_risk_score', 0):.1f}/100
- Risk Level: {fraud.get('risk_level', 'N/A')}
- KYC Score: {fraud.get('kyc_score', 0):.1f}/100
- Identity Verification: {fraud.get('identity_verification_status', 'N/A')}
""")
            
            return '\n'.join(profile_sections) if profile_sections else "No customer profile data available."
            
        except Exception as e:
            logger.error(f"Error extracting customer profile: {e}")
            return "Error extracting customer profile data."

    def generate_investigation_plan(self, customer_id: int, customer_name: str, customer_data: Dict[str, Any], report_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a comprehensive investigation plan for data processing stage."""
        try:
            # Extract key customer data for analysis
            banking_data = customer_data.get('internal_banking_data', {}).get('data', {})
            credit_data = customer_data.get('credit_bureau_data', {}).get('data', {})
            income_data = customer_data.get('income_ability_to_pay', {}).get('data', {})
            demo_data = customer_data.get('customer_demographics', {}).get('data', {})
            
            # Generate investigation steps based on customer profile
            investigation_steps = []
            
            # Data Collection Steps
            investigation_steps.append({
                "id": "similar_customers",
                "title": "Analyze Similar Customer Profiles",
                "description": f"Pull data for customers with similar profiles: FICO score {credit_data.get('fico_score_8', 'N/A')}, income range ${income_data.get('verified_annual_income', 0):,.0f}, and {demo_data.get('employment_status', 'N/A')} employment status. Compare credit utilization patterns and payment behaviors.",
                "category": "data_collection",
                "priority": "high",
                "estimatedTime": "15-20 min"
            })
            
            investigation_steps.append({
                "id": "geographic_analysis",
                "title": "Geographic Risk Assessment",
                "description": f"Analyze credit performance of customers in {demo_data.get('city', 'N/A')}, {demo_data.get('state', 'N/A')}. Check local economic indicators, unemployment rates, and housing market conditions that may affect repayment ability.",
                "category": "data_collection",
                "priority": "medium",
                "estimatedTime": "10-15 min"
            })
            
            investigation_steps.append({
                "id": "employer_analysis",
                "title": "Employer Financial Health Check",
                "description": f"Research {demo_data.get('employer_name', 'N/A')} financial stability, industry trends, and employment outlook. Check company credit ratings, recent news, and sector performance to assess job security.",
                "category": "data_collection",
                "priority": "high",
                "estimatedTime": "20-25 min"
            })
            
            # Analysis Steps
            investigation_steps.append({
                "id": "utilization_trends",
                "title": "Credit Utilization Pattern Analysis",
                "description": f"Analyze historical credit utilization trends for customer. Current utilization: {banking_data.get('utilization_rate', 0):.1f}%. Check seasonal patterns, spending behaviors, and correlation with income cycles.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "15-20 min"
            })
            
            investigation_steps.append({
                "id": "payment_behavior",
                "title": "Payment Behavior Deep Dive",
                "description": f"Detailed analysis of payment history: {banking_data.get('on_time_payments_12m', 0)} on-time payments, {banking_data.get('late_payments_12m', 0)} late payments. Identify patterns, timing of payments, and correlation with credit limit changes.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "10-15 min"
            })
            
            # Scenario Analysis Steps
            investigation_steps.append({
                "id": "scenario_modeling",
                "title": "Credit Limit Increase Scenarios",
                "description": "Model different credit limit increase scenarios (25%, 50%, 75%, 100% increase) and calculate probability of default, expected credit utilization, and impact on credit score. Include stress testing for economic downturns.",
                "category": "scenario",
                "priority": "high",
                "estimatedTime": "25-30 min"
            })
            
            investigation_steps.append({
                "id": "repayment_probability",
                "title": "Monthly Repayment Probability Analysis",
                "description": "Calculate probability of customer paying back borrowed amount per month across different credit limit increases. Model cash flow scenarios and debt-to-income ratios under various credit conditions.",
                "category": "scenario",
                "priority": "high",
                "estimatedTime": "20-25 min"
            })
            
            # Visualization Steps
            investigation_steps.append({
                "id": "utilization_graphs",
                "title": "Credit Utilization Visualization",
                "description": "Create graphs showing credit utilization trends over time, seasonal patterns, and correlation with payment behaviors. Include comparison with similar customer profiles.",
                "category": "visualization",
                "priority": "medium",
                "estimatedTime": "15-20 min"
            })
            
            investigation_steps.append({
                "id": "risk_heatmap",
                "title": "Risk Assessment Heatmap",
                "description": "Generate risk heatmap showing probability of default vs. credit limit increase amounts. Include confidence intervals and sensitivity analysis for key risk factors.",
                "category": "visualization",
                "priority": "medium",
                "estimatedTime": "20-25 min"
            })
            
            investigation_steps.append({
                "id": "comparison_charts",
                "title": "Peer Comparison Analysis",
                "description": "Create comparison charts showing customer performance vs. similar profiles. Include credit utilization, payment history, and risk metrics for benchmarking.",
                "category": "visualization",
                "priority": "low",
                "estimatedTime": "15-20 min"
            })
            
            return {
                "steps": investigation_steps,
                "summary": f"Generated comprehensive investigation plan for {customer_name} with {len(investigation_steps)} analysis steps covering data collection, analysis, scenario modeling, and visualization.",
                "total_estimated_time": "2-3 hours",
                "high_priority_steps": len([step for step in investigation_steps if step["priority"] == "high"])
            }
            
        except Exception as e:
            logger.error(f"Error generating investigation plan: {e}")
            return {
                "steps": [],
                "summary": "Error generating investigation plan",
                "total_estimated_time": "Unknown",
                "high_priority_steps": 0
            }

    def _generate_comprehensive_recommendation(self, customer_data: Dict[str, Any], inquiry_type: str, inquiry_description: str, extracted_credit_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate a comprehensive recommendation using customer data."""
        try:
            # Extract key customer data
            banking_data = customer_data.get('internal_banking_data', {}).get('data', {})
            credit_data = customer_data.get('credit_bureau_data', {}).get('data', {})
            income_data = customer_data.get('income_ability_to_pay', {}).get('data', {})
            demo_data = customer_data.get('customer_demographics', {}).get('data', {})
            
            # Build comprehensive recommendation
            recommendation_parts = []
            
            # Header
            recommendation_parts.append(f"Based on the customer inquiry ({inquiry_type}), I recommend a thorough review of the customer's financial profile.")
            recommendation_parts.append(f"The inquiry appears to be related to: {inquiry_description}")
            recommendation_parts.append("")
            
            # Banking Relationship Analysis
            if banking_data:
                recommendation_parts.append("BANKING RELATIONSHIP ANALYSIS:")
                recommendation_parts.append(f"- Current Credit Limit: ${banking_data.get('current_credit_limit', 0):,.2f}")
                recommendation_parts.append(f"- Current Balance: ${banking_data.get('current_balance', 0):,.2f}")
                recommendation_parts.append(f"- Credit Utilization Rate: {banking_data.get('utilization_rate', 0):.1f}%")
                recommendation_parts.append(f"- On-Time Payments (12 months): {banking_data.get('on_time_payments_12m', 0)}")
                recommendation_parts.append(f"- Late Payments (12 months): {banking_data.get('late_payments_12m', 0)}")
                recommendation_parts.append(f"- Account Tenure: {banking_data.get('tenure_months', 0)} months")
                recommendation_parts.append("")
            
            # Credit Bureau Analysis
            if credit_data:
                recommendation_parts.append("CREDIT BUREAU ANALYSIS:")
                recommendation_parts.append(f"- FICO Score 8: {credit_data.get('fico_score_8', 'N/A')}")
                recommendation_parts.append(f"- FICO Score 9: {credit_data.get('fico_score_9', 'N/A')}")
                recommendation_parts.append(f"- Total Accounts: {credit_data.get('total_accounts_bureau', 'N/A')}")
                recommendation_parts.append(f"- Delinquencies (30+ days, 12 months): {credit_data.get('delinquencies_30_plus_12m', 0)}")
                recommendation_parts.append("")
            
            # Income & Ability to Pay
            if income_data:
                recommendation_parts.append("INCOME & ABILITY TO PAY:")
                recommendation_parts.append(f"- Verified Annual Income: ${income_data.get('verified_annual_income', 0):,.2f}")
                recommendation_parts.append(f"- Debt-to-Income Ratio: {income_data.get('debt_to_income_ratio', 0):.1%}")
                recommendation_parts.append(f"- Total Monthly Debt Payments: ${income_data.get('total_monthly_debt_payments', 0):,.2f}")
                recommendation_parts.append(f"- Income Stability Score: {income_data.get('income_stability_score', 0):.1f}/100")
                recommendation_parts.append("")
            
            # Request Analysis
            if extracted_credit_data:
                recommendation_parts.append("CREDIT REQUEST ANALYSIS:")
                recommendation_parts.append(f"- Requested Increase: ${extracted_credit_data.get('creditLimitIncrease', 0):,.2f}")
                recommendation_parts.append(f"- New Total Limit: ${extracted_credit_data.get('requestedCreditLimit', 0):,.2f}")
                recommendation_parts.append(f"- Increase Percentage: {(extracted_credit_data.get('creditLimitIncrease', 0) / extracted_credit_data.get('currentCreditLimit', 1) * 100):.1f}%")
                recommendation_parts.append("")
            
            # Risk Assessment
            recommendation_parts.append("RISK ASSESSMENT:")
            utilization_rate = banking_data.get('utilization_rate', 0)
            fico_score = credit_data.get('fico_score_8', 0)
            dti_ratio = income_data.get('debt_to_income_ratio', 0)
            
            risk_factors = []
            if utilization_rate > 70:
                risk_factors.append("High credit utilization")
            if fico_score < 650:
                risk_factors.append("Low FICO score")
            if dti_ratio > 0.43:
                risk_factors.append("High debt-to-income ratio")
            
            if not risk_factors:
                recommendation_parts.append("- Low risk profile with strong credit indicators")
            else:
                recommendation_parts.append(f"- Risk factors identified: {', '.join(risk_factors)}")
            
            recommendation_parts.append("")
            recommendation_parts.append("Please review the customer data and make an informed decision.")
            
            return "\n".join(recommendation_parts)
            
        except Exception as e:
            logger.error(f"Error generating comprehensive recommendation: {e}")
            return f"Based on the customer inquiry ({inquiry_type}), I recommend a thorough review of the customer's financial profile. The inquiry appears to be related to {inquiry_description}. Please review the customer data and make an informed decision."

    def _extract_with_llm(self, inquiry_description: str, current_credit_limit: float) -> Dict[str, Any]:
        """Extract credit limit information using LLM for complex cases."""
        try:
            from openai import AzureOpenAI
            import os
            import json
            
            prompt = f"""
            Analyze this credit limit inquiry and extract the requested amount. The customer's current credit limit is ${current_credit_limit:,.2f}.

            Inquiry: "{inquiry_description}"

            Determine if the customer is requesting:
            1. An INCREASE BY a specific amount (e.g., "increase by $5,000")
            2. A TOTAL LIMIT to be a specific amount (e.g., "increase to $40,000")

            Respond with JSON only:
            {{
                "increase_amount": null or the increase amount if specified,
                "requested_total_limit": null or the total limit if specified,
                "extraction_method": "increase_by" or "total_limit",
                "confidence": "high" or "medium",
                "reasoning": "brief explanation of your analysis"
            }}

            Examples:
            - "increase by 5000" → {{"increase_amount": 5000, "requested_total_limit": null, "extraction_method": "increase_by"}}
            - "increase to 40000" → {{"increase_amount": null, "requested_total_limit": 40000, "extraction_method": "total_limit"}}
            - "want limit to be 50000" → {{"increase_amount": null, "requested_total_limit": 50000, "extraction_method": "total_limit"}}
            """

            client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            )
            
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "You are a banking assistant that extracts credit limit information. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"🤖 LLM response: {ai_response}")
            
            # Parse JSON response
            try:
                result = json.loads(ai_response)
                logger.info(f"✅ LLM extraction successful: {result}")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse LLM JSON response: {e}")
                return {
                    "increase_amount": None,
                    "requested_total_limit": None,
                    "extraction_method": "unclear",
                    "confidence": "low",
                    "reasoning": f"LLM response parsing failed: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"❌ LLM extraction failed: {e}")
            return {
                "increase_amount": None,
                "requested_total_limit": None,
                "extraction_method": "unclear",
                "confidence": "low",
                "reasoning": f"LLM extraction error: {str(e)}"
            }

    def _generate_fallback_decision(self, customer_data: Dict[str, Any], extracted_credit_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate a fallback decision based on customer data when AI fails."""
        try:
            # Extract key metrics
            utilization_rate = 0
            fico_score = 0
            current_limit = 0
            requested_limit = 0
            increase_amount = 0
            
            if customer_data.get('internal_banking_data', {}).get('data'):
                banking = customer_data['internal_banking_data']['data']
                utilization_rate = banking.get('utilization_rate', 0)
                current_limit = banking.get('current_credit_limit', 0)
            
            if customer_data.get('credit_bureau_data', {}).get('data'):
                credit = customer_data['credit_bureau_data']['data']
                fico_score = credit.get('fico_score_8', 0)
            
            if extracted_credit_data:
                requested_limit = extracted_credit_data.get('requestedCreditLimit', 0)
                increase_amount = extracted_credit_data.get('creditLimitIncrease', 0)
            
            # Generate decision based on risk factors
            risk_factors = []
            if utilization_rate > 70:
                risk_factors.append(f"high credit utilization ({utilization_rate:.1f}%)")
            if fico_score < 650:
                risk_factors.append(f"low FICO score ({fico_score})")
            if increase_amount > current_limit * 0.5:
                risk_factors.append(f"large increase request ({increase_amount:,.0f})")
            
            if not risk_factors:
                return f"Approved for credit limit increase from ${current_limit:,.0f} to ${requested_limit:,.0f}. Customer demonstrates strong creditworthiness with {utilization_rate:.1f}% utilization and FICO score of {fico_score}."
            else:
                return f"Approved with conditions for credit limit increase from ${current_limit:,.0f} to ${requested_limit:,.0f}. Monitor: {', '.join(risk_factors)}."
                
        except Exception as e:
            logger.error(f"Error generating fallback decision: {e}")
            return "Approved for continued premium banking relationship, with consideration for expanded credit facilities and personalized financial solutions."

# Global instance
report_service = ReportService()
