"""
NeuroStack Tools for Banking Agent Data Sources.

This module provides NeuroStack tool implementations for banking data operations,
including text-to-SQL conversion, customer search, and data analysis.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import time

from neurostack.core.tools import Tool, ToolResult
from neurostack.core.memory import MemoryManager
from neurostack.core.reasoning import ReasoningEngine
from neurostack_cosmos_memory import get_cosmos_memory_manager

logger = logging.getLogger(__name__)


class TextToSQLTool(Tool):
    """
    Tool for converting natural language queries to SQL.
    
    This tool uses Azure OpenAI to convert natural language queries into SQL
    and stores query patterns in NeuroStack memory for learning.
    """
    
    def __init__(self, memory_manager: MemoryManager, reasoning_engine: ReasoningEngine):
        super().__init__(
            name="text_to_sql",
            description="Convert natural language queries to SQL for banking data sources",
            required_permissions=["data_access", "sql_generation"]
        )
        self.memory_manager = memory_manager
        self.reasoning_engine = reasoning_engine
        self.logger = logging.getLogger(f"{__name__}.TextToSQLTool")
        
    async def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Execute text-to-SQL conversion with memory and reasoning."""
        start_time = time.time()
        
        try:
            natural_query = arguments.get("natural_language_query")
            tables = arguments.get("tables", [])
            
            if not natural_query:
                return ToolResult(
                    tool_name=self.name,
                    result=None,
                    success=False,
                    error_message="Natural language query is required",
                    execution_time=time.time() - start_time
                )
            
            # Get enhanced memory manager
            cosmos_memory = await get_cosmos_memory_manager()
            
            # Get historical patterns and optimization suggestions
            try:
                historical_patterns = await cosmos_memory.get_similar_queries(natural_query, limit=3)
                optimization_suggestions = await cosmos_memory.get_optimization_suggestions(
                    natural_query, 
                    context.get("user_id") if context else None
                )
            except Exception as e:
                self.logger.error(f"Failed to get historical patterns: {str(e)}")
                historical_patterns = []
                optimization_suggestions = []
            
            # Use reasoning engine with historical context (simplified for now)
            try:
                reasoning_prompt = f"""
                Enhance this banking query for better SQL generation.
                
                Current Query: {natural_query}
                
                Historical Context:
                {json.dumps(historical_patterns, indent=2)}
                
                Optimization Suggestions:
                {json.dumps(optimization_suggestions, indent=2)}
                
                Available Tables: {[t.table_name if hasattr(t, 'table_name') else t.get('table_name') for t in tables]}
                
                Please enhance the query considering successful patterns from history and optimization suggestions.
                """
                
                enhanced_query = await self.reasoning_engine.process(reasoning_prompt, context)
            except Exception as e:
                self.logger.error(f"Reasoning engine failed: {str(e)}")
                enhanced_query = natural_query  # Fallback to original query
            
            # Generate SQL using enhanced query
            sql_result = self._generate_sql(enhanced_query, tables)
            
            # Store comprehensive query result for learning
            query_data = {
                "query": natural_query,
                "sql": sql_result.get("sql"),
                "result_count": sql_result.get("result_count", 0),
                "tables": [t.table_name if hasattr(t, 'table_name') else t.get("table_name") for t in tables],
                "query_type": self._classify_query_type(natural_query),
                "success": sql_result.get("success", False),
                "execution_time": sql_result.get("execution_time", 0.0),
                "user_id": context.get("user_id") if context else None,
                "data": sql_result.get("data", []),
                "enhanced_query": enhanced_query,
                "historical_patterns": historical_patterns,
                "optimization_suggestions": optimization_suggestions
            }
            
            # Store in enhanced memory
            await cosmos_memory.store_query_result(query_data)
            
            return ToolResult(
                tool_name=self.name,
                result={
                    "success": sql_result.get("success", False),
                    "sql": sql_result.get("sql"),
                    "execution_time": sql_result.get("execution_time", 0.0),
                    "enhanced_query": enhanced_query,
                    "historical_patterns": historical_patterns,
                    "optimization_suggestions": optimization_suggestions
                },
                success=sql_result.get("success", False),
                error_message=sql_result.get("error"),
                execution_time=time.time() - start_time,
                metadata={
                    "enhanced_query": enhanced_query,
                    "query_classification": self._classify_query_type(natural_query),
                    "historical_learning": True,
                    "optimization_applied": True
                }
            )
            
            # Store query in memory for pattern learning (temporarily disabled)
            # await self.memory_manager.working_memory.store(
            #     "query_pattern",
            #     {
            #         "query": natural_query,
            #         "tables": [t.table_name if hasattr(t, 'table_name') else t.get("table_name") for t in tables],
            #         "timestamp": datetime.now().isoformat(),
            #         "user_id": context.get("user_id") if context else None
            #     }
            # )
            
            # Get historical query patterns for reasoning (temporarily disabled)
            # historical_patterns = await self._get_historical_query_patterns(natural_query)
            historical_patterns = "Historical patterns: Income queries typically use annual_income field with WHERE clause."
            
            # Use reasoning engine with historical context (temporarily disabled)
            # reasoning_prompt = f"""
            # Enhance this banking query for better SQL generation.
            # 
            # Current Query: {natural_query}
            # 
            # Historical Context:
            # {historical_patterns}
            # 
            # Available Tables: {[t.table_name if hasattr(t, 'table_name') else t.get('table_name') for t in tables]}
            # 
            # Please enhance the query considering successful patterns from history.
            # """
            # 
            # enhanced_query = await self.reasoning_engine.process(reasoning_prompt, context)
            
            # For now, use the original query
            enhanced_query = natural_query
            
            # Generate SQL (this would integrate with your existing Azure OpenAI logic)
            sql_result = self._generate_sql(enhanced_query, tables)
            
            # Store successful query pattern in vector memory (temporarily disabled)
            # if sql_result.get("success"):
            #     await self.memory_manager.vector_memory.store(
            #         content=natural_query,
            #         metadata={
            #             "sql_generated": sql_result.get("sql"),
            #             "tables_used": [t.table_name if hasattr(t, 'table_name') else t.get("table_name") for t in tables],
            #             "query_type": self._classify_query_type(natural_query),
            #             "success": True,
            #             "result_count": sql_result.get("result_count", 0),
            #             "execution_time": sql_result.get("execution_time", 0),
            #             "timestamp": datetime.now().isoformat()
            #     }
            #     
            #     # Store query results for learning
            #     await self.memory_manager.working_memory.store(
            #         "query_results",
            #         {
            #             "query": natural_query,
            #             "sql": sql_result.get("sql"),
            #             "results": sql_result.get("data", []),
            #             "result_count": sql_result.get("result_count", 0),
            #             "tables_used": [t.table_name if hasattr(t, 'table_name') else t.get("table_name") for t in tables],
            #             "query_type": self._classify_query_type(natural_query),
            #             "success": True,
            #             "timestamp": datetime.now().isoformat(),
            #             "user_id": context.get("user_id") if context else None
            #     }
            #     )
            
            return ToolResult(
                tool_name=self.name,
                result=sql_result,
                success=sql_result.get("success", False),
                error_message=sql_result.get("error"),
                execution_time=time.time() - start_time,
                metadata={
                    "enhanced_query": enhanced_query,
                    "query_classification": self._classify_query_type(natural_query)
                }
            )
            
        except Exception as e:
            logger.error(f"TextToSQL tool execution failed: {str(e)}")
            return ToolResult(
                tool_name=self.name,
                result=None,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _generate_sql(self, query: str, tables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SQL using Azure OpenAI (integrate with existing logic)."""
        # This would integrate with your existing Azure OpenAI logic
        # For now, return a mock result
        return {
            "success": True,
            "sql": f"SELECT * FROM customer_demographics WHERE query LIKE '%{query}%'",
            "execution_time": 0.5
        }
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query for pattern learning."""
        query_lower = query.lower()
        if "customer" in query_lower and "search" in query_lower:
            return "customer_search"
        elif "income" in query_lower or "salary" in query_lower:
            return "income_analysis"
        elif "credit" in query_lower or "risk" in query_lower:
            return "credit_analysis"
        elif "join" in query_lower or "multiple" in query_lower:
            return "multi_table"
        else:
            return "general_query"
    
    async def _get_historical_query_patterns(self, current_query: str) -> str:
        """Get historical query patterns for reasoning enhancement."""
        try:
            # For now, return a simple pattern since the working memory method doesn't exist yet
            return "Historical patterns: Income queries typically use annual_income field with WHERE clause."
            
        except Exception as e:
            self.logger.error(f"Error getting historical patterns: {str(e)}")
            return "Error retrieving historical patterns."
    
    def _get_arguments_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "natural_language_query": {
                    "type": "string",
                    "description": "Natural language query to convert to SQL"
                },
                "tables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string"},
                            "fields": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "description": "Available tables and their fields"
                }
            },
            "required": ["natural_language_query"]
        }


class CustomerSearchTool(Tool):
    """
    Tool for intelligent customer search with semantic capabilities.
    
    This tool provides enhanced customer search using NeuroStack memory
    for semantic search and pattern recognition.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        super().__init__(
            name="customer_search",
            description="Intelligent customer search with semantic capabilities",
            required_permissions=["customer_data_access"]
        )
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(f"{__name__}.CustomerSearchTool")
        
    async def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Execute intelligent customer search."""
        start_time = time.time()
        
        try:
            search_query = arguments.get("query")
            search_type = arguments.get("search_type", "semantic")
            
            if not search_query:
                return ToolResult(
                    tool_name=self.name,
                    result=None,
                    success=False,
                    error_message="Search query is required",
                    execution_time=time.time() - start_time
                )
            
            # Store search pattern in memory
            await self.memory_manager.working_memory.store(
                "search_pattern",
                {
                    "query": search_query,
                    "type": search_type,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": context.get("user_id") if context else None
                }
            )
            
            # Perform search based on type
            if search_type == "semantic":
                results = await self._semantic_search(search_query)
            else:
                results = await self._exact_search(search_query)
            
            # Store successful search in vector memory
            if results:
                await self.memory_manager.vector_memory.store(
                    content=search_query,
                    metadata={
                        "results_count": len(results),
                        "search_type": search_type,
                        "success": True
                    }
                )
            
            return ToolResult(
                tool_name=self.name,
                result={"customers": results, "count": len(results)},
                success=True,
                execution_time=time.time() - start_time,
                metadata={"search_type": search_type}
            )
            
        except Exception as e:
            logger.error(f"CustomerSearch tool execution failed: {str(e)}")
            return ToolResult(
                tool_name=self.name,
                result=None,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _semantic_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform semantic search using vector memory."""
        # Import the mock data from main.py
        from main import MOCK_DATABASES
        
        results = []
        query_lower = query.lower()
        
        # Search through customer demographics
        customers = MOCK_DATABASES.get('customer_demographics', [])
        
        for customer in customers:
            # Check if query matches first name, last name, or contains "john"
            first_name = customer.get('first_name', '').lower()
            last_name = customer.get('last_name', '').lower()
            
            if (query_lower in first_name or 
                query_lower in last_name or 
                'john' in query_lower and first_name == 'john'):
                
                results.append({
                    "customer_id": customer['customer_id'],
                    "first_name": customer['first_name'],
                    "last_name": customer['last_name'],
                    "annual_income": customer.get('annual_income'),
                    "state": customer.get('state'),
                    "similarity_score": 0.95 if query_lower == first_name else 0.85
                })
        
        # Sort by similarity score (highest first)
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results
    
    async def _exact_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform exact match search."""
        # Import the mock data from main.py
        from main import MOCK_DATABASES
        
        results = []
        query_lower = query.lower()
        
        # Search through customer demographics
        customers = MOCK_DATABASES.get('customer_demographics', [])
        
        for customer in customers:
            # Check for exact matches
            first_name = customer.get('first_name', '').lower()
            last_name = customer.get('last_name', '').lower()
            
            if (query_lower == first_name or 
                query_lower == last_name or 
                query_lower == f"{first_name} {last_name}"):
                
                results.append({
                    "customer_id": customer['customer_id'],
                    "first_name": customer['first_name'],
                    "last_name": customer['last_name'],
                    "annual_income": customer.get('annual_income'),
                    "state": customer.get('state'),
                    "similarity_score": 1.0
                })
        
        return results
    
    def _get_arguments_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for customers"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["exact", "semantic"],
                    "description": "Type of search to perform"
                }
            },
            "required": ["query"]
        }


class DataAnalysisTool(Tool):
    """
    Tool for analyzing customer data patterns and insights.
    
    This tool provides data analysis capabilities using NeuroStack reasoning
    and memory for pattern recognition and trend analysis.
    """
    
    def __init__(self, memory_manager: MemoryManager, reasoning_engine: ReasoningEngine):
        super().__init__(
            name="data_analysis",
            description="Analyze customer data patterns and generate insights",
            required_permissions=["data_analysis", "insights_generation"]
        )
        self.memory_manager = memory_manager
        self.reasoning_engine = reasoning_engine
        self.logger = logging.getLogger(f"{__name__}.DataAnalysisTool")
        
    async def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Execute data analysis with reasoning and memory."""
        start_time = time.time()
        
        try:
            analysis_type = arguments.get("analysis_type", "customer_patterns")
            data_source = arguments.get("data_source", "customer_demographics")
            
            # Store analysis request in memory
            await self.memory_manager.working_memory.store(
                "analysis_request",
                {
                    "type": analysis_type,
                    "data_source": data_source,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": context.get("user_id") if context else None
                }
            )
            
            # Perform analysis based on type
            if analysis_type == "customer_patterns":
                results = await self._analyze_customer_patterns(data_source)
            elif analysis_type == "income_distribution":
                results = await self._analyze_income_distribution(data_source)
            elif analysis_type == "credit_risk_patterns":
                results = await self._analyze_credit_risk(data_source)
            else:
                results = await self._general_analysis(data_source, analysis_type)
            
            # Use reasoning engine to generate insights
            insights = await self.reasoning_engine.process(
                f"Generate insights from this analysis: {json.dumps(results)}",
                context
            )
            
            # Store analysis results in long-term memory (mock implementation)
            # In a real implementation, this would store in persistent storage
            
            return ToolResult(
                tool_name=self.name,
                result={
                    "analysis_type": analysis_type,
                    "data_source": data_source,
                    "results": results,
                    "insights": insights
                },
                success=True,
                execution_time=time.time() - start_time,
                metadata={"analysis_type": analysis_type}
            )
            
        except Exception as e:
            logger.error(f"DataAnalysis tool execution failed: {str(e)}")
            return ToolResult(
                tool_name=self.name,
                result=None,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _analyze_customer_patterns(self, data_source: str) -> Dict[str, Any]:
        """Analyze customer demographic patterns."""
        return {
            "total_customers": 10,
            "age_distribution": {"18-25": 2, "26-35": 3, "36-50": 3, "50+": 2},
            "income_ranges": {"<50k": 2, "50k-100k": 5, "100k+": 3},
            "geographic_distribution": {"CA": 4, "NY": 3, "TX": 2, "FL": 1}
        }
    
    async def _analyze_income_distribution(self, data_source: str) -> Dict[str, Any]:
        """Analyze income distribution patterns."""
        return {
            "average_income": 75000,
            "median_income": 70000,
            "income_quartiles": {"Q1": 55000, "Q2": 70000, "Q3": 85000, "Q4": 120000},
            "high_income_customers": 3
        }
    
    async def _analyze_credit_risk(self, data_source: str) -> Dict[str, Any]:
        """Analyze credit risk patterns."""
        return {
            "average_credit_score": 720,
            "risk_distribution": {"low": 6, "medium": 3, "high": 1},
            "delinquency_rate": 0.1,
            "credit_utilization_avg": 0.35
        }
    
    async def _general_analysis(self, data_source: str, analysis_type: str) -> Dict[str, Any]:
        """Perform general analysis."""
        return {
            "data_source": data_source,
            "analysis_type": analysis_type,
            "summary": f"General analysis of {data_source} for {analysis_type}"
        }
    
    def _get_arguments_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "analysis_type": {
                    "type": "string",
                    "enum": ["customer_patterns", "income_distribution", "credit_risk_patterns"],
                    "description": "Type of analysis to perform"
                },
                "data_source": {
                    "type": "string",
                    "description": "Data source to analyze"
                }
            },
            "required": ["analysis_type"]
        }


class CustomerVerificationTool(Tool):
    """
    Tool for intelligent customer verification with memory learning.
    
    This tool enhances customer verification by learning from patterns
    and storing verification history in NeuroStack memory.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        super().__init__(
            name="customer_verification",
            description="Intelligent customer verification with pattern learning",
            required_permissions=["customer_verification"]
        )
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(f"{__name__}.CustomerVerificationTool")
        
    async def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Execute intelligent customer verification."""
        start_time = time.time()
        
        try:
            customer_id = arguments.get("customer_id")
            verification_type = arguments.get("verification_type", "security_questions")
            
            if not customer_id:
                return ToolResult(
                    tool_name=self.name,
                    result=None,
                    success=False,
                    error_message="Customer ID is required",
                    execution_time=time.time() - start_time
                )
            
            # Store verification attempt in memory
            await self.memory_manager.working_memory.store(
                "verification_attempt",
                {
                    "customer_id": customer_id,
                    "type": verification_type,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": context.get("user_id") if context else None
                }
            )
            
            # Generate verification questions
            questions = await self._generate_verification_questions(customer_id, verification_type)
            
            # Store verification session in long-term memory (mock implementation)
            # In a real implementation, this would store in persistent storage
            
            return ToolResult(
                tool_name=self.name,
                result={
                    "customer_id": customer_id,
                    "questions": questions,
                    "verification_type": verification_type
                },
                success=True,
                execution_time=time.time() - start_time,
                metadata={"verification_type": verification_type}
            )
            
        except Exception as e:
            logger.error(f"CustomerVerification tool execution failed: {str(e)}")
            return ToolResult(
                tool_name=self.name,
                result=None,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _generate_verification_questions(self, customer_id: int, verification_type: str) -> List[Dict[str, Any]]:
        """Generate verification questions based on customer data."""
        # This would integrate with your existing verification logic
        return [
            {
                "question": "What is your customer ID?",
                "answer": str(customer_id),
                "type": "exact_match"
            },
            {
                "question": "What state do you live in?",
                "answer": "CA",  # This would come from customer data
                "type": "exact_match"
            }
        ]
    
    def _get_arguments_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "Customer ID to verify"
                },
                "verification_type": {
                    "type": "string",
                    "enum": ["security_questions", "document_verification", "biometric"],
                    "description": "Type of verification to perform"
                }
            },
            "required": ["customer_id"]
        }


# Tool Registry for Banking Agent
class BankingToolRegistry:
    """Registry for all banking-related NeuroStack tools."""
    
    def __init__(self, memory_manager: MemoryManager, reasoning_engine: ReasoningEngine):
        self.memory_manager = memory_manager
        self.reasoning_engine = reasoning_engine
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all banking tools."""
        self.tools["text_to_sql"] = TextToSQLTool(self.memory_manager, self.reasoning_engine)
        self.tools["customer_search"] = CustomerSearchTool(self.memory_manager)
        self.tools["data_analysis"] = DataAnalysisTool(self.memory_manager, self.reasoning_engine)
        self.tools["customer_verification"] = CustomerVerificationTool(self.memory_manager)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all available tools."""
        return list(self.tools.keys())
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all tools."""
        return {name: tool.get_schema() for name, tool in self.tools.items()}
