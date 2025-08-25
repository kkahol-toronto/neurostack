import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx
from models import ChatMessage, ChatSession, ScenarioAnalysis, ChatMessageRequest
from neurostack_integration import NeuroStackBankingIntegration

class ChatService:
    def __init__(self):
        self.neurostack = None  # Will be initialized when needed
        self.sessions: Dict[str, ChatSession] = {}
        self.messages: Dict[str, List[ChatMessage]] = {}
        
    async def _get_neurostack(self):
        """Get or initialize the neurostack integration"""
        if self.neurostack is None:
            self.neurostack = NeuroStackBankingIntegration(tenant_id="banking_agent")
            await self.neurostack.initialize()
        return self.neurostack

    async def process_message(self, request: ChatMessageRequest) -> Dict[str, Any]:
        """Process a chat message and generate a response"""
        try:
            # Create or get session
            session = await self._get_or_create_session(request)
            
            # Create user message
            user_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=request.session_id,
                customer_id=request.customer_id,
                customer_name=request.customer_name,
                message_type="user",
                content=request.content,
                timestamp=datetime.now()
            )
            
            # Store user message
            if request.session_id not in self.messages:
                self.messages[request.session_id] = []
            self.messages[request.session_id].append(user_message)
            
            # Check for special commands
            if request.content.strip().lower().startswith('/scenario'):
                return await self._handle_scenario_command(request, session)
            
            # Generate AI response
            ai_response = await self._generate_ai_response(request, session)
            
            # Create assistant message
            assistant_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=request.session_id,
                customer_id=request.customer_id,
                customer_name=request.customer_name,
                message_type="assistant",
                content=ai_response["content"],
                timestamp=datetime.now(),
                metadata=ai_response.get("metadata")
            )
            
            # Store assistant message
            self.messages[request.session_id].append(assistant_message)
            
            # Update session
            session.message_count = len(self.messages[request.session_id])
            session.updated_at = datetime.now()
            
            return {
                "success": True,
                "message": assistant_message.dict(),
                "session": session.dict()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process message: {str(e)}"
            }
    
    async def _get_or_create_session(self, request: ChatMessageRequest) -> ChatSession:
        """Get existing session or create a new one"""
        if request.session_id in self.sessions:
            return self.sessions[request.session_id]
        
        session = ChatSession(
            session_id=request.session_id,
            customer_id=request.customer_id,
            customer_name=request.customer_name,
            execution_id=request.execution_id,
            investigation_results=request.investigation_results,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.sessions[request.session_id] = session
        return session
    
    async def _handle_scenario_command(self, request: ChatMessageRequest, session: ChatSession) -> Dict[str, Any]:
        """Handle the /scenario command to generate credit limit variations"""
        try:
            # Extract base increase amount from the command
            # Format: /scenario 8000 or /scenario base=8000
            content = request.content.strip()
            base_increase = 8000.0  # Default value
            
            if '=' in content:
                try:
                    base_increase = float(content.split('=')[1].strip())
                except:
                    pass
            else:
                # Try to extract number from the command
                import re
                numbers = re.findall(r'\d+', content)
                if numbers:
                    base_increase = float(numbers[0])
            
            # Generate scenario analysis
            scenario_analysis = await self._generate_scenario_analysis(
                request,  # Pass the full request object
                request.customer_id, 
                request.customer_name, 
                base_increase,
                session
            )
            
            # Create scenario message
            scenario_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=request.session_id,
                customer_id=request.customer_id,
                customer_name=request.customer_name,
                message_type="assistant",
                content=scenario_analysis["content"],
                timestamp=datetime.now(),
                metadata=scenario_analysis["metadata"]
            )
            
            # Store scenario message
            if request.session_id not in self.messages:
                self.messages[request.session_id] = []
            self.messages[request.session_id].append(scenario_message)
            
            # Update session
            session.message_count = len(self.messages[request.session_id])
            session.updated_at = datetime.now()
            
            return {
                "success": True,
                "message": scenario_message.dict(),
                "session": session.dict()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate scenario analysis: {str(e)}"
            }
    
    async def _generate_scenario_analysis(self, request: ChatMessageRequest, customer_id: int, customer_name: str, base_increase: float, session: ChatSession) -> Dict[str, Any]:
        """Generate scenario analysis with credit limit variations"""
        
        # Generate variations: 40%, 60%, 80%, 100%, 120% of base increase
        variations = [0.4, 0.6, 0.8, 1.0, 1.2]
        scenarios = []
        
        # Mock current credit limit (in real implementation, get from customer data)
        current_limit = 32000.0
        
        for variation in variations:
            increase_amount = base_increase * variation
            new_limit = current_limit + increase_amount
            
            # Calculate projected utilization (mock calculation)
            # In real implementation, use spending trends and patterns
            current_utilization = 25.0  # Mock current utilization
            projected_utilization = max(15.0, current_utilization * (current_limit / new_limit))
            
            # Risk assessment
            risk_score = self._calculate_risk_score(increase_amount, new_limit, projected_utilization)
            risk_level = "Low" if risk_score < 30 else "Medium" if risk_score < 60 else "High"
            
            scenarios.append({
                "variation_percentage": int(variation * 100),
                "increase_amount": increase_amount,
                "new_credit_limit": new_limit,
                "projected_utilization": projected_utilization,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "recommendation": self._get_recommendation(risk_score)
            })
        
        # Generate spending trends analysis
        spending_trends = {
            "monthly_average": 8500.0,
            "trend_direction": "increasing",
            "seasonal_patterns": ["Q4 peak", "Q1 decline"],
            "projected_spending": 9200.0,
            "confidence_level": 85
        }
        
        # Create visualization data for the scenarios
        viz_data = {
            "type": "scenario_analysis",
            "title": "Credit Limit Increase Scenarios",
            "subtitle": f"Analysis for {customer_name} - Base Increase: ${base_increase:,.0f}",
            "scenarios": scenarios,
            "spending_trends": spending_trends,
            "current_limit": current_limit,
            "base_increase": base_increase
        }
        
        # Get comprehensive context for scenario analysis
        context = await self._build_comprehensive_context(
            request,  # Use the request parameter
            session
        )
        
        # Generate intelligent scenario analysis prompt
        prompt = f"""
        You are an AI banking analyst assistant performing a comprehensive credit limit increase scenario analysis.

        CUSTOMER PROFILE:
        {self._format_customer_profile(context.get("customer_profile", {}))}

        INVESTIGATION RESULTS:
        {context.get("investigation_results", "No investigation results available.")}

        SCENARIO ANALYSIS REQUEST:
        - Customer: {customer_name}
        - Current Credit Limit: ${current_limit:,.0f}
        - Base Increase Requested: ${base_increase:,.0f}

        GENERATED SCENARIOS (40% to 120% of requested increase):
        {json.dumps(scenarios, indent=2)}

        SPENDING PATTERN ANALYSIS:
        {json.dumps(spending_trends, indent=2)}

        RECENT CONVERSATION CONTEXT:
        {self._format_chat_history(context.get("chat_history", []))}

        INSTRUCTIONS:
        Provide a comprehensive, data-driven analysis that:
        1. Evaluates each scenario based on the customer's profile and investigation results
        2. Considers the customer's spending patterns and utilization trends
        3. Assesses risk factors using the available investigation data
        4. Provides specific recommendations with rationale
        5. References relevant data points from the investigation results
        6. Suggests monitoring strategies for the recommended approach
        7. Considers the conversation context to provide continuity

        Format your response in a clear, professional manner suitable for banking decision-making.
        """
        
        try:
            neurostack = await self._get_neurostack()
            ai_response = await neurostack.generate_response(prompt)
        except Exception as e:
            print(f"Reasoning agent failed for scenario: {e}")
            # Fallback to direct APIM call
            try:
                ai_response = await self._call_apim_directly(prompt)
            except Exception as apim_error:
                print(f"Direct APIM call also failed: {apim_error}")
                # Generate intelligent fallback response based on the scenarios
                ai_response = self._generate_intelligent_fallback_response(scenarios, spending_trends, customer_name, base_increase)
        
        return {
            "content": ai_response,
            "metadata": {
                "scenario_analysis": viz_data,
                "command_type": "scenario",
                "base_increase": base_increase
            }
        }
    
    def _calculate_risk_score(self, increase_amount: float, new_limit: float, projected_utilization: float) -> float:
        """Calculate risk score for a scenario"""
        # Mock risk calculation - in real implementation, use ML models
        utilization_factor = min(100, projected_utilization * 2)
        increase_factor = min(100, (increase_amount / 10000) * 50)
        limit_factor = min(100, (new_limit / 50000) * 30)
        
        risk_score = (utilization_factor + increase_factor + limit_factor) / 3
        return round(risk_score, 1)
    
    def _get_recommendation(self, risk_score: float) -> str:
        """Get recommendation based on risk score"""
        if risk_score < 30:
            return "Strongly Recommend"
        elif risk_score < 60:
            return "Recommend with Monitoring"
        else:
            return "Recommend Against"
    
    def _generate_fallback_scenario_response(self, scenarios: List[Dict], spending_trends: Dict) -> str:
        """Generate fallback response if LLM fails"""
        response = "## Credit Limit Increase Scenario Analysis\n\n"
        response += "I've analyzed multiple credit limit increase scenarios based on your request:\n\n"
        
        for scenario in scenarios:
            response += f"**{scenario['variation_percentage']}% Scenario:**\n"
            response += f"- Increase Amount: ${scenario['increase_amount']:,.0f}\n"
            response += f"- New Credit Limit: ${scenario['new_credit_limit']:,.0f}\n"
            response += f"- Projected Utilization: {scenario['projected_utilization']:.1f}%\n"
            response += f"- Risk Level: {scenario['risk_level']} (Score: {scenario['risk_score']})\n"
            response += f"- Recommendation: {scenario['recommendation']}\n\n"
        
        response += "**Spending Pattern Analysis:**\n"
        response += f"- Monthly Average: ${spending_trends['monthly_average']:,.0f}\n"
        response += f"- Trend: {spending_trends['trend_direction'].title()}\n"
        response += f"- Projected Spending: ${spending_trends['projected_spending']:,.0f}\n\n"
        
        response += "**Key Recommendations:**\n"
        response += "1. Consider the 80-100% scenarios for optimal balance of risk and customer satisfaction\n"
        response += "2. Monitor utilization patterns closely after implementation\n"
        response += "3. Review spending trends quarterly to adjust limits if needed\n"
        
        return response
    
    def _generate_intelligent_fallback_response(self, scenarios: List[Dict], spending_trends: Dict, customer_name: str, base_increase: float) -> str:
        """Generate intelligent fallback response for scenario analysis when APIM fails"""
        
        response = f"## Credit Limit Increase Analysis for {customer_name}\n\n"
        response += f"Based on the scenario analysis for a **${base_increase:,.0f}** base increase request, here's my comprehensive assessment:\n\n"
        
        # Find the 100% scenario (the requested amount)
        requested_scenario = next((s for s in scenarios if s['variation_percentage'] == 100), None)
        
        if requested_scenario:
            response += f"**Requested Increase Analysis (100%):**\n"
            response += f"- **Increase Amount:** ${requested_scenario['increase_amount']:,.0f}\n"
            response += f"- **New Credit Limit:** ${requested_scenario['new_credit_limit']:,.0f}\n"
            response += f"- **Projected Utilization:** {requested_scenario['projected_utilization']:.1f}%\n"
            response += f"- **Risk Level:** {requested_scenario['risk_level']} (Score: {requested_scenario['risk_score']})\n"
            response += f"- **Recommendation:** {requested_scenario['recommendation']}\n\n"
        
        # Analyze the difference between 80% and 100% scenarios
        scenario_80 = next((s for s in scenarios if s['variation_percentage'] == 80), None)
        scenario_100 = next((s for s in scenarios if s['variation_percentage'] == 100), None)
        
        if scenario_80 and scenario_100:
            difference = scenario_100['increase_amount'] - scenario_80['increase_amount']
            risk_difference = scenario_100['risk_score'] - scenario_80['risk_score']
            
            response += f"**Risk Analysis for Additional ${difference:,.0f}:**\n"
            response += f"- The difference between 80% and 100% scenarios is **${difference:,.0f}**\n"
            response += f"- Risk score increases by **{risk_difference:.1f} points**\n"
            response += f"- This represents a **{risk_difference/scenario_80['risk_score']*100:.1f}%** increase in risk\n\n"
        
        # Spending pattern analysis
        response += f"**Spending Pattern Context:**\n"
        response += f"- Monthly Average: ${spending_trends['monthly_average']:,.0f}\n"
        response += f"- Trend Direction: {spending_trends['trend_direction'].title()}\n"
        response += f"- Projected Spending: ${spending_trends['projected_spending']:,.0f}\n"
        response += f"- Confidence Level: {spending_trends['confidence_level']}%\n\n"
        
        # Recommendations
        response += "**Strategic Recommendations:**\n"
        
        if requested_scenario and requested_scenario['risk_score'] < 50:
            response += "✅ **Recommend proceeding with the full requested amount** - Risk profile remains acceptable\n"
        elif requested_scenario and requested_scenario['risk_score'] < 70:
            response += "⚠️ **Consider a compromise approach** - Moderate risk increase, suggest 90% of requested amount\n"
        else:
            response += "❌ **Recommend against full amount** - Risk profile becomes elevated, suggest 80% of requested amount\n"
        
        response += "\n**Monitoring Strategy:**\n"
        response += "1. **Monthly utilization monitoring** for the first 3 months\n"
        response += "2. **Quarterly spending pattern review** to adjust if needed\n"
        response += "3. **Credit score monitoring** to ensure no negative impact\n"
        response += "4. **Payment behavior tracking** to maintain risk profile\n\n"
        
        response += "**Next Steps:**\n"
        response += "- If proceeding with full amount: Implement with enhanced monitoring\n"
        response += "- If compromise needed: Present 90% option with rationale\n"
        response += "- Document decision factors for future reference\n"
        
        return response
    
    async def _generate_ai_response(self, request: ChatMessageRequest, session: ChatSession) -> Dict[str, Any]:
        """Generate AI response using comprehensive context"""
        
        try:
            # Get comprehensive context
            context = await self._build_comprehensive_context(request, session)
            
            # Create intelligent prompt with full context
            prompt = self._create_intelligent_prompt(request, context)
            
            print(f"Prompt length: {len(prompt)} characters")
            print(f"Context includes: customer_profile={bool(context.get('customer_profile'))}, investigation_results={bool(context.get('investigation_results'))}, chat_history={len(context.get('chat_history', []))}")
            
            # Use reasoning agent as primary method
            neurostack = await self._get_neurostack()
            ai_response = await neurostack.generate_response(prompt)
            
            return {
                "content": ai_response,
                "metadata": {
                    "context_used": {
                        "customer_profile": True,
                        "investigation_results": True,
                        "chat_history": len(context.get("chat_history", [])) > 0,
                        "total_context_length": len(prompt)
                    },
                    "customer_id": request.customer_id
                }
            }
            
        except Exception as e:
            print(f"Reasoning agent failed: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            # Only use direct APIM as last resort
            try:
                fallback_prompt = f"""
                You are an AI banking analyst assistant. A banking analyst is asking questions about investigation results for customer {request.customer_name} (ID: {request.customer_id}).

                ANALYST'S QUESTION: {request.content}

                Please provide a helpful, professional response that would assist a banking analyst in making credit decisions. If you need more context, ask the analyst to provide additional information.
                """
                ai_response = await self._call_apim_directly(fallback_prompt)
            except Exception as fallback_error:
                ai_response = f"I apologize, but I'm having trouble accessing the AI analysis service right now. Please try again in a moment, or contact technical support if the issue persists. Error: {str(fallback_error)}"
            
            return {
                "content": ai_response,
                "metadata": {
                    "context_used": {"fallback_mode": True},
                    "customer_id": request.customer_id
                }
            }
    
    async def _build_comprehensive_context(self, request: ChatMessageRequest, session: ChatSession) -> Dict[str, Any]:
        """Build comprehensive context including customer profile, investigation results, and chat history"""
        
        context = {
            "customer_profile": {},
            "investigation_results": {},
            "chat_history": [],
            "session_info": {}
        }
        
        try:
            # Get customer profile from NeuroStack memory (which now contains actual database data)
            neurostack = await self._get_neurostack()
            customer_profile = neurostack.get_customer_by_id_direct(request.customer_id)
            
            if customer_profile:
                context["customer_profile"] = customer_profile
            else:
                # Fallback to basic profile if not found in memory
                context["customer_profile"] = {
                    "customer_id": request.customer_id,
                    "name": request.customer_name,
                    "credit_limit": 32000.0,
                    "fico_score": 720,
                    "credit_utilization": 25.0,
                    "payment_history": "Excellent",
                    "income": 85000.0,
                    "dti_ratio": 28.0
                }
            
            # Build investigation context
            if session.investigation_results:
                context["investigation_results"] = self._build_investigation_context(session.investigation_results)
            
            # Get recent chat history (last 10 exchanges)
            if request.session_id in self.messages:
                recent_messages = self.messages[request.session_id][-20:]  # Last 20 messages (10 exchanges)
                context["chat_history"] = [
                    {
                        "role": msg.message_type,
                        "content": msg.content,
                        "timestamp": msg.timestamp
                    }
                    for msg in recent_messages
                ]
            
            # Add session information
            context["session_info"] = {
                "session_id": session.session_id,
                "customer_id": session.customer_id,
                "customer_name": session.customer_name,
                "message_count": session.message_count,
                "execution_id": session.execution_id
            }
            
        except Exception as e:
            print(f"Error building comprehensive context: {e}")
            # Fallback to basic context
            context["investigation_results"] = self._build_investigation_context(session.investigation_results)
            # Ensure we have at least basic customer profile
            if not context.get("customer_profile"):
                context["customer_profile"] = {
                    "customer_id": request.customer_id,
                    "name": request.customer_name,
                    "credit_limit": 32000.0,
                    "fico_score": 720,
                    "credit_utilization": 25.0,
                    "payment_history": "Excellent",
                    "income": 85000.0,
                    "dti_ratio": 28.0
                }
        
        return context
    
    def _extract_customer_profile_from_investigation(self, investigation_results: Optional[Dict[str, Any]], customer_id: int) -> Dict[str, Any]:
        """Extract customer profile data from investigation results (actual database data)"""
        
        # Import the mock databases to get actual customer data
        from main import MOCK_DATABASES
        
        customer_profile = {
            "customer_id": customer_id,
            "name": f"Customer {customer_id}",
            "credit_limit": 32000.0,  # Default fallback
            "fico_score": 720,  # Default fallback
            "credit_utilization": 25.0,  # Default fallback
            "payment_history": "Excellent",  # Default fallback
            "income": 85000.0,  # Default fallback
            "dti_ratio": 28.0  # Default fallback
        }
        
        try:
            # Get customer demographics
            demographics = next((c for c in MOCK_DATABASES["customer_demographics"] if c["customer_id"] == customer_id), None)
            if demographics:
                customer_profile.update({
                    "first_name": demographics.get("first_name"),
                    "last_name": demographics.get("last_name"),
                    "name": f"{demographics.get('first_name', '')} {demographics.get('last_name', '')}".strip(),
                    "annual_income": demographics.get("annual_income"),  # Keep for reference
                    "employment_status": demographics.get("employment_status"),
                    "customer_segment": demographics.get("customer_segment"),
                    "state": demographics.get("state"),
                    "city": demographics.get("city"),
                    "customer_since": demographics.get("customer_since"),
                    "employer_name": demographics.get("employer_name"),
                    "job_title": demographics.get("job_title"),
                    "household_size": demographics.get("household_size")
                })
            
            # Get internal banking data (credit limit, balance, utilization)
            banking_data = next((c for c in MOCK_DATABASES["internal_banking_data"] if c["customer_id"] == customer_id), None)
            if banking_data:
                customer_profile.update({
                    "credit_limit": banking_data.get("current_credit_limit"),
                    "current_balance": banking_data.get("current_balance"),
                    "credit_utilization": banking_data.get("utilization_rate"),
                    "on_time_payments_12m": banking_data.get("on_time_payments_12m"),
                    "late_payments_12m": banking_data.get("late_payments_12m"),
                    "tenure_months": banking_data.get("tenure_months"),
                    "payment_history": "Excellent" if banking_data.get("late_payments_12m", 0) == 0 else "Good" if banking_data.get("late_payments_12m", 0) <= 1 else "Fair"
                })
            
            # Get credit bureau data (FICO scores)
            credit_bureau = next((c for c in MOCK_DATABASES["credit_bureau_data"] if c["customer_id"] == customer_id), None)
            if credit_bureau:
                customer_profile.update({
                    "fico_score": credit_bureau.get("fico_score_8"),
                    "fico_score_9": credit_bureau.get("fico_score_9"),
                    "total_accounts_bureau": credit_bureau.get("total_accounts_bureau"),
                    "delinquencies_30_plus_12m": credit_bureau.get("delinquencies_30_plus_12m")
                })
            
            # Get income and ability to pay data (PRIORITY for income)
            income_data = next((c for c in MOCK_DATABASES["income_ability_to_pay"] if c["customer_id"] == customer_id), None)
            if income_data:
                customer_profile.update({
                    "verified_annual_income": income_data.get("verified_annual_income"),
                    "income": income_data.get("verified_annual_income"),  # Use verified income as primary
                    "dti_ratio": income_data.get("debt_to_income_ratio", 0) * 100,  # Convert to percentage
                    "total_monthly_debt_payments": income_data.get("total_monthly_debt_payments"),
                    "income_stability_score": income_data.get("income_stability_score")
                })
            
            # Get fraud/KYC data
            fraud_data = next((c for c in MOCK_DATABASES["fraud_kyc_compliance"] if c["customer_id"] == customer_id), None)
            if fraud_data:
                customer_profile.update({
                    "fraud_risk_score": fraud_data.get("overall_fraud_risk_score"),
                    "fraud_risk_level": fraud_data.get("risk_level"),
                    "kyc_score": fraud_data.get("kyc_score"),
                    "identity_verification_status": fraud_data.get("identity_verification_status")
                })
            
            # Get open banking data if available
            open_banking = next((c for c in MOCK_DATABASES["open_banking_data"] if c["customer_id"] == customer_id), None)
            if open_banking:
                customer_profile.update({
                    "open_banking_consent": open_banking.get("open_banking_consent"),
                    "avg_monthly_income": open_banking.get("avg_monthly_income"),
                    "cash_flow_stability_score": open_banking.get("cash_flow_stability_score"),
                    "expense_obligations_rent": open_banking.get("expense_obligations_rent")
                })
            
            # Get economic indicators for the customer's state
            if demographics and demographics.get("state"):
                state_code = demographics["state"]
                economic_data = next((e for e in MOCK_DATABASES["state_economic_indicators"] if e["state_code"] == state_code), None)
                if economic_data:
                    customer_profile.update({
                        "state_unemployment_rate": economic_data.get("unemployment_rate"),
                        "state_macro_risk_score": economic_data.get("macro_risk_score"),
                        "state_risk_level": economic_data.get("risk_level"),
                        "state_gdp_growth_rate": economic_data.get("gdp_growth_rate")
                    })
            
        except Exception as e:
            print(f"Error extracting customer profile from investigation: {e}")
            # Keep the default values if extraction fails
        
        return customer_profile
    
    def _create_intelligent_prompt(self, request: ChatMessageRequest, context: Dict[str, Any]) -> str:
        """Create an intelligent prompt with comprehensive context"""
        
        prompt = f"""You are an AI banking analyst assistant with access to comprehensive customer data and investigation results. You are helping a banking analyst (the person asking questions) make informed decisions about credit limit requests for a specific customer.

CUSTOMER PROFILE:
{self._format_customer_profile(context.get("customer_profile", {}))}

INVESTIGATION RESULTS:
{context.get("investigation_results", "No investigation results available.")}

SESSION INFORMATION:
- Customer Being Analyzed: {context.get("session_info", {}).get("customer_name", "Unknown")} (ID: {context.get("session_info", {}).get("customer_id", "Unknown")})
- Session ID: {context.get("session_info", {}).get("session_id", "Unknown")}
- Total Messages: {context.get("session_info", {}).get("message_count", 0)}

RECENT CONVERSATION HISTORY (Last 10 exchanges):
{self._format_chat_history(context.get("chat_history", []))}

ANALYST'S CURRENT QUESTION: {request.content}

INSTRUCTIONS:
1. Use ALL available context (customer profile, investigation results, chat history) to provide informed responses
2. Reference specific data points from the investigation results when relevant
3. Consider the conversation history to maintain context and avoid repetition
4. Provide actionable insights based on the comprehensive data available
5. If the question is about scenarios or "what-if" analysis, suggest using the /scenario command
6. Maintain a professional banking tone
7. If you need more information, ask specific questions
8. Remember: You are helping an analyst who is asking questions about a customer, not talking directly to the customer

Please provide a comprehensive, data-driven response:"""
        
        return prompt
    
    def _format_customer_profile(self, profile: Dict[str, Any]) -> str:
        """Format customer profile for context"""
        if not profile:
            return "No customer profile available."
        
        formatted = "Customer Profile:\n"
        try:
            # Basic customer information
            if "customer_id" in profile:
                formatted += f"- Customer ID: {profile['customer_id']}\n"
            
            # Handle name fields
            if "name" in profile:
                formatted += f"- Name: {profile['name']}\n"
            
            # Credit information
            if "credit_limit" in profile:
                formatted += f"- Current Credit Limit: ${profile['credit_limit']:,.0f}\n"
            
            if "current_balance" in profile:
                formatted += f"- Current Balance: ${profile['current_balance']:,.2f}\n"
            
            if "credit_utilization" in profile:
                formatted += f"- Credit Utilization: {profile['credit_utilization']:.1f}%\n"
            
            # FICO scores
            if "fico_score" in profile:
                formatted += f"- FICO Score 8: {profile['fico_score']}\n"
            
            if "fico_score_9" in profile:
                formatted += f"- FICO Score 9: {profile['fico_score_9']}\n"
            
            # Payment history
            if "payment_history" in profile:
                formatted += f"- Payment History: {profile['payment_history']}\n"
            
            if "on_time_payments_12m" in profile:
                formatted += f"- On-time Payments (12m): {profile['on_time_payments_12m']}\n"
            
            if "late_payments_12m" in profile:
                formatted += f"- Late Payments (12m): {profile['late_payments_12m']}\n"
            
            # Income information
            if "income" in profile:
                formatted += f"- Annual Income: ${profile['income']:,.0f}\n"
            
            if "verified_annual_income" in profile:
                formatted += f"- Verified Annual Income: ${profile['verified_annual_income']:,.0f}\n"
            
            # Debt-to-income ratio
            if "dti_ratio" in profile:
                formatted += f"- Debt-to-Income Ratio: {profile['dti_ratio']:.1f}%\n"
            
            # Employment and demographics
            if "employment_status" in profile:
                formatted += f"- Employment Status: {profile['employment_status']}\n"
            
            if "customer_segment" in profile:
                formatted += f"- Customer Segment: {profile['customer_segment']}\n"
            
            if "state" in profile:
                formatted += f"- State: {profile['state']}\n"
            
            if "city" in profile:
                formatted += f"- City: {profile['city']}\n"
            
            if "tenure_months" in profile:
                formatted += f"- Account Tenure: {profile['tenure_months']} months\n"
            
            # Fraud and KYC information
            if "fraud_risk_score" in profile:
                formatted += f"- Fraud Risk Score: {profile['fraud_risk_score']:.2f}\n"
            
            if "fraud_risk_level" in profile:
                formatted += f"- Fraud Risk Level: {profile['fraud_risk_level']}\n"
            
            if "kyc_score" in profile:
                formatted += f"- KYC Score: {profile['kyc_score']:.1f}\n"
            
            if "identity_verification_status" in profile:
                formatted += f"- Identity Verification: {profile['identity_verification_status']}\n"
            
            # Income stability
            if "income_stability_score" in profile:
                formatted += f"- Income Stability Score: {profile['income_stability_score']:.1f}\n"
            
            # Economic indicators
            if "state_unemployment_rate" in profile:
                formatted += f"- State Unemployment Rate: {profile['state_unemployment_rate']:.1f}%\n"
            
            if "state_macro_risk_score" in profile:
                formatted += f"- State Macro Risk Score: {profile['state_macro_risk_score']:.1f}\n"
            
            if "state_risk_level" in profile:
                formatted += f"- State Risk Level: {profile['state_risk_level']}\n"
            
        except Exception as e:
            formatted += f"Error formatting profile: {str(e)}\n"
        
        return formatted
    
    def _format_chat_history(self, history: List[Dict[str, Any]]) -> str:
        """Format chat history for context"""
        if not history:
            return "No previous conversation history."
        
        formatted = ""
        for i, msg in enumerate(history[-10:], 1):  # Last 10 messages
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")[:200]  # Truncate long messages
            formatted += f"{i}. {role}: {content}\n"
        
        return formatted
    
    def _build_investigation_context(self, investigation_results: Optional[Dict[str, Any]]) -> str:
        """Build context string from investigation results"""
        if not investigation_results:
            return "No investigation results available."
        
        context = "Investigation Results Summary:\n"
        
        try:
            # Extract key insights from investigation results
            if "results" in investigation_results:
                for result in investigation_results["results"]:
                    if "step_title" in result:
                        context += f"\n- {result['step_title']}:\n"
                        if "insights" in result:
                            for insight in result["insights"][:3]:  # Top 3 insights
                                context += f"  • {insight}\n"
                        if "recommendations" in result:
                            for rec in result["recommendations"][:2]:  # Top 2 recommendations
                                context += f"  • {rec}\n"
            
            # Add cumulative data if available
            if "cumulative_data" in investigation_results:
                cumulative = investigation_results["cumulative_data"]
                context += f"\nCumulative Analysis:\n"
                if "risk_analysis" in cumulative:
                    context += f"- Risk Assessment: {cumulative['risk_analysis']}\n"
                if "recommendation_factors" in cumulative:
                    context += f"- Key Factors: {list(cumulative['recommendation_factors'].keys())}\n"
                    
        except Exception as e:
            context += f"Error parsing investigation results: {str(e)}"
        
        return context
    
    def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session"""
        return self.messages.get(session_id, [])
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    async def _call_apim_directly(self, prompt: str) -> str:
        """Call APIM endpoint directly as fallback"""
        import os
        import httpx
        
        try:
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            key = os.getenv("AZURE_OPENAI_KEY")
            deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            
            if not all([endpoint, key, deployment]):
                raise Exception("Missing Azure OpenAI configuration")
            
            # Construct the API URL
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            # Remove trailing slash from endpoint to avoid double slashes
            clean_endpoint = endpoint.rstrip('/')
            api_url = f"{clean_endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
            
            headers = {
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": key
            }
            
            data = {
                "messages": [
                    {"role": "system", "content": "You are an AI banking analyst assistant. Provide helpful, professional responses."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, headers=headers, json=data, timeout=30.0)
                
                if response.status_code != 200:
                    response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            print(f"Direct APIM call failed: {e}")
            raise e
