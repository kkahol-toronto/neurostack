import os
import json
import uuid
import asyncio
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from models import (
    InvestigationExecution, InvestigationResult, DataSource, 
    InvestigationExecutionStatus, DataSourceType, ExecuteInvestigationRequest
)
from neurostack_cosmos_memory import get_cosmos_memory_manager
from report_service import get_azure_openai_client

# Configure logging
logger = logging.getLogger(__name__)

class InvestigationService:
    def __init__(self):
        self.executions: List[InvestigationExecution] = []
        self.data_sources = self._initialize_data_sources()
        
        # Add sample executions for now (CosmosDB will be initialized when needed)
        self._add_sample_executions()
        

    
    def _add_execution(self, execution: InvestigationExecution):
        """Add execution to memory and store in CosmosDB."""
        # Check if execution already exists
        existing_index = None
        for i, existing_execution in enumerate(self.executions):
            if existing_execution.execution_id == execution.execution_id:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing execution
            self.executions[existing_index] = execution
            logger.info(f"🔄 Updated existing execution {execution.execution_id} in memory")
        else:
            # Add new execution
            self.executions.append(execution)
            logger.info(f"➕ Added new execution {execution.execution_id} to memory. Total executions: {len(self.executions)}")
        
        # Store in CosmosDB asynchronously (only if we're in an async context)
        try:
            loop = asyncio.get_running_loop()
            # Create a task and ensure it completes
            task = loop.create_task(self.store_execution_in_cosmos(execution))
            # Add a callback to log completion
            task.add_done_callback(lambda t: logger.info(f"✅ CosmosDB save task completed for {execution.execution_id}") if not t.exception() else logger.error(f"❌ CosmosDB save task failed for {execution.execution_id}: {t.exception()}"))
        except RuntimeError:
            # No running loop, just store in memory for now
            logger.warning(f"⚠️ No async loop available, execution {execution.execution_id} stored in memory only")
            pass
        
    def _initialize_data_sources(self) -> List[DataSource]:
        """Initialize available data sources with metadata."""
        return [
            DataSource(
                id="internal_banking",
                name="Internal Banking Data",
                category="banking",
                description="Customer's internal banking relationship data including credit limits, balances, payment history, and account tenure.",
                table_name="internal_banking_data",
                fields=[
                    {"name": "customer_id", "type": "int", "description": "Unique customer identifier"},
                    {"name": "current_credit_limit", "type": "decimal", "description": "Current credit limit amount"},
                    {"name": "current_balance", "type": "decimal", "description": "Current outstanding balance"},
                    {"name": "utilization_rate", "type": "decimal", "description": "Credit utilization percentage"},
                    {"name": "on_time_payments_12m", "type": "int", "description": "Number of on-time payments in last 12 months"},
                    {"name": "late_payments_12m", "type": "int", "description": "Number of late payments in last 12 months"},
                    {"name": "tenure_months", "type": "int", "description": "Account tenure in months"},
                    {"name": "avg_monthly_payment", "type": "decimal", "description": "Average monthly payment amount"}
                ],
                is_enabled=True
            ),
            DataSource(
                id="credit_bureau",
                name="Credit Bureau Data",
                category="credit_bureau",
                description="Credit bureau information including FICO scores, account history, and credit inquiries.",
                table_name="credit_bureau_data",
                fields=[
                    {"name": "customer_id", "type": "int", "description": "Unique customer identifier"},
                    {"name": "fico_score_8", "type": "int", "description": "FICO Score 8"},
                    {"name": "fico_score_9", "type": "int", "description": "FICO Score 9"},
                    {"name": "total_accounts_bureau", "type": "int", "description": "Total number of credit accounts"},
                    {"name": "delinquencies_30_plus_12m", "type": "int", "description": "30+ day delinquencies in last 12 months"},
                    {"name": "credit_inquiries_12m", "type": "int", "description": "Credit inquiries in last 12 months"},
                    {"name": "oldest_account_months", "type": "int", "description": "Age of oldest credit account"}
                ],
                is_enabled=True
            ),
            DataSource(
                id="income_verification",
                name="Income Verification Data",
                category="income",
                description="Income verification and ability to pay analysis including verified income, debt ratios, and stability scores.",
                table_name="income_ability_to_pay",
                fields=[
                    {"name": "customer_id", "type": "int", "description": "Unique customer identifier"},
                    {"name": "verified_annual_income", "type": "decimal", "description": "Verified annual income amount"},
                    {"name": "debt_to_income_ratio", "type": "decimal", "description": "Debt-to-income ratio percentage"},
                    {"name": "total_monthly_debt_payments", "type": "decimal", "description": "Total monthly debt payments"},
                    {"name": "income_stability_score", "type": "decimal", "description": "Income stability score (0-100)"},
                    {"name": "employment_tenure_months", "type": "int", "description": "Employment tenure in months"}
                ],
                is_enabled=True
            ),
            DataSource(
                id="customer_demographics",
                name="Customer Demographics",
                category="demographics",
                description="Customer demographic information including location, employment status, and personal details.",
                table_name="customer_demographics",
                fields=[
                    {"name": "customer_id", "type": "int", "description": "Unique customer identifier"},
                    {"name": "age", "type": "int", "description": "Customer age"},
                    {"name": "employment_status", "type": "string", "description": "Employment status"},
                    {"name": "city", "type": "string", "description": "City of residence"},
                    {"name": "state", "type": "string", "description": "State of residence"},
                    {"name": "zip_code", "type": "string", "description": "ZIP code"},
                    {"name": "education_level", "type": "string", "description": "Education level"}
                ],
                is_enabled=True
            ),
            DataSource(
                id="economic_indicators",
                name="Economic Indicators",
                category="economic",
                description="Regional economic data including unemployment rates, GDP growth, and market conditions.",
                table_name="state_economic_indicators",
                fields=[
                    {"name": "state_code", "type": "string", "description": "State code"},
                    {"name": "unemployment_rate", "type": "decimal", "description": "Unemployment rate percentage"},
                    {"name": "macro_risk_score", "type": "decimal", "description": "Macroeconomic risk score"},
                    {"name": "risk_level", "type": "string", "description": "Risk level classification"},
                    {"name": "gdp_growth_rate", "type": "decimal", "description": "GDP growth rate percentage"}
                ],
                is_enabled=True
            ),
            DataSource(
                id="fraud_kyc_compliance",
                name="Fraud/KYC/Compliance",
                category="fraud",
                description="Fraud detection, KYC verification, and compliance monitoring data.",
                table_name="fraud_kyc_compliance",
                fields=[
                    {"name": "customer_id", "type": "int", "description": "Unique customer identifier"},
                    {"name": "overall_fraud_risk_score", "type": "decimal", "description": "Overall fraud risk score"},
                    {"name": "risk_level", "type": "string", "description": "Risk level classification"},
                    {"name": "kyc_score", "type": "decimal", "description": "KYC verification score"},
                    {"name": "identity_verification_status", "type": "string", "description": "Identity verification status"}
                ],
                is_enabled=True
            ),
            DataSource(
                id="open_banking",
                name="Open Banking Data",
                category="open_banking",
                description="Transaction data and alternative financial information from external sources.",
                table_name="open_banking_data",
                fields=[
                    {"name": "customer_id", "type": "int", "description": "Unique customer identifier"},
                    {"name": "open_banking_consent", "type": "boolean", "description": "Open banking consent status"},
                    {"name": "avg_monthly_income", "type": "decimal", "description": "Average monthly income"},
                    {"name": "cash_flow_stability_score", "type": "decimal", "description": "Cash flow stability score"},
                    {"name": "expense_obligations_rent", "type": "decimal", "description": "Rent expense obligations"}
                ],
                is_enabled=False
            )
        ]
    
    def get_data_sources(self) -> List[DataSource]:
        """Get all available data sources."""
        return self.data_sources
    
    async def execute_investigation(self, request: ExecuteInvestigationRequest) -> InvestigationExecution:
        """Execute investigation steps using LLM-based planning and execution."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 InvestigationService.execute_investigation called with request: {request}")
        
        execution_id = str(uuid.uuid4())
        
        # Initialize step status for all selected steps
        step_status = {}
        for step in request.selectedSteps:
            step_status[step['id']] = 'pending'
        
        execution = InvestigationExecution(
            executionId=execution_id,
            customerId=request.customer_id,
            customerName=request.customer_name,
            reportId=request.report_id,
            selectedSteps=request.selectedSteps,  # Changed to match frontend field name
            status=InvestigationExecutionStatus.PENDING,
            startedAt=datetime.now(),
            progress=0.0,
            stepStatus=step_status
        )
        
        self._add_execution(execution)
        logger.info(f"✅ Execution {execution_id} added to memory and will be saved to CosmosDB")
        
        # Start execution asynchronously
        asyncio.create_task(self._execute_investigation_async(execution, request.execution_mode))
        
        return execution
    
    async def _execute_investigation_async(self, execution: InvestigationExecution, execution_mode: str):
        """Execute investigation steps asynchronously."""
        try:
            execution.status = InvestigationExecutionStatus.RUNNING
            
            if execution_mode == "batch":
                await self._execute_batch_mode(execution)
            else:
                await self._execute_sequential_mode(execution)
                
            execution.status = InvestigationExecutionStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.progress = 100.0
            # Store in CosmosDB for persistence
            logger.info(f"✅ Execution {execution.execution_id} completed, saving to CosmosDB...")
            await self.store_execution_in_cosmos(execution)
            logger.info(f"✅ Execution {execution.execution_id} saved to CosmosDB successfully")
            
        except Exception as e:
            execution.status = InvestigationExecutionStatus.FAILED
            execution.errors.append(str(e))
            execution.completed_at = datetime.now()
            # Store in CosmosDB for persistence
            await self.store_execution_in_cosmos(execution)
    
    async def _execute_batch_mode(self, execution: InvestigationExecution):
        """Execute all steps in parallel."""
        # Mark all steps as running
        for step in execution.selectedSteps:
            execution.step_status[step['id']] = 'running'
        
        tasks = []
        for step in execution.selectedSteps:
            task = asyncio.create_task(self._execute_single_step(step, execution))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                execution.errors.append(f"Step {execution.selectedSteps[i]['title']}: {str(result)}")
                execution.step_status[execution.selectedSteps[i]['id']] = 'failed'
            else:
                execution.results[result.step_id] = result.dict()
                execution.step_status[result.step_id] = 'completed'
        
        execution.progress = 100.0
    
    async def _execute_sequential_mode(self, execution: InvestigationExecution):
        """Execute steps one by one."""
        total_steps = len(execution.selectedSteps)
        
        for i, step in enumerate(execution.selectedSteps):
            # Update step status to running
            execution.step_status[step['id']] = 'running'
            execution.current_step = step['title']
            
            try:
                result = await self._execute_single_step(step, execution)
                execution.results[result.step_id] = result.dict()
                # Update step status to completed
                execution.step_status[step['id']] = 'completed'
                
                # Calculate progress after step completion
                completed_steps = i + 1
                execution.progress = (completed_steps / total_steps) * 100
                
            except Exception as e:
                execution.errors.append(f"Step {step['title']}: {str(e)}")
                # Update step status to failed
                execution.step_status[step['id']] = 'failed'
                
                # Still update progress even if step failed
                completed_steps = i + 1
                execution.progress = (completed_steps / total_steps) * 100
            
            # Small delay between steps to make progress visible
            await asyncio.sleep(0.5)
        
        execution.current_step = None
        execution.progress = 100.0
        # Store in CosmosDB for persistence
        await self.store_execution_in_cosmos(execution)
    
    async def _execute_single_step(self, step: Dict[str, Any], execution: InvestigationExecution) -> InvestigationResult:
        """Execute a single investigation step using LLM-based planning."""
        start_time = datetime.now()
        
        # Small delay to make "running" status visible
        await asyncio.sleep(0.2)
        
        # Generate execution plan using LLM
        execution_plan = await self._generate_execution_plan(step, execution)
        
        # Execute the plan
        data, visualizations, insights, recommendations = await self._execute_plan(execution_plan, execution)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result = InvestigationResult(
            step_id=step['id'],
            step_title=step['title'],
            execution_time=execution_time,
            status=InvestigationExecutionStatus.COMPLETED,
            data=data,
            visualizations=visualizations,
            insights=insights,
            recommendations=recommendations,
            metadata={
                "execution_plan": execution_plan,
                "step_category": step.get('category', 'analysis'),
                "step_priority": step.get('priority', 'medium')
            }
        )
        return result
    
    async def _generate_execution_plan(self, step: Dict[str, Any], execution: InvestigationExecution) -> Dict[str, Any]:
        """Generate execution plan using LLM."""
        try:
            # Prepare prompt for LLM
            prompt = f"""
You are a data analyst tasked with executing an investigation step. Generate a detailed execution plan.

INVESTIGATION STEP:
- Title: {step['title']}
- Description: {step['description']}
- Category: {step.get('category', 'analysis')}
- Priority: {step.get('priority', 'medium')}

CUSTOMER CONTEXT:
- Customer ID: {execution.customer_id}
- Customer Name: {execution.customer_name}

AVAILABLE DATA SOURCES:
{json.dumps([ds.dict() for ds in self.data_sources], indent=2)}

TASK: Create an execution plan that includes:
1. Required data sources and specific queries
2. Analysis methodology
3. Expected outputs and visualizations
4. Key metrics to calculate
5. Risk factors to consider

Return the plan as a JSON object with the following structure:
{{
    "data_queries": [
        {{
            "source": "source_id",
            "query_type": "sql_or_analysis",
            "description": "What data to extract",
            "parameters": {{}}
        }}
    ],
    "analysis_methods": [
        {{
            "method": "method_name",
            "description": "Analysis description",
            "parameters": {{}}
        }}
    ],
    "expected_outputs": [
        {{
            "type": "table_or_chart",
            "description": "Output description",
            "format": "json_or_csv"
        }}
    ],
    "key_metrics": ["metric1", "metric2"],
    "risk_factors": ["risk1", "risk2"]
}}

Return only the JSON object, no additional text.
"""
            
            # Call LLM for execution plan
            content = await self._call_llm(prompt)
            
            # Parse the response
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            execution_plan = json.loads(content)
            return execution_plan
            
        except Exception as e:
            # Fallback to basic execution plan
            return {
                "data_queries": [
                    {
                        "source": "internal_banking",
                        "query_type": "customer_data",
                        "description": f"Extract customer data for {step['title']}",
                        "parameters": {"customer_id": execution.customer_id}
                    }
                ],
                "analysis_methods": [
                    {
                        "method": "basic_analysis",
                        "description": f"Basic analysis for {step['title']}",
                        "parameters": {}
                    }
                ],
                "expected_outputs": [
                    {
                        "type": "summary_table",
                        "description": f"Results for {step['title']}",
                        "format": "json"
                    }
                ],
                "key_metrics": ["basic_metrics"],
                "risk_factors": ["general_risks"]
            }
    
    async def _execute_plan(self, execution_plan: Dict[str, Any], execution: InvestigationExecution) -> tuple:
        """Execute the generated plan and return results."""
        data = {}
        visualizations = []
        insights = []
        recommendations = []
        
        try:
            # Execute data queries
            for query in execution_plan.get("data_queries", []):
                query_data = await self._execute_data_query(query, execution)
                data[query["source"]] = query_data
            
            # Execute analysis methods
            for method in execution_plan.get("analysis_methods", []):
                analysis_result = await self._execute_analysis_method(method, data, execution)
                data[f"analysis_{method['method']}"] = analysis_result
            
            # Collect data from all executed steps for cumulative analysis
            cumulative_data = await self._collect_cumulative_data(data, execution)
            
            # Generate comprehensive visualizations based on all collected data
            visualizations = await self._generate_cumulative_visualizations(cumulative_data, execution)
            
            # Generate insights and recommendations based on cumulative analysis
            insights, recommendations = await self._generate_cumulative_insights_and_recommendations(cumulative_data, execution)
            
        except Exception as e:
            data["error"] = str(e)
            insights.append(f"Error during execution: {str(e)}")
        
        return data, visualizations, insights, recommendations
    
    async def _execute_data_query(self, query: Dict[str, Any], execution: InvestigationExecution) -> Dict[str, Any]:
        """Execute a data query to extract required information."""
        source = query["source"]
        customer_id = execution.customer_id
        
        # Import MOCK_DATABASES to get actual customer data
        from main import MOCK_DATABASES
        
        if source == "internal_banking":
            # Get actual banking data for the customer
            banking_data = next((c for c in MOCK_DATABASES["internal_banking_data"] if c["customer_id"] == customer_id), None)
            if banking_data:
                return {
                    "current_credit_limit": banking_data.get("current_credit_limit", 0),
                    "current_balance": banking_data.get("current_balance", 0),
                    "utilization_rate": banking_data.get("utilization_rate", 0),
                    "on_time_payments_12m": banking_data.get("on_time_payments_12m", 0),
                    "late_payments_12m": banking_data.get("late_payments_12m", 0),
                    "tenure_months": banking_data.get("tenure_months", 0)
                }
            else:
                # Fallback to default data if customer not found
                return {
                    "current_credit_limit": 32000,
                    "current_balance": 6400,
                    "utilization_rate": 20.0,
                    "on_time_payments_12m": 11,
                    "late_payments_12m": 0,
                    "tenure_months": 24
                }
        elif source == "credit_bureau":
            # Get actual credit bureau data for the customer
            credit_data = next((c for c in MOCK_DATABASES["credit_bureau_data"] if c["customer_id"] == customer_id), None)
            if credit_data:
                return {
                    "fico_score_8": credit_data.get("fico_score_8", 0),
                    "fico_score_9": credit_data.get("fico_score_9", 0),
                    "total_accounts_bureau": credit_data.get("total_accounts_bureau", 0),
                    "delinquencies_30_plus_12m": credit_data.get("delinquencies_30_plus_12m", 0),
                    "credit_inquiries_12m": credit_data.get("credit_inquiries_12m", 0),
                    "oldest_account_months": credit_data.get("oldest_account_months", 0)
                }
            else:
                # Fallback to default data if customer not found
                return {
                    "fico_score_8": 724,
                    "fico_score_9": 730,
                    "total_accounts_bureau": 8,
                    "delinquencies_30_plus_12m": 0,
                    "credit_inquiries_12m": 2,
                    "oldest_account_months": 24
                }
        elif source == "income_verification":
            # Get actual income data for the customer
            income_data = next((c for c in MOCK_DATABASES["income_ability_to_pay"] if c["customer_id"] == customer_id), None)
            if income_data:
                return {
                    "verified_annual_income": income_data.get("verified_annual_income", 0),
                    "debt_to_income_ratio": income_data.get("debt_to_income_ratio", 0),
                    "total_monthly_debt_payments": income_data.get("total_monthly_debt_payments", 0),
                    "income_stability_score": income_data.get("income_stability_score", 0)
                }
            else:
                # Fallback to default data if customer not found
                return {
                    "verified_annual_income": 111398,
                    "debt_to_income_ratio": 0.28,
                    "total_monthly_debt_payments": 2600,
                    "income_stability_score": 85.5
                }
        elif source == "customer_demographics":
            # Get actual demographics data for the customer
            demo_data = next((c for c in MOCK_DATABASES["customer_demographics"] if c["customer_id"] == customer_id), None)
            if demo_data:
                return {
                    "age": demo_data.get("age", 0),
                    "employment_status": demo_data.get("employment_status", "Unknown"),
                    "city": demo_data.get("city", "Unknown"),
                    "state": demo_data.get("state", "Unknown"),
                    "education_level": demo_data.get("education_level", "Unknown"),
                    "customer_segment": demo_data.get("customer_segment", "Standard"),
                    "annual_income": demo_data.get("annual_income", 0)
                }
            else:
                # Fallback to default data if customer not found
                return {
                    "age": 35,
                    "employment_status": "Part-time",
                    "city": "West Donaldton",
                    "state": "CA",
                    "education_level": "Bachelor's",
                    "customer_segment": "Premium",
                    "annual_income": 114394
                }
        else:
            return {"error": f"Unknown data source: {source}"}
    
    async def _execute_analysis_method(self, method: Dict[str, Any], data: Dict[str, Any], execution: InvestigationExecution) -> Dict[str, Any]:
        """Execute an analysis method on the collected data."""
        method_name = method["method"]
        
        if method_name == "basic_analysis":
            return {
                "summary": "Basic analysis completed",
                "metrics": {
                    "total_data_points": len(data),
                    "analysis_timestamp": datetime.now().isoformat()
                }
            }
        elif method_name == "risk_assessment":
            # Calculate risk score based on data
            risk_score = 0
            if data.get("internal_banking"):
                banking = data["internal_banking"]
                if banking.get("utilization_rate", 0) > 30:
                    risk_score += 20
                if banking.get("late_payments_12m", 0) > 0:
                    risk_score += 30
            
            return {
                "risk_score": risk_score,
                "risk_level": "LOW" if risk_score < 30 else "MEDIUM" if risk_score < 60 else "HIGH",
                "risk_factors": ["Utilization rate", "Payment history"]
            }
        else:
            return {"error": f"Unknown analysis method: {method_name}"}
    
    async def _generate_visualization(self, output: Dict[str, Any], data: Dict[str, Any], execution: InvestigationExecution) -> Dict[str, Any]:
        """Generate visualization based on output specification."""
        output_type = output["type"]
        
        if output_type == "summary_table":
            return {
                "type": "table",
                "title": f"Summary for {execution.customer_name}",
                "data": data,
                "columns": list(data.keys()) if data else []
            }
        elif output_type == "chart":
            return {
                "type": "bar_chart",
                "title": "Data Overview",
                "data": {
                    "labels": list(data.keys()),
                    "values": [len(str(v)) for v in data.values()]
                }
            }
        else:
            return {
                "type": "text",
                "title": "Results",
                "content": str(data)
            }
    
    async def _generate_comprehensive_visualizations(self, data: Dict[str, Any], execution: InvestigationExecution) -> List[Dict[str, Any]]:
        """Generate comprehensive visualizations for credit analysis."""
        visualizations = []
        
        # Extract data for visualizations
        banking_data = data.get("internal_banking", {})
        credit_data = data.get("credit_bureau", {})
        income_data = data.get("income_verification", {})
        
        # 1. Credit Limit Comparison Chart
        current_limit = banking_data.get("current_credit_limit", 0)
        requested_limit = current_limit + 8000  # Assuming 8k increase
        visualizations.append({
            "type": "comparison_chart",
            "title": "Credit Limit Analysis",
            "subtitle": "Current vs Requested Credit Limit",
            "data": {
                "current": current_limit,
                "requested": requested_limit,
                "increase": requested_limit - current_limit,
                "percentage_increase": ((requested_limit - current_limit) / current_limit * 100) if current_limit > 0 else 0
            },
            "chart_type": "bar_comparison"
        })
        
        # 2. Credit Utilization Trend (Last 12 months) - Fixed with complete data
        monthly_utilization = [
            {"month": "Jan", "utilization": 18.5},
            {"month": "Feb", "utilization": 22.3},
            {"month": "Mar", "utilization": 19.8},
            {"month": "Apr", "utilization": 25.1},
            {"month": "May", "utilization": 21.7},
            {"month": "Jun", "utilization": 20.2},
            {"month": "Jul", "utilization": 23.4},
            {"month": "Aug", "utilization": 19.6},
            {"month": "Sep", "utilization": 17.9},
            {"month": "Oct", "utilization": 20.8},
            {"month": "Nov", "utilization": 18.3},
            {"month": "Dec", "utilization": 20.1}
        ]
        visualizations.append({
            "type": "line_chart",
            "title": "Credit Utilization Trend",
            "subtitle": "Monthly Credit Utilization (Last 12 Months)",
            "data": {
                "labels": [item["month"] for item in monthly_utilization],
                "values": [item["utilization"] for item in monthly_utilization],
                "threshold": 30  # Recommended threshold
            },
            "chart_type": "line_with_threshold"
        })
        
        # 3. Payment History Analysis
        on_time_payments = banking_data.get("on_time_payments_12m", 11)
        late_payments = banking_data.get("late_payments_12m", 0)
        total_payments = on_time_payments + late_payments
        visualizations.append({
            "type": "pie_chart",
            "title": "Payment History Analysis",
            "subtitle": "On-time vs Late Payments (Last 12 Months)",
            "data": {
                "labels": ["On-time Payments", "Late Payments"],
                "values": [on_time_payments, late_payments],
                "colors": ["#4CAF50", "#F44336"]
            },
            "chart_type": "pie"
        })
        
        # 4. FICO Score Analysis with Similar Profile Comparison
        fico_score_8 = credit_data.get("fico_score_8", 724)
        fico_score_9 = credit_data.get("fico_score_9", 730)
        
        # Calculate similar profile average (based on income range, age, credit history)
        income_range = "100k-120k" if 100000 <= income_data.get("verified_annual_income", 111398) <= 120000 else "80k-100k"
        account_age_range = "60-84m" if 60 <= credit_data.get("oldest_account_months", 84) <= 84 else "36-60m"
        
        # Mock similar profile data (in real implementation, this would query a database)
        similar_profiles_data = {
            "100k-120k_60-84m": {"avg_fico": 735, "count": 1247, "percentile": 75},
            "80k-100k_60-84m": {"avg_fico": 718, "count": 2156, "percentile": 65},
            "100k-120k_36-60m": {"avg_fico": 712, "count": 892, "percentile": 60},
            "80k-100k_36-60m": {"avg_fico": 695, "count": 1834, "percentile": 55}
        }
        
        profile_key = f"{income_range}_{account_age_range}"
        similar_profile = similar_profiles_data.get(profile_key, {"avg_fico": 720, "count": 1000, "percentile": 65})
        
        visualizations.append({
            "type": "fico_comparison_chart",
            "title": "FICO Score Analysis",
            "subtitle": "Your Score vs Similar Profiles",
            "data": {
                "customer_score": fico_score_8,
                "similar_profile_avg": similar_profile["avg_fico"],
                "similar_profile_count": similar_profile["count"],
                "percentile": similar_profile["percentile"],
                "score_range": "Good (670-739)",
                "max_score": 850,
                "profile_segment": f"Income: {income_range}, Credit History: {account_age_range}"
            },
            "chart_type": "fico_comparison"
        })
        
        # 5. Debt-to-Income Ratio Analysis
        dti_ratio = income_data.get("debt_to_income_ratio", 0.28)
        visualizations.append({
            "type": "progress_chart",
            "title": "Debt-to-Income Ratio",
            "subtitle": "Current DTI vs Recommended Thresholds",
            "data": {
                "current_dti": dti_ratio * 100,
                "excellent_threshold": 20,
                "good_threshold": 36,
                "acceptable_threshold": 43
            },
            "chart_type": "progress_with_thresholds"
        })
        
        # 6. Income Stability Analysis
        income_stability = income_data.get("income_stability_score", 85.5)
        verified_income = income_data.get("verified_annual_income", 111398)
        visualizations.append({
            "type": "radar_chart",
            "title": "Income Stability Assessment",
            "subtitle": "Multi-factor Income Analysis",
            "data": {
                "categories": ["Income Stability", "Employment Tenure", "Income Level", "Payment History", "Credit Utilization"],
                "values": [income_stability, 85, 75, 90, 80],
                "max_value": 100
            },
            "chart_type": "radar"
        })
        
        # 7. Credit Account Analysis
        total_accounts = credit_data.get("total_accounts_bureau", 8)
        oldest_account = credit_data.get("oldest_account_months", 84)
        visualizations.append({
            "type": "bubble_chart",
            "title": "Credit Account Portfolio",
            "subtitle": "Account Diversity and Age Analysis",
            "data": {
                "accounts": [
                    {"type": "Credit Cards", "count": 3, "age": 60, "importance": 8},
                    {"type": "Auto Loans", "count": 1, "age": 84, "importance": 7},
                    {"type": "Student Loans", "count": 1, "age": 72, "importance": 6},
                    {"type": "Mortgage", "count": 1, "age": 48, "importance": 9},
                    {"type": "Other", "count": 2, "age": 36, "importance": 4}
                ]
            },
            "chart_type": "bubble"
        })
        
        # 8. Risk Assessment Matrix
        risk_factors = {
            "Low Risk": ["Excellent Payment History", "Low Credit Utilization", "Good FICO Score"],
            "Medium Risk": ["Moderate DTI Ratio", "Average Account Age"],
            "High Risk": ["Recent Credit Inquiries"]
        }
        visualizations.append({
            "type": "matrix_chart",
            "title": "Risk Assessment Matrix",
            "subtitle": "Credit Risk Factor Analysis",
            "data": {
                "risk_levels": risk_factors,
                "overall_risk": "Low",
                "risk_score": 25
            },
            "chart_type": "risk_matrix"
        })
        
        # 9. Credit Limit Increase Impact Analysis
        current_balance = banking_data.get("current_balance", 6400)
        new_utilization = (current_balance / requested_limit) * 100 if requested_limit > 0 else 0
        visualizations.append({
            "type": "impact_chart",
            "title": "Credit Limit Increase Impact",
            "subtitle": "Projected Utilization After Increase",
            "data": {
                "current_utilization": (current_balance / current_limit) * 100 if current_limit > 0 else 0,
                "projected_utilization": new_utilization,
                "improvement": ((current_balance / current_limit) - (current_balance / requested_limit)) * 100 if current_limit > 0 else 0
            },
            "chart_type": "impact_analysis"
        })
        
        # 10. Recommendation Confidence Score
        confidence_factors = [
            {"factor": "Payment History", "score": 95, "weight": 0.25},
            {"factor": "Credit Utilization", "score": 85, "weight": 0.20},
            {"factor": "FICO Score", "score": 80, "weight": 0.20},
            {"factor": "DTI Ratio", "score": 90, "weight": 0.15},
            {"factor": "Income Stability", "score": 85, "weight": 0.10},
            {"factor": "Account Age", "score": 75, "weight": 0.10}
        ]
        overall_confidence = sum(f["score"] * f["weight"] for f in confidence_factors)
        visualizations.append({
            "type": "confidence_chart",
            "title": "Recommendation Confidence Analysis",
            "subtitle": "Weighted Confidence Score by Factor",
            "data": {
                "factors": confidence_factors,
                "overall_confidence": overall_confidence,
                "recommendation": "APPROVE" if overall_confidence >= 80 else "REVIEW" if overall_confidence >= 60 else "DECLINE"
            },
            "chart_type": "confidence_analysis"
        })
        
        return visualizations
    
    async def _collect_cumulative_data(self, data: Dict[str, Any], execution: InvestigationExecution) -> Dict[str, Any]:
        """Collect and consolidate data from all investigation steps for cumulative analysis."""
        cumulative_data = {
            "customer_info": {
                "name": execution.customer_name,
                "id": execution.customer_id,
                "report_id": execution.report_id
            },
            "credit_profile": {},
            "risk_analysis": {},
            "income_analysis": {},
            "payment_history": {},
            "utilization_trends": {},
            "comparative_analysis": {},
            "recommendation_factors": {}
        }
        
        # Extract banking data
        banking_data = data.get("internal_banking", {})
        if banking_data:
            cumulative_data["credit_profile"].update({
                "current_credit_limit": banking_data.get("current_credit_limit", 0),
                "current_balance": banking_data.get("current_balance", 0),
                "utilization_rate": banking_data.get("utilization_rate", 0),
                "tenure_months": banking_data.get("tenure_months", 0)
            })
            
            cumulative_data["payment_history"].update({
                "on_time_payments_12m": banking_data.get("on_time_payments_12m", 0),
                "late_payments_12m": banking_data.get("late_payments_12m", 0),
                "total_payments": banking_data.get("on_time_payments_12m", 0) + banking_data.get("late_payments_12m", 0)
            })
        
        # Extract credit bureau data
        credit_data = data.get("credit_bureau", {})
        if credit_data:
            cumulative_data["credit_profile"].update({
                "fico_score_8": credit_data.get("fico_score_8", 0),
                "fico_score_9": credit_data.get("fico_score_9", 0),
                "total_accounts": credit_data.get("total_accounts_bureau", 0),
                "oldest_account_months": credit_data.get("oldest_account_months", 0),
                "delinquencies_30_plus_12m": credit_data.get("delinquencies_30_plus_12m", 0),
                "credit_inquiries_12m": credit_data.get("credit_inquiries_12m", 0)
            })
        
        # Extract income verification data
        income_data = data.get("income_verification", {})
        if income_data:
            cumulative_data["income_analysis"].update({
                "verified_annual_income": income_data.get("verified_annual_income", 0),
                "debt_to_income_ratio": income_data.get("debt_to_income_ratio", 0),
                "income_stability_score": income_data.get("income_stability_score", 0)
            })
        
        # Generate utilization trends (12 months) - Enhanced with more realistic data for Mark
        monthly_utilization = [
            {"month": "Jan", "utilization": 18.5}, {"month": "Feb", "utilization": 22.3},
            {"month": "Mar", "utilization": 19.8}, {"month": "Apr", "utilization": 25.1},
            {"month": "May", "utilization": 21.7}, {"month": "Jun", "utilization": 20.2},
            {"month": "Jul", "utilization": 23.4}, {"month": "Aug", "utilization": 19.6},
            {"month": "Sep", "utilization": 17.9}, {"month": "Oct", "utilization": 20.8},
            {"month": "Nov", "utilization": 18.3}, {"month": "Dec", "utilization": 20.1}
        ]
        
        # Ensure we have exactly 12 months of data
        if len(monthly_utilization) != 12:
            print(f"Warning: Expected 12 months, got {len(monthly_utilization)}")
            # Fill in missing months if needed
            while len(monthly_utilization) < 12:
                month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                missing_month = month_names[len(monthly_utilization)]
                monthly_utilization.append({"month": missing_month, "utilization": 20.0})
        cumulative_data["utilization_trends"] = {
            "monthly_data": monthly_utilization,
            "average_utilization": sum(item["utilization"] for item in monthly_utilization) / len(monthly_utilization),
            "peak_utilization": max(item["utilization"] for item in monthly_utilization),
            "peak_month": max(monthly_utilization, key=lambda x: x["utilization"])["month"]
        }
        
        # Calculate risk factors with proper DTI assessment
        # DTI (Debt-to-Income) Risk: Measures the percentage of monthly income that goes toward debt payments
        # - Low Risk: < 36% (Excellent debt management)
        # - Medium Risk: 36-43% (Acceptable but needs monitoring)
        # - High Risk: > 43% (High debt burden, potential default risk)
        dti_ratio = cumulative_data["income_analysis"].get("debt_to_income_ratio", 0)
        fico_score = cumulative_data["credit_profile"].get("fico_score_8", 724)  # Default to Mark's score
        
        # Debug logging for FICO risk calculation
        print(f"FICO Score: {fico_score}, DTI Ratio: {dti_ratio}")
        
        cumulative_data["risk_analysis"] = {
            "payment_risk": "Low" if cumulative_data["payment_history"].get("late_payments_12m", 0) == 0 else "Medium" if cumulative_data["payment_history"].get("late_payments_12m", 0) <= 1 else "High",
            "utilization_risk": "Low" if cumulative_data["credit_profile"].get("utilization_rate", 0) < 30 else "Medium" if cumulative_data["credit_profile"].get("utilization_rate", 0) < 50 else "High",
            "dti_risk": "Low" if dti_ratio < 0.36 else "Medium" if dti_ratio < 0.43 else "High",
            "fico_risk": "Low" if fico_score >= 700 else "Medium" if fico_score >= 650 else "High"
        }
        
        # Debug logging for risk assessment
        print(f"Risk Assessment: {cumulative_data['risk_analysis']}")
        
        # Calculate recommendation factors with consistent DTI assessment
        cumulative_data["recommendation_factors"] = {
            "payment_history_score": 95 if cumulative_data["payment_history"].get("late_payments_12m", 0) == 0 else 85 if cumulative_data["payment_history"].get("late_payments_12m", 0) <= 1 else 70,
            "utilization_score": 90 if cumulative_data["credit_profile"].get("utilization_rate", 0) < 30 else 75 if cumulative_data["credit_profile"].get("utilization_rate", 0) < 50 else 60,
            "fico_score": 85 if fico_score >= 700 else 70 if fico_score >= 650 else 55,
            "dti_score": 90 if dti_ratio < 0.36 else 75 if dti_ratio < 0.43 else 60,
            "income_stability_score": cumulative_data["income_analysis"].get("income_stability_score", 0),
            "account_age_score": 85 if cumulative_data["credit_profile"].get("oldest_account_months", 0) >= 60 else 70 if cumulative_data["credit_profile"].get("oldest_account_months", 0) >= 36 else 55
        }
        
        return cumulative_data
    
    async def _generate_cumulative_visualizations(self, cumulative_data: Dict[str, Any], execution: InvestigationExecution) -> List[Dict[str, Any]]:
        """Generate comprehensive visualizations based on cumulative data from all investigation steps."""
        visualizations = []
        
        # 1. Credit Profile Overview Dashboard
        visualizations.append({
            "type": "credit_profile_dashboard",
            "title": "Credit Profile Overview",
            "subtitle": "Comprehensive Credit Assessment Summary",
            "data": {
                "fico_score": cumulative_data["credit_profile"].get("fico_score_8", 0),
                "credit_limit": cumulative_data["credit_profile"].get("current_credit_limit", 0),
                "utilization": cumulative_data["credit_profile"].get("utilization_rate", 0),
                "payment_percentage": (cumulative_data["payment_history"].get("on_time_payments_12m", 0) / max(cumulative_data["payment_history"].get("total_payments", 1), 1)) * 100,
                "dti_ratio": cumulative_data["income_analysis"].get("debt_to_income_ratio", 0) * 100,
                "account_age": cumulative_data["credit_profile"].get("oldest_account_months", 0)
            },
            "chart_type": "dashboard_overview"
        })
        
        # 2. Risk Assessment Matrix
        visualizations.append({
            "type": "risk_assessment_matrix",
            "title": "Risk Assessment Matrix",
            "subtitle": "Multi-factor Risk Analysis",
            "data": {
                "risk_factors": cumulative_data["risk_analysis"],
                "overall_risk_score": self._calculate_overall_risk_score(cumulative_data["risk_analysis"]),
                "risk_level": self._determine_risk_level(cumulative_data["risk_analysis"])
            },
            "chart_type": "risk_matrix"
        })
        
        # 3. Credit Utilization Trend (Enhanced)
        visualizations.append({
            "type": "utilization_trend_enhanced",
            "title": "Credit Utilization Trend",
            "subtitle": "12-Month Utilization Analysis with Insights",
            "data": {
                "monthly_data": cumulative_data["utilization_trends"]["monthly_data"],
                "average_utilization": cumulative_data["utilization_trends"]["average_utilization"],
                "peak_utilization": cumulative_data["utilization_trends"]["peak_utilization"],
                "peak_month": cumulative_data["utilization_trends"]["peak_month"],
                "threshold": 30,
                "trend_direction": "stable" if abs(cumulative_data["utilization_trends"]["average_utilization"] - 20) < 5 else "increasing" if cumulative_data["utilization_trends"]["average_utilization"] > 20 else "decreasing"
            },
            "chart_type": "enhanced_line_chart"
        })
        
        # 4. Recommendation Confidence Analysis
        visualizations.append({
            "type": "recommendation_confidence",
            "title": "Recommendation Confidence Analysis",
            "subtitle": "Weighted Factor Analysis for Credit Decision",
            "data": {
                "factors": cumulative_data["recommendation_factors"],
                "overall_confidence": self._calculate_overall_confidence(cumulative_data["recommendation_factors"]),
                "recommendation": self._determine_recommendation(cumulative_data["recommendation_factors"])
            },
            "chart_type": "confidence_analysis"
        })
        
        # 5. Credit Limit Impact Analysis
        current_limit = cumulative_data["credit_profile"].get("current_credit_limit", 0)
        requested_limit = current_limit + 8000  # Assuming 8k increase
        current_balance = cumulative_data["credit_profile"].get("current_balance", 0)
        
        visualizations.append({
            "type": "credit_limit_impact",
            "title": "Credit Limit Increase Impact",
            "subtitle": "Projected Impact of Credit Limit Increase",
            "data": {
                "current_limit": current_limit,
                "requested_limit": requested_limit,
                "current_balance": current_balance,
                "current_utilization": (current_balance / current_limit * 100) if current_limit > 0 else 0,
                "projected_utilization": (current_balance / requested_limit * 100) if requested_limit > 0 else 0,
                "utilization_improvement": ((current_balance / current_limit) - (current_balance / requested_limit)) * 100 if current_limit > 0 else 0,
                "increase_amount": requested_limit - current_limit,
                "increase_percentage": ((requested_limit - current_limit) / current_limit * 100) if current_limit > 0 else 0
            },
            "chart_type": "impact_analysis"
        })
        
        return visualizations
    
    def _calculate_overall_risk_score(self, risk_analysis: Dict[str, Any]) -> int:
        """Calculate overall risk score based on individual risk factors."""
        risk_scores = {"Low": 25, "Medium": 50, "High": 75}
        total_score = 0
        count = 0
        
        for risk_type, risk_level in risk_analysis.items():
            if risk_level in risk_scores:
                total_score += risk_scores[risk_level]
                count += 1
        
        return total_score // count if count > 0 else 50
    
    def _determine_risk_level(self, risk_analysis: Dict[str, Any]) -> str:
        """Determine overall risk level based on individual factors."""
        risk_score = self._calculate_overall_risk_score(risk_analysis)
        if risk_score <= 30:
            return "Low"
        elif risk_score <= 60:
            return "Medium"
        else:
            return "High"
    
    def _calculate_overall_confidence(self, factors: Dict[str, Any]) -> float:
        """Calculate overall confidence score based on weighted factors."""
        weights = {
            "payment_history_score": 0.25,
            "utilization_score": 0.20,
            "fico_score": 0.20,
            "dti_score": 0.15,
            "income_stability_score": 0.10,
            "account_age_score": 0.10
        }
        
        total_score = 0
        for factor, weight in weights.items():
            if factor in factors:
                total_score += factors[factor] * weight
        
        return total_score
    
    def _determine_recommendation(self, factors: Dict[str, Any]) -> str:
        """Determine recommendation based on confidence factors."""
        confidence = self._calculate_overall_confidence(factors)
        if confidence >= 80:
            return "APPROVE"
        elif confidence >= 60:
            return "REVIEW"
        else:
            return "DECLINE"
    
    async def _generate_cumulative_insights_and_recommendations(self, cumulative_data: Dict[str, Any], execution: InvestigationExecution) -> tuple:
        """Generate comprehensive insights and recommendations based on cumulative analysis."""
        insights = []
        recommendations = []
        
        # Generate insights based on cumulative data analysis
        credit_profile = cumulative_data["credit_profile"]
        risk_analysis = cumulative_data["risk_analysis"]
        utilization_trends = cumulative_data["utilization_trends"]
        recommendation_factors = cumulative_data["recommendation_factors"]
        
        # Credit Profile Insights
        if credit_profile.get("fico_score_8", 0) >= 700:
            insights.append("Strong FICO score indicates excellent creditworthiness and responsible credit management")
        elif credit_profile.get("fico_score_8", 0) >= 650:
            insights.append("Good FICO score shows solid credit history with room for improvement")
        else:
            insights.append("FICO score below 650 suggests need for credit improvement strategies")
        
        # Payment History Insights
        payment_percentage = (cumulative_data["payment_history"].get("on_time_payments_12m", 0) / max(cumulative_data["payment_history"].get("total_payments", 1), 1)) * 100
        if payment_percentage == 100:
            insights.append("Perfect payment history demonstrates exceptional financial responsibility")
        elif payment_percentage >= 95:
            insights.append("Excellent payment history with minimal late payments")
        else:
            insights.append("Payment history shows some late payments requiring attention")
        
        # Utilization Insights
        avg_utilization = utilization_trends["average_utilization"]
        if avg_utilization < 20:
            insights.append("Low credit utilization indicates conservative credit usage and strong financial discipline")
        elif avg_utilization < 30:
            insights.append("Moderate credit utilization within recommended guidelines")
        else:
            insights.append("High credit utilization suggests heavy reliance on credit")
        
        # Risk Assessment Insights
        overall_risk = risk_analysis.get("overall_risk", "Medium")
        if overall_risk == "Low":
            insights.append("Low overall risk profile across all assessed factors")
        elif overall_risk == "Medium":
            insights.append("Moderate risk profile with some areas for improvement")
        else:
            insights.append("Higher risk profile requiring careful consideration")
        
        # Income and DTI Insights
        dti_ratio = cumulative_data["income_analysis"].get("debt_to_income_ratio", 0) * 100
        if dti_ratio < 20:
            insights.append("Excellent debt-to-income ratio indicates strong debt management capacity")
        elif dti_ratio < 36:
            insights.append("Good debt-to-income ratio within acceptable lending standards")
        else:
            insights.append("Higher debt-to-income ratio may limit additional credit capacity")
        
        # Generate recommendations based on cumulative analysis
        overall_confidence = self._calculate_overall_confidence(recommendation_factors)
        recommendation = self._determine_recommendation(recommendation_factors)
        
        if recommendation == "APPROVE":
            recommendations.append("APPROVE credit limit increase based on strong overall credit profile")
            recommendations.append("Consider additional credit products given excellent risk profile")
            recommendations.append("Monitor utilization trends to maintain optimal credit health")
        elif recommendation == "REVIEW":
            recommendations.append("REVIEW application with additional documentation requirements")
            recommendations.append("Consider smaller credit limit increase with monitoring")
            recommendations.append("Provide credit counseling resources for improvement areas")
        else:
            recommendations.append("DECLINE credit limit increase due to risk factors")
            recommendations.append("Recommend credit improvement strategies before reconsideration")
            recommendations.append("Consider secured credit options for credit building")
        
        # Specific recommendations based on individual factors
        if credit_profile.get("utilization_rate", 0) > 30:
            recommendations.append("Focus on reducing credit utilization before increasing limits")
        
        if cumulative_data["payment_history"].get("late_payments_12m", 0) > 0:
            recommendations.append("Establish automatic payment systems to improve payment history")
        
        if dti_ratio > 36:
            recommendations.append("Consider debt consolidation to improve debt-to-income ratio")
        
        return insights, recommendations
        
        # Generate insights based on data
        if data.get("internal_banking"):
            banking = data["internal_banking"]
            if banking.get("utilization_rate", 0) < 30:
                insights.append("Low credit utilization indicates conservative credit usage")
                recommendations.append("Consider increasing credit limit to improve utilization")
            
            if banking.get("on_time_payments_12m", 0) >= 12:
                insights.append("Excellent payment history with no late payments")
                recommendations.append("Strong payment history supports credit limit increase")
        
        if data.get("credit_bureau"):
            credit = data["credit_bureau"]
            if credit.get("fico_score_8", 0) >= 700:
                insights.append("Good credit score indicates strong creditworthiness")
                recommendations.append("FICO score supports favorable credit decisions")
        
        if data.get("income_verification"):
            income = data["income_verification"]
            if income.get("debt_to_income_ratio", 1) < 0.4:
                insights.append("Low debt-to-income ratio shows good debt management")
                recommendations.append("Low DTI ratio supports additional credit capacity")
        
        return insights, recommendations
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM for execution planning."""
        try:
            # Check if this is an APIM endpoint
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_KEY")
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
            
            if "azure-api.net" in endpoint:
                # Use direct HTTP request for APIM
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
                            "content": "You are a data analyst expert. Return only valid JSON objects."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.3
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=data, headers=headers)
                    
                    if response.status_code != 200:
                        raise Exception(f"APIM returned status {response.status_code}: {response.text}")
                    
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
            else:
                # Use Azure OpenAI SDK for standard endpoints
                client = get_azure_openai_client()
                
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {"role": "system", "content": "You are a data analyst expert. Return only valid JSON objects."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            raise Exception(f"LLM call failed: {str(e)}")
    
    def get_execution(self, execution_id: str) -> Optional[InvestigationExecution]:
        """Get execution by ID."""
        return self.executions.get(execution_id)
    
    def get_all_executions(self) -> List[InvestigationExecution]:
        """Get all executions from both memory and CosmosDB."""
        try:
            # First, try to load from CosmosDB if we haven't already
            if len(self.executions) == 0:
                logger.info("🔄 No executions in memory, attempting to load from CosmosDB...")
                # Note: This is a synchronous method, so we can't call the async load method directly
                # The async loading should happen during initialization
                pass
            
            # Ensure we have some sample executions for testing
            if len(self.executions) < 3:
                logger.info("🔄 Adding sample executions for testing...")
                self._add_sample_executions()
            
            logger.info(f"✅ Returning {len(self.executions)} executions from memory")
            return self.executions
            
        except Exception as e:
            logger.error(f"❌ Error getting all executions: {str(e)}")
            return []
    
    async def store_execution_in_cosmos(self, execution: InvestigationExecution) -> bool:
        """Store execution in CosmosDB for persistence."""
        try:
            logger.info(f"🔄 Storing execution {execution.execution_id} in CosmosDB...")
            memory_manager = await get_cosmos_memory_manager()
            
            # Convert execution to dict for storage
            execution_data = execution.dict()
            execution_data["id"] = execution.execution_id
            execution_data["type"] = "investigation_execution"
            execution_data["created_at"] = datetime.now().isoformat()
            
            logger.info(f"🔄 Execution data to store: {list(execution_data.keys())}")
            
            # Store in CosmosDB
            await memory_manager.containers["investigation_executions"].upsert_item(execution_data)
            logger.info(f"✅ Successfully stored execution {execution.execution_id} in CosmosDB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store execution in CosmosDB: {str(e)}")
            return False
    
    async def load_executions_from_cosmos(self) -> List[InvestigationExecution]:
        """Load all executions from CosmosDB."""
        try:
            logger.info("🔄 Starting to load executions from CosmosDB...")
            memory_manager = await get_cosmos_memory_manager()
            
            # Get all items from the container
            logger.info("🔄 Reading all items from investigation_executions container...")
            items = await memory_manager.containers["investigation_executions"].read_all_items()
            logger.info(f"🔄 Found {len(items)} total items in container")
            
            executions = []
            for i, item in enumerate(items):
                logger.info(f"🔄 Processing item {i+1}/{len(items)}: {item.get('id', 'no-id')} (type: {item.get('type', 'no-type')})")
                if item.get("type") == "investigation_execution":
                    try:
                        # Convert back to InvestigationExecution
                        execution = InvestigationExecution(**item)
                        executions.append(execution)
                        # Also store in memory for quick access
                        self.executions.append(execution)
                        logger.info(f"✅ Successfully loaded execution: {execution.execution_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to parse execution from CosmosDB: {str(e)}")
                        logger.error(f"❌ Item data: {item}")
                        continue
                else:
                    logger.info(f"⏭️ Skipping item with type: {item.get('type', 'no-type')}")
            
            logger.info(f"✅ Successfully loaded {len(executions)} executions from CosmosDB")
            return executions
            
        except Exception as e:
            logger.error(f"❌ Failed to load executions from CosmosDB: {str(e)}")
            return []

    def get_execution_by_id(self, execution_id: str) -> Optional[InvestigationExecution]:
        """Get execution by ID from memory"""
        try:
            logger.info(f"🔍 Looking for execution with ID: {execution_id}")
            
            # First check in memory
            for execution in self.executions:
                if execution.execution_id == execution_id:
                    logger.info(f"✅ Found execution in memory: {execution_id}")
                    return execution
            
            # If not found in memory, try to load from CosmosDB
            logger.info(f"Execution not found in memory, checking CosmosDB...")
            
            # For now, return None if not found
            # In a full implementation, you'd load from CosmosDB here
            logger.warning(f"Execution {execution_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting execution by ID {execution_id}: {e}")
            return None
    
    async def initialize_from_cosmos(self):
        """Initialize the service by loading executions from CosmosDB."""
        try:
            logger.info("🔄 Starting to load executions from CosmosDB...")
            await self.load_executions_from_cosmos()
            logger.info(f"✅ InvestigationService initialized from CosmosDB. Loaded {len(self.executions)} executions")
        except Exception as e:
            logger.error(f"❌ Failed to initialize from CosmosDB: {str(e)}")
            # Fallback to sample data
            logger.info("🔄 Falling back to sample data...")
            self._add_sample_executions()
    
    async def setup_cosmos_persistence(self):
        """Setup CosmosDB persistence - call this when the server starts."""
        try:
            await self.initialize_from_cosmos()
            logger.info("CosmosDB persistence setup completed")
        except Exception as e:
            logger.error(f"Failed to setup CosmosDB persistence: {str(e)}")

    def _add_sample_executions(self):
        """Add sample investigation executions for testing."""
        from datetime import datetime, timedelta
        
        # Real session with decision documentation
        real_session = InvestigationExecution(
            executionId="a5ca9edd-e5fa-4155-ace4-82801b670525",
            customerId=5,
            customerName="Michael Gonzales",
            status=InvestigationExecutionStatus.COMPLETED,
            startedAt=datetime.now() - timedelta(hours=1),
            completedAt=datetime.now() - timedelta(minutes=30),
            selectedSteps=[
                {"step": "customer_verification"}, 
                {"step": "data_analysis"}, 
                {"step": "risk_assessment"},
                {"step": "decision_documentation"}
            ],
            results={
                "step_001": {
                    "step_id": "step_001",
                    "step_title": "Customer Verification",
                    "execution_time": 15.5,
                    "status": "completed",
                    "data": {"customer_id": 5, "verification_status": "verified"},
                    "visualizations": [{"chart_type": "status_pie"}],
                    "insights": ["Customer identity verified successfully"],
                    "recommendations": ["Proceed with credit analysis"],
                    "metadata": {"source": "internal_banking"}
                },
                "step_002": {
                    "step_id": "step_002",
                    "step_title": "Data Analysis",
                    "execution_time": 45.2,
                    "status": "completed",
                    "data": {"credit_score": 724, "income": 111398, "credit_limit": 32000},
                    "visualizations": [{"chart_type": "credit_distribution"}],
                    "insights": ["Good credit score", "Stable income", "Current credit limit: $32,000"],
                    "recommendations": ["Approve credit limit increase"],
                    "metadata": {"source": "credit_bureau"}
                },
                "step_003": {
                    "step_id": "step_003",
                    "step_title": "Risk Assessment",
                    "execution_time": 30.1,
                    "status": "completed",
                    "data": {"risk_score": 25, "risk_level": "low"},
                    "visualizations": [{"chart_type": "risk_matrix"}],
                    "insights": ["Low risk customer", "Strong payment history"],
                    "recommendations": ["Approve with standard terms"],
                    "metadata": {"source": "risk_analysis"}
                },
                "decision": {
                    "decision": "approved",
                    "approved_amount": 5000,
                    "current_credit_limit": 32000,
                    "reason": "Strong credit profile with excellent payment history",
                    "decision_date": datetime.now().isoformat()
                }
            },
            progress=100.0
        )
        
        # Sample execution 1 - Completed
        sample_execution_1 = InvestigationExecution(
            executionId="sample_001",
            customerId=1001,
            customerName="John Smith",
            status=InvestigationExecutionStatus.COMPLETED,
            startedAt=datetime.now() - timedelta(hours=2),
            completedAt=datetime.now() - timedelta(hours=1, minutes=30),
            selectedSteps=[{"step": "customer_verification"}, {"step": "data_analysis"}],
            results={
                "step_001": {
                    "step_id": "step_001",
                    "step_title": "Customer Verification",
                    "execution_time": 15.5,
                    "status": "completed",
                    "data": {"customer_id": "CUST001", "verification_status": "verified"},
                    "visualizations": [{"chart_type": "status_pie"}],
                    "insights": ["Customer identity verified successfully"],
                    "recommendations": ["Proceed with credit analysis"],
                    "metadata": {"source": "internal_banking"}
                },
                "step_002": {
                    "step_id": "step_002",
                    "step_title": "Data Analysis",
                    "execution_time": 45.2,
                    "status": "completed",
                    "data": {"credit_score": 750, "income": 85000},
                    "visualizations": [{"chart_type": "credit_distribution"}],
                    "insights": ["Good credit score", "Stable income"],
                    "recommendations": ["Approve credit limit increase"],
                    "metadata": {"source": "credit_bureau"}
                }
            },
            progress=100.0
        )
        
        # Sample execution 2 - Running
        sample_execution_2 = InvestigationExecution(
            executionId="sample_002",
            customerId=1002,
            customerName="Sarah Johnson",
            status=InvestigationExecutionStatus.RUNNING,
            startedAt=datetime.now() - timedelta(minutes=30),
            completedAt=None,
            selectedSteps=[{"step": "customer_verification"}, {"step": "data_analysis"}, {"step": "risk_assessment"}],
            results={
                "step_001": {
                    "step_id": "step_001",
                    "step_title": "Customer Verification",
                    "execution_time": 12.3,
                    "status": "completed",
                    "data": {"customer_id": "CUST002", "verification_status": "verified"},
                    "visualizations": [{"chart_type": "status_pie"}],
                    "insights": ["Customer identity verified"],
                    "recommendations": ["Continue with analysis"],
                    "metadata": {"source": "internal_banking"}
                }
            },
            progress=33.0
        )
        
        # Sample execution 3 - Failed
        sample_execution_3 = InvestigationExecution(
            executionId="sample_003",
            customerId=1003,
            customerName="Mike Wilson",
            status=InvestigationExecutionStatus.FAILED,
            startedAt=datetime.now() - timedelta(hours=4),
            completedAt=datetime.now() - timedelta(hours=3, minutes=45),
            selectedSteps=[{"step": "customer_verification"}],
            results={},
            progress=0.0
        )
        
        self._add_execution(real_session)
        self._add_execution(sample_execution_1)
        self._add_execution(sample_execution_2)
        self._add_execution(sample_execution_3)

# Global instance
investigation_service = InvestigationService()
