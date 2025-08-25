import json
import uuid
import os
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import CustomerReport, CreateReportRequest, UpdateReportRequest, ReportStatus, InvestigationStrategy, CreateStrategyRequest, UpdateStrategyRequest
import logging
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

def get_azure_openai_client():
    """Initialize Azure OpenAI client with environment variables"""
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        logger.info(f"Azure OpenAI Endpoint: {endpoint}")
        logger.info(f"Azure OpenAI Key: {'***' + api_key[-4:] if api_key else 'NOT SET'}")
        
        if not endpoint or not api_key:
            raise ValueError("Azure OpenAI endpoint and API key must be set in environment variables")
        
        # Check if this is an APIM endpoint
        if "azure-api.net" in endpoint:
            # For APIM endpoints, we need to use the subscription key header
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version,
                default_headers={
                    "Ocp-Apim-Subscription-Key": api_key
                }
            )
            logger.info(f"✅ APIM endpoint configured: {endpoint}")
        else:
            # Standard Azure OpenAI endpoint
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
        
        logger.info("✅ Azure OpenAI client initialized successfully")
        return client
        
    except Exception as e:
        logger.error(f"Error initializing Azure OpenAI client: {e}")
        raise

class ReportService:
    def __init__(self):
        # In a real application, this would be a database
        # For now, we'll use in-memory storage with file persistence
        self.reports_file = "customer_reports.json"
        self.strategies_file = "investigation_strategies.json"
        self.reports = self._load_reports()
        self.strategies = self._load_strategies()
    
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
    
    def _load_strategies(self) -> Dict[str, InvestigationStrategy]:
        """Load strategies from file storage."""
        try:
            with open(self.strategies_file, 'r') as f:
                data = json.load(f)
                strategies = {}
                for strategy_id, strategy_data in data.items():
                    # Convert string dates back to datetime objects
                    strategy_data['created_at'] = datetime.fromisoformat(strategy_data['created_at'])
                    if strategy_data.get('updated_at'):
                        strategy_data['updated_at'] = datetime.fromisoformat(strategy_data['updated_at'])
                    
                    strategies[strategy_id] = InvestigationStrategy(**strategy_data)
                return strategies
        except FileNotFoundError:
            return {}
        except Exception as e:
            logger.error(f"Error loading strategies: {e}")
            return {}
    
    def _save_strategies(self):
        """Save strategies to file storage."""
        try:
            # Convert datetime objects to ISO strings for JSON serialization
            data = {}
            for strategy_id, strategy in self.strategies.items():
                strategy_dict = strategy.dict()
                strategy_dict['created_at'] = strategy.created_at.isoformat()
                if strategy.updated_at:
                    strategy_dict['updated_at'] = strategy.updated_at.isoformat()
                data[strategy_id] = strategy_dict
            
            with open(self.strategies_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving strategies: {e}")
    
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
            client = get_azure_openai_client()
            
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

    async def generate_investigation_plan(self, customer_id: int, customer_name: str, customer_data: Dict[str, Any], report_id: Optional[str] = None, current_steps: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate a comprehensive investigation strategy for analysis stage."""
        try:
            # Extract key customer data for analysis
            banking_data = customer_data.get('internal_banking_data', {}).get('data', {})
            credit_data = customer_data.get('credit_bureau_data', {}).get('data', {})
            income_data = customer_data.get('income_ability_to_pay', {}).get('data', {})
            demo_data = customer_data.get('customer_demographics', {}).get('data', {})
            
            # Analyze customer profile to determine strategy focus
            fico_score = credit_data.get('fico_score_8', 0)
            utilization_rate = banking_data.get('utilization_rate', 0)
            late_payments = banking_data.get('late_payments_12m', 0)
            income = income_data.get('verified_annual_income', 0)
            employment_status = demo_data.get('employment_status', 'unknown')
            
            # Determine risk profile and strategy focus
            risk_profile = self._determine_risk_profile(fico_score, utilization_rate, late_payments, income)
            strategy_focus = self._determine_strategy_focus(risk_profile, employment_status, income)
            
            # If current steps are provided, personalize the strategy using LLM
            if current_steps:
                investigation_steps = await self._personalize_strategy_with_llm(
                    customer_data, current_steps, strategy_focus, risk_profile
                )
            else:
                # Generate basic boilerplate steps
                investigation_steps = self._generate_basic_boilerplate_steps(banking_data, credit_data, income_data, demo_data)
                # Add common steps that apply to all strategies (only for initial generation)
                investigation_steps.extend(self._generate_common_steps(banking_data, credit_data, income_data, demo_data))
            
            return {
                "steps": investigation_steps,
                "summary": f"Generated {strategy_focus.replace('_', ' ').title()} investigation strategy for {customer_name} ({risk_profile.replace('_', ' ').title()} risk profile) with {len(investigation_steps)} analysis steps covering data collection, analysis, scenario modeling, and visualization.",
                "total_estimated_time": "2-3 hours",
                "high_priority_steps": len([step for step in investigation_steps if step["priority"] == "high"]),
                "strategy_focus": strategy_focus,
                "risk_profile": risk_profile
            }
        except Exception as e:
            logger.error(f"Error generating investigation strategy: {e}")
            return {
                "steps": [],
                "summary": "Error generating investigation strategy",
                "total_estimated_time": "Unknown",
                "high_priority_steps": 0
            }

    def _generate_basic_boilerplate_steps(self, banking_data: Dict, credit_data: Dict, income_data: Dict, demo_data: Dict) -> List[Dict]:
        """Generate basic boilerplate investigation steps."""
        steps = []
        
        steps.append({
            "id": "basic_credit_analysis",
            "title": "Basic Credit Profile Analysis",
            "description": f"Analyze credit profile with FICO {credit_data.get('fico_score_8', 'N/A')} and {banking_data.get('utilization_rate', 0):.1f}% utilization.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "15-20 min"
        })
        
        steps.append({
            "id": "payment_history_review",
            "title": "Payment History Review",
            "description": f"Review payment history with {banking_data.get('on_time_payments_12m', 0)} on-time payments.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "10-15 min"
        })
        
        steps.append({
            "id": "income_verification",
            "title": "Income Verification",
            "description": f"Verify income stability for ${income_data.get('verified_annual_income', 0):,.0f} annual income.",
            "category": "data_collection",
            "priority": "medium",
            "estimatedTime": "15-20 min"
        })
        
        return steps

    async def _personalize_strategy_with_llm(self, customer_data: Dict[str, Any], current_steps: List[Dict[str, Any]], strategy_focus: str, risk_profile: str) -> List[Dict[str, Any]]:
        """Use LLM to personalize the investigation strategy based on customer data and current steps."""
        try:
            # Check if Azure OpenAI is configured
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_KEY")
            
            if not endpoint or not api_key:
                logger.warning("⚠️ Azure OpenAI not configured, using rule-based personalization")
                return self._personalize_strategy_rule_based(customer_data, current_steps, strategy_focus, risk_profile)
            
            logger.info("🔧 Attempting LLM-based personalization...")
            # Extract customer profile for LLM
            customer_profile = self._extract_customer_profile_for_analysis(customer_data)
            
            # Prepare the prompt for LLM personalization
            prompt = f"""
You are a senior credit analyst tasked with personalizing an investigation strategy for a customer. 

CUSTOMER PROFILE:
{customer_profile}

CURRENT STRATEGY FOCUS: {strategy_focus.replace('_', ' ').title()}
RISK PROFILE: {risk_profile.replace('_', ' ').title()}

CURRENT INVESTIGATION STEPS:
{json.dumps(current_steps, indent=2)}

AVAILABLE STEP TEMPLATES:
{json.dumps(self._get_all_step_templates(), indent=2)}

TASK: Personalize the investigation strategy by:
1. Analyzing the customer profile and identifying specific areas that need deeper investigation
2. Selecting the most relevant steps from the current list
3. Adding new personalized steps based on the customer's specific situation
4. Prioritizing steps based on the customer's risk profile and strategy focus
5. Ensuring the strategy addresses the customer's unique characteristics

CRITICAL REQUIREMENTS:
- Return a JSON array of investigation steps
- Each step should have: id, title, description, category, priority, estimatedTime
- Categories: data_collection, analysis, scenario, visualization
- Priorities: high, medium, low
- Include 5-8 total steps
- Focus on customer-specific insights and risks
- Consider the customer's employment status, income level, credit history, and geographic location
- AVOID DUPLICATES: Do not include steps with similar titles or purposes
- Each step should be unique and address a different aspect of the investigation
- Use unique IDs for each step (e.g., "credit_profile_analysis", "payment_history_review", "geographic_risk_assessment")

Return only the JSON array of steps, no additional text.
"""
            
            # Check if this is an APIM endpoint and handle accordingly
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_KEY")
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
            
            # Log environment variables for debugging
            logger.info(f"🔍 Environment check:")
            logger.info(f"  - Endpoint: {endpoint}")
            logger.info(f"  - API Key: {'***' + api_key[-4:] if api_key else 'NOT SET'}")
            logger.info(f"  - Deployment: {deployment_name}")
            logger.info(f"  - API Version: {api_version}")
            logger.info(f"  - Is APIM: {'azure-api.net' in endpoint if endpoint else False}")
            
            if "azure-api.net" in endpoint:
                # Use direct HTTP request for APIM (same as working methods)
                import httpx
                
                base_endpoint = endpoint.rstrip('/')
                url = f"{base_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
                
                headers = {
                    "Content-Type": "application/json",
                    "Ocp-Apim-Subscription-Key": api_key,
                    "User-Agent": "BankingAgent/1.0"
                }
                
                data = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a senior credit analyst expert. Return only valid JSON arrays."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.3
                }
                
                logger.info(f"Making APIM request to: {url}")
                logger.info(f"Deployment: {deployment_name}")
                logger.info(f"API Version: {api_version}")
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=data, headers=headers)
                    logger.info(f"APIM Response status: {response.status_code}")
                    
                    if response.status_code != 200:
                        logger.error(f"APIM Error: {response.text}")
                        raise Exception(f"APIM returned status {response.status_code}: {response.text}")
                    
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()
            else:
                # Use Azure OpenAI SDK for standard endpoints
                client = get_azure_openai_client()
                
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {"role": "system", "content": "You are a senior credit analyst expert. Return only valid JSON arrays."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                content = response.choices[0].message.content.strip()
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                personalized_steps = json.loads(content)
                
                # Validate and clean the steps
                validated_steps = []
                for step in personalized_steps:
                    if isinstance(step, dict) and 'id' in step and 'title' in step:
                        validated_step = {
                            "id": step.get("id", f"personalized_{len(validated_steps)}"),
                            "title": step.get("title", "Personalized Step"),
                            "description": step.get("description", ""),
                            "category": step.get("category", "analysis"),
                            "priority": step.get("priority", "medium"),
                            "estimatedTime": step.get("estimatedTime", "15-20 min")
                        }
                        validated_steps.append(validated_step)
                
                # Remove duplicates based on step ID and title similarity
                seen_ids = set()
                seen_titles = set()
                unique_steps = []
                
                for step in validated_steps:
                    step_id = step["id"]
                    step_title = step["title"].lower().strip()
                    
                    # Check for exact ID match
                    if step_id in seen_ids:
                        continue
                    
                    # Check for similar title (fuzzy matching)
                    title_similar = False
                    for seen_title in seen_titles:
                        # Simple similarity check - if titles are very similar, consider them duplicates
                        if (step_title in seen_title or seen_title in step_title) and len(step_title) > 10:
                            title_similar = True
                            break
                    
                    if title_similar:
                        continue
                    
                    seen_ids.add(step_id)
                    seen_titles.add(step_title)
                    unique_steps.append(step)
                
                # Limit to 8 steps maximum
                if len(unique_steps) > 8:
                    # Prioritize high priority steps
                    high_priority = [step for step in unique_steps if step["priority"] == "high"]
                    medium_priority = [step for step in unique_steps if step["priority"] == "medium"]
                    low_priority = [step for step in unique_steps if step["priority"] == "low"]
                    
                    unique_steps = high_priority + medium_priority[:8-len(high_priority)] + low_priority[:max(0, 8-len(high_priority)-len(medium_priority))]
                
                logger.info(f"✅ LLM personalized strategy with {len(unique_steps)} unique steps (removed {len(validated_steps) - len(unique_steps)} duplicates)")
                return unique_steps
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse LLM response as JSON: {e}")
                logger.error(f"LLM Response: {content}")
                # Fallback to current steps
                return current_steps
                
        except Exception as e:
            logger.error(f"❌ Error personalizing strategy with LLM: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            if hasattr(e, 'response'):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            logger.info("🔄 Falling back to rule-based personalization...")
            # Fallback to rule-based personalization
            return self._personalize_strategy_rule_based(customer_data, current_steps, strategy_focus, risk_profile)

    def _get_all_step_templates(self) -> List[Dict[str, Any]]:
        """Get all available step templates for LLM reference."""
        templates = []
        
        # Risk mitigation templates
        templates.extend([
            {
                "id": "risk_assessment_deep_dive",
                "title": "Comprehensive Risk Assessment",
                "description": "Conduct detailed risk analysis focusing on specific risk factors and mitigation strategies.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "25-30 min"
            },
            {
                "id": "payment_pattern_analysis",
                "title": "Payment Pattern Risk Analysis",
                "description": "Analyze payment patterns to identify triggers for late payments and develop early warning indicators.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "20-25 min"
            },
            {
                "id": "debt_service_coverage",
                "title": "Debt Service Coverage Analysis",
                "description": "Calculate debt service coverage ratio to assess ability to handle additional debt obligations.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "15-20 min"
            }
        ])
        
        # Opportunity optimization templates
        templates.extend([
            {
                "id": "credit_limit_optimization",
                "title": "Optimal Credit Limit Analysis",
                "description": "Analyze optimal credit limit and determine maximum safe credit increase.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "20-25 min"
            },
            {
                "id": "revenue_opportunity_analysis",
                "title": "Revenue Opportunity Assessment",
                "description": "Calculate potential revenue increase from credit limit optimization.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "15-20 min"
            },
            {
                "id": "cross_sell_opportunities",
                "title": "Cross-Sell Opportunity Analysis",
                "description": "Identify cross-sell opportunities based on customer profile.",
                "category": "analysis",
                "priority": "medium",
                "estimatedTime": "15-20 min"
            }
        ])
        
        # Income verification templates
        templates.extend([
            {
                "id": "income_stability_analysis",
                "title": "Income Stability Assessment",
                "description": "Analyze income stability and review income trends and volatility over time.",
                "category": "data_collection",
                "priority": "high",
                "estimatedTime": "25-30 min"
            },
            {
                "id": "business_financial_health",
                "title": "Business Financial Health Check",
                "description": "Assess business financial health and stability for self-employed customers.",
                "category": "data_collection",
                "priority": "high",
                "estimatedTime": "30-35 min"
            },
            {
                "id": "cash_flow_analysis",
                "title": "Cash Flow Pattern Analysis",
                "description": "Analyze cash flow patterns and seasonal variations.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "20-25 min"
            }
        ])
        
        # Affordability analysis templates
        templates.extend([
            {
                "id": "affordability_assessment",
                "title": "Comprehensive Affordability Assessment",
                "description": "Conduct detailed affordability analysis including debt-to-income ratios and living expense analysis.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "25-30 min"
            },
            {
                "id": "expense_analysis",
                "title": "Living Expense Analysis",
                "description": "Analyze living expenses and discretionary spending patterns.",
                "category": "analysis",
                "priority": "high",
                "estimatedTime": "20-25 min"
            },
            {
                "id": "budget_impact_modeling",
                "title": "Budget Impact Modeling",
                "description": "Model impact of credit limit increase on monthly budget.",
                "category": "scenario",
                "priority": "high",
                "estimatedTime": "15-20 min"
            }
        ])
        
        return templates

    def _personalize_strategy_rule_based(self, customer_data: Dict[str, Any], current_steps: List[Dict[str, Any]], strategy_focus: str, risk_profile: str) -> List[Dict[str, Any]]:
        """Rule-based personalization when LLM is not available."""
        try:
            # Extract customer data
            banking_data = customer_data.get('internal_banking_data', {}).get('data', {})
            credit_data = customer_data.get('credit_bureau_data', {}).get('data', {})
            income_data = customer_data.get('income_ability_to_pay', {}).get('data', {})
            demo_data = customer_data.get('customer_demographics', {}).get('data', {})
            
            # Start with current steps
            personalized_steps = current_steps.copy()
            
            # Add strategy-specific steps based on focus
            if strategy_focus == "risk_mitigation":
                personalized_steps.extend(self._generate_risk_mitigation_steps(banking_data, credit_data, income_data, demo_data))
            elif strategy_focus == "opportunity_optimization":
                personalized_steps.extend(self._generate_opportunity_optimization_steps(banking_data, credit_data, income_data, demo_data))
            elif strategy_focus == "income_verification":
                personalized_steps.extend(self._generate_income_verification_steps(banking_data, credit_data, income_data, demo_data))
            elif strategy_focus == "affordability_analysis":
                personalized_steps.extend(self._generate_affordability_analysis_steps(banking_data, credit_data, income_data, demo_data))
            
            # Remove duplicates based on step ID and title similarity
            seen_ids = set()
            seen_titles = set()
            unique_steps = []
            
            for step in personalized_steps:
                step_id = step["id"]
                step_title = step["title"].lower().strip()
                
                # Check for exact ID match
                if step_id in seen_ids:
                    continue
                
                # Check for similar title (fuzzy matching)
                title_similar = False
                for seen_title in seen_titles:
                    # Simple similarity check - if titles are very similar, consider them duplicates
                    if (step_title in seen_title or seen_title in step_title) and len(step_title) > 10:
                        title_similar = True
                        break
                
                if title_similar:
                    continue
                
                seen_ids.add(step_id)
                seen_titles.add(step_title)
                unique_steps.append(step)
            
            # Limit to 8 steps maximum
            if len(unique_steps) > 8:
                # Prioritize high priority steps
                high_priority = [step for step in unique_steps if step["priority"] == "high"]
                medium_priority = [step for step in unique_steps if step["priority"] == "medium"]
                low_priority = [step for step in unique_steps if step["priority"] == "low"]
                
                unique_steps = high_priority + medium_priority[:8-len(high_priority)] + low_priority[:max(0, 8-len(high_priority)-len(medium_priority))]
            
            logger.info(f"✅ Rule-based personalization completed with {len(unique_steps)} steps")
            return unique_steps
            
        except Exception as e:
            logger.error(f"❌ Error in rule-based personalization: {e}")
            return current_steps

    # Strategy Management Methods
    def create_strategy(self, request: CreateStrategyRequest, created_by: str) -> InvestigationStrategy:
        """Create a new investigation strategy."""
        try:
            strategy_id = str(uuid.uuid4())
            now = datetime.now()
            
            strategy = InvestigationStrategy(
                strategy_id=strategy_id,
                name=request.name,
                description=request.description,
                strategy_focus=request.strategy_focus,
                risk_profile=request.risk_profile,
                steps=request.steps,
                is_template=request.is_template,
                tags=request.tags,
                created_by=created_by,
                created_at=now
            )
            
            self.strategies[strategy_id] = strategy
            self._save_strategies()
            
            logger.info(f"Created strategy {strategy_id}: {request.name}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error creating strategy: {e}")
            raise

    def get_strategy(self, strategy_id: str) -> Optional[InvestigationStrategy]:
        """Get a strategy by ID."""
        return self.strategies.get(strategy_id)

    def get_all_strategies(self) -> List[InvestigationStrategy]:
        """Get all strategies."""
        return list(self.strategies.values())

    def get_strategies_by_focus(self, strategy_focus: str) -> List[InvestigationStrategy]:
        """Get strategies by focus type."""
        return [s for s in self.strategies.values() if s.strategy_focus == strategy_focus]

    def get_strategies_by_risk_profile(self, risk_profile: str) -> List[InvestigationStrategy]:
        """Get strategies by risk profile."""
        return [s for s in self.strategies.values() if s.risk_profile == risk_profile]

    def get_template_strategies(self) -> List[InvestigationStrategy]:
        """Get template strategies."""
        return [s for s in self.strategies.values() if s.is_template]

    def update_strategy(self, strategy_id: str, request: UpdateStrategyRequest) -> Optional[InvestigationStrategy]:
        """Update a strategy."""
        try:
            if strategy_id not in self.strategies:
                return None
            
            strategy = self.strategies[strategy_id]
            now = datetime.now()
            
            # Update fields if provided
            if request.name is not None:
                strategy.name = request.name
            if request.description is not None:
                strategy.description = request.description
            if request.tags is not None:
                strategy.tags = request.tags
            if request.is_template is not None:
                strategy.is_template = request.is_template
            
            strategy.updated_at = now
            
            self._save_strategies()
            
            logger.info(f"Updated strategy {strategy_id}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error updating strategy: {e}")
            raise

    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a strategy."""
        try:
            if strategy_id not in self.strategies:
                return False
            
            del self.strategies[strategy_id]
            self._save_strategies()
            
            logger.info(f"Deleted strategy {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting strategy: {e}")
            return False

    def search_strategies(self, query: str) -> List[InvestigationStrategy]:
        """Search strategies by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for strategy in self.strategies.values():
            if (query_lower in strategy.name.lower() or
                (strategy.description and query_lower in strategy.description.lower()) or
                any(query_lower in tag.lower() for tag in strategy.tags)):
                results.append(strategy)
        
        return results

    def _determine_risk_profile(self, fico_score: int, utilization_rate: float, late_payments: int, income: float) -> str:
        """Determine customer risk profile based on key metrics."""
        risk_score = 0
        
        # FICO score assessment
        if fico_score >= 750:
            risk_score += 0
        elif fico_score >= 700:
            risk_score += 1
        elif fico_score >= 650:
            risk_score += 2
        else:
            risk_score += 3
        
        # Utilization rate assessment
        if utilization_rate <= 30:
            risk_score += 0
        elif utilization_rate <= 50:
            risk_score += 1
        elif utilization_rate <= 70:
            risk_score += 2
        else:
            risk_score += 3
        
        # Late payments assessment
        if late_payments == 0:
            risk_score += 0
        elif late_payments <= 2:
            risk_score += 1
        elif late_payments <= 4:
            risk_score += 2
        else:
            risk_score += 3
        
        # Income assessment (simplified)
        if income >= 100000:
            risk_score += 0
        elif income >= 50000:
            risk_score += 1
        else:
            risk_score += 2
        
        # Determine risk profile
        if risk_score <= 2:
            return "low_risk"
        elif risk_score <= 5:
            return "medium_risk"
        else:
            return "high_risk"

    def _determine_strategy_focus(self, risk_profile: str, employment_status: str, income: float) -> str:
        """Determine the focus area for investigation strategy."""
        if risk_profile == "high_risk":
            return "risk_mitigation"
        elif risk_profile == "low_risk":
            return "opportunity_optimization"
        elif employment_status in ["self_employed", "contractor"]:
            return "income_verification"
        elif income < 50000:
            return "affordability_analysis"
        else:
            return "standard_analysis"

    def _generate_risk_mitigation_steps(self, banking_data: Dict, credit_data: Dict, income_data: Dict, demo_data: Dict) -> List[Dict]:
        """Generate steps focused on risk mitigation for high-risk customers."""
        steps = []
        
        steps.append({
            "id": "risk_assessment_deep_dive",
            "title": "Comprehensive Risk Assessment",
            "description": f"Conduct detailed risk analysis for customer with FICO {credit_data.get('fico_score_8', 'N/A')} and {banking_data.get('late_payments_12m', 0)} late payments. Focus on identifying specific risk factors and mitigation strategies.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "25-30 min"
        })
        
        steps.append({
            "id": "payment_pattern_analysis",
            "title": "Payment Pattern Risk Analysis",
            "description": f"Analyze payment patterns with {banking_data.get('late_payments_12m', 0)} late payments. Identify triggers for late payments and develop early warning indicators.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "20-25 min"
        })
        
        steps.append({
            "id": "debt_service_coverage",
            "title": "Debt Service Coverage Analysis",
            "description": f"Calculate debt service coverage ratio for income ${income_data.get('verified_annual_income', 0):,.0f}. Assess ability to handle additional debt obligations.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "15-20 min"
        })
        
        return steps

    def _generate_opportunity_optimization_steps(self, banking_data: Dict, credit_data: Dict, income_data: Dict, demo_data: Dict) -> List[Dict]:
        """Generate steps focused on opportunity optimization for low-risk customers."""
        steps = []
        
        steps.append({
            "id": "credit_limit_optimization",
            "title": "Optimal Credit Limit Analysis",
            "description": f"Analyze optimal credit limit for customer with FICO {credit_data.get('fico_score_8', 'N/A')} and {banking_data.get('utilization_rate', 0):.1f}% utilization. Determine maximum safe credit increase.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "20-25 min"
        })
        
        steps.append({
            "id": "revenue_opportunity_analysis",
            "title": "Revenue Opportunity Assessment",
            "description": f"Calculate potential revenue increase from credit limit optimization. Analyze customer spending patterns and credit utilization trends.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "15-20 min"
        })
        
        steps.append({
            "id": "cross_sell_opportunities",
            "title": "Cross-Sell Opportunity Analysis",
            "description": f"Identify cross-sell opportunities based on customer profile. Analyze potential for additional products and services.",
            "category": "analysis",
            "priority": "medium",
            "estimatedTime": "15-20 min"
        })
        
        return steps

    def _generate_income_verification_steps(self, banking_data: Dict, credit_data: Dict, income_data: Dict, demo_data: Dict) -> List[Dict]:
        """Generate steps focused on income verification for self-employed customers."""
        steps = []
        
        steps.append({
            "id": "income_stability_analysis",
            "title": "Income Stability Assessment",
            "description": f"Analyze income stability for {demo_data.get('employment_status', 'N/A')} customer. Review income trends and volatility over time.",
            "category": "data_collection",
            "priority": "high",
            "estimatedTime": "25-30 min"
        })
        
        steps.append({
            "id": "business_financial_health",
            "title": "Business Financial Health Check",
            "description": f"Assess business financial health and stability. Review business credit reports and financial statements if available.",
            "category": "data_collection",
            "priority": "high",
            "estimatedTime": "30-35 min"
        })
        
        steps.append({
            "id": "cash_flow_analysis",
            "title": "Cash Flow Pattern Analysis",
            "description": f"Analyze cash flow patterns and seasonal variations. Assess ability to maintain consistent income.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "20-25 min"
        })
        
        return steps

    def _generate_affordability_analysis_steps(self, banking_data: Dict, credit_data: Dict, income_data: Dict, demo_data: Dict) -> List[Dict]:
        """Generate steps focused on affordability analysis for lower-income customers."""
        steps = []
        
        steps.append({
            "id": "affordability_assessment",
            "title": "Comprehensive Affordability Assessment",
            "description": f"Conduct detailed affordability analysis for income ${income_data.get('verified_annual_income', 0):,.0f}. Calculate debt-to-income ratios and living expense analysis.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "25-30 min"
        })
        
        steps.append({
            "id": "expense_analysis",
            "title": "Living Expense Analysis",
            "description": f"Analyze living expenses and discretionary spending patterns. Assess impact of credit limit increase on overall financial health.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "20-25 min"
        })
        
        steps.append({
            "id": "budget_impact_modeling",
            "title": "Budget Impact Modeling",
            "description": f"Model impact of credit limit increase on monthly budget. Assess sustainability of additional credit obligations.",
            "category": "scenario",
            "priority": "high",
            "estimatedTime": "15-20 min"
        })
        
        return steps

    def _generate_standard_analysis_steps(self, banking_data: Dict, credit_data: Dict, income_data: Dict, demo_data: Dict) -> List[Dict]:
        """Generate standard analysis steps for typical customers."""
        steps = []
        
        steps.append({
            "id": "credit_profile_analysis",
            "title": "Comprehensive Credit Profile Analysis",
            "description": f"Analyze credit profile with FICO {credit_data.get('fico_score_8', 'N/A')} and {banking_data.get('utilization_rate', 0):.1f}% utilization. Assess overall creditworthiness.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "20-25 min"
        })
        
        steps.append({
            "id": "payment_history_review",
            "title": "Payment History Review",
            "description": f"Review payment history with {banking_data.get('on_time_payments_12m', 0)} on-time payments. Analyze payment patterns and reliability.",
            "category": "analysis",
            "priority": "high",
            "estimatedTime": "15-20 min"
        })
        
        steps.append({
            "id": "income_verification",
            "title": "Income Verification and Stability",
            "description": f"Verify income stability for ${income_data.get('verified_annual_income', 0):,.0f} annual income. Assess employment stability and income trends.",
            "category": "data_collection",
            "priority": "medium",
            "estimatedTime": "15-20 min"
        })
        
        return steps

    def _generate_common_steps(self, banking_data: Dict, credit_data: Dict, income_data: Dict, demo_data: Dict) -> List[Dict]:
        """Generate common steps that apply to all strategies."""
        steps = []
        
        steps.append({
            "id": "similar_customers",
            "title": "Similar Customer Profile Analysis",
            "description": f"Analyze customers with similar profiles: FICO {credit_data.get('fico_score_8', 'N/A')}, income ${income_data.get('verified_annual_income', 0):,.0f}, {demo_data.get('employment_status', 'N/A')} employment.",
            "category": "data_collection",
            "priority": "medium",
            "estimatedTime": "15-20 min"
        })
        
        steps.append({
            "id": "geographic_analysis",
            "title": "Geographic Risk Assessment",
            "description": f"Analyze credit performance in {demo_data.get('city', 'N/A')}, {demo_data.get('state', 'N/A')}. Check local economic indicators and market conditions.",
            "category": "data_collection",
            "priority": "medium",
            "estimatedTime": "10-15 min"
        })
        
        steps.append({
            "id": "scenario_modeling",
            "title": "Credit Limit Increase Scenarios",
            "description": "Model different credit limit increase scenarios and calculate probability of default, expected utilization, and credit score impact.",
            "category": "scenario",
            "priority": "high",
            "estimatedTime": "25-30 min"
        })
        
        steps.append({
            "id": "risk_visualization",
            "title": "Risk Assessment Visualization",
            "description": "Create risk assessment heatmap showing probability of default vs. credit limit increase amounts with confidence intervals.",
            "category": "visualization",
            "priority": "medium",
            "estimatedTime": "20-25 min"
        })
        
        return steps

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

            client = get_azure_openai_client()
            
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
