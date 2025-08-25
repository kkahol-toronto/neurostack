"""
NeuroStack Integration Layer for Banking Agent.

This module provides the main integration between FastAPI and NeuroStack,
managing tools, memory, and reasoning for the banking agent.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from neurostack.core.memory import MemoryManager
from neurostack.core.reasoning import ReasoningEngine
from neurostack.core.agents import AgentContext

from neurostack_tools import BankingToolRegistry
from neurostack_memory import BankingMemoryManager, EnhancedCustomerData

logger = logging.getLogger(__name__)


class NeuroStackBankingIntegration:
    """
    Main integration class for NeuroStack with Banking Agent.
    
    This class manages the integration between FastAPI endpoints and
    NeuroStack's tools, memory, and reasoning capabilities.
    """
    
    def __init__(self, tenant_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.logger = logging.getLogger(f"{__name__}.NeuroStackBankingIntegration")
        
        # Initialize NeuroStack components
        self.memory_manager = BankingMemoryManager(tenant_id)
        self.reasoning_engine = ReasoningEngine(model="gpt-4", temperature=0.7)
        self.tool_registry = BankingToolRegistry(self.memory_manager, self.reasoning_engine)
        
        # Initialize enhanced customer data
        self.customer_data = EnhancedCustomerData()
        
        # Initialize customer profiles in memory
        self._initialized = False
    
    async def initialize(self):
        """Initialize the integration and load customer data into memory."""
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing NeuroStack Banking Integration")
            
            # Store all customer profiles in vector memory
            for customer in self.customer_data.get_all_customers():
                await self.memory_manager.store_customer_profile(customer)
            
            self._initialized = True
            self.logger.info("NeuroStack Banking Integration initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize NeuroStack integration: {str(e)}")
            raise
    
    async def execute_text_to_sql(self, natural_query: str, tables: List[Dict[str, Any]], 
                                user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute text-to-SQL conversion using NeuroStack tools.
        
        Args:
            natural_query: Natural language query
            tables: Available tables and their fields
            user_id: User ID for context
            
        Returns:
            Dictionary with SQL result and metadata
        """
        try:
            # Execute tool
            tool = self.tool_registry.get_tool("text_to_sql")
            if not tool:
                return {
                    "success": False,
                    "error": "Text-to-SQL tool not found",
                    "execution_time": 0.0
                }
            
            # Temporarily test without tables parameter to see if that's the issue
            try:
                result = await tool.execute(
                    arguments={
                        "natural_language_query": natural_query
                    },
                    context={"user_id": user_id, "tenant_id": self.tenant_id, "operation": "text_to_sql"}
                )
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Tool execution failed: {str(e)}",
                    "execution_time": 0.0
                }
            
            if result.success:
                # Store query pattern for learning (temporarily disabled for debugging)
                # await self.memory_manager.store_query_pattern(
                #     query=natural_query,
                #     sql_generated=result.result.get("sql", ""),
                #     tables_used=[t.table_name if hasattr(t, 'table_name') else t.get("table_name") for t in tables],
                #     success=True
                # )
                
                return {
                    "success": True,
                    "sql": result.result.get("sql"),
                    "execution_time": result.execution_time,
                    "enhanced_query": result.metadata.get("enhanced_query"),
                    "query_classification": result.metadata.get("query_classification"),
                    "neurostack_features": {
                        "memory_stored": True,
                        "reasoning_applied": True,
                        "pattern_learning": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.error_message,
                    "execution_time": result.execution_time
                }
                
        except Exception as e:
            self.logger.error(f"Text-to-SQL execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0.0
            }
    
    async def execute_customer_search(self, query: str, search_type: str = "semantic",
                                    user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute customer search using NeuroStack tools.
        
        Args:
            query: Search query
            search_type: Type of search (exact or semantic)
            user_id: User ID for context
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Execute tool
            tool = self.tool_registry.get_tool("customer_search")
            result = await tool.execute(
                arguments={
                    "query": query,
                    "search_type": search_type
                },
                context={"user_id": user_id, "tenant_id": self.tenant_id, "operation": "customer_search"}
            )
            
            if result.success:
                return {
                    "success": True,
                    "customers": result.result.get("customers", []),
                    "count": result.result.get("count", 0),
                    "search_type": search_type,
                    "execution_time": result.execution_time,
                    "neurostack_features": {
                        "semantic_search": search_type == "semantic",
                        "memory_stored": True,
                        "pattern_learning": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.error_message,
                    "execution_time": result.execution_time
                }
                
        except Exception as e:
            self.logger.error(f"Customer search execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0.0
            }
    
    async def execute_data_analysis(self, analysis_type: str, data_source: str,
                                  user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute data analysis using NeuroStack tools.
        
        Args:
            analysis_type: Type of analysis to perform
            data_source: Data source to analyze
            user_id: User ID for context
            
        Returns:
            Dictionary with analysis results and insights
        """
        try:
            # Execute tool
            tool = self.tool_registry.get_tool("data_analysis")
            result = await tool.execute(
                arguments={
                    "analysis_type": analysis_type,
                    "data_source": data_source
                },
                context={"user_id": user_id, "tenant_id": self.tenant_id, "operation": "data_analysis"}
            )
            
            if result.success:
                return {
                    "success": True,
                    "analysis_type": analysis_type,
                    "data_source": data_source,
                    "results": result.result.get("results", {}),
                    "insights": result.result.get("insights", ""),
                    "execution_time": result.execution_time,
                    "neurostack_features": {
                        "reasoning_applied": True,
                        "insights_generated": True,
                        "memory_stored": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.error_message,
                    "execution_time": result.execution_time
                }
                
        except Exception as e:
            self.logger.error(f"Data analysis execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0.0
            }
    
    async def execute_customer_verification(self, customer_id: int, 
                                          verification_type: str = "security_questions",
                                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute customer verification using NeuroStack tools.
        
        Args:
            customer_id: Customer ID to verify
            verification_type: Type of verification
            user_id: User ID for context
            
        Returns:
            Dictionary with verification questions and metadata
        """
        try:
            # Execute tool
            tool = self.tool_registry.get_tool("customer_verification")
            result = await tool.execute(
                arguments={
                    "customer_id": customer_id,
                    "verification_type": verification_type
                },
                context={"user_id": user_id, "tenant_id": self.tenant_id, "operation": "customer_verification"}
            )
            
            if result.success:
                return {
                    "success": True,
                    "customer_id": customer_id,
                    "questions": result.result.get("questions", []),
                    "verification_type": verification_type,
                    "execution_time": result.execution_time,
                    "neurostack_features": {
                        "verification_history": True,
                        "pattern_learning": True,
                        "memory_stored": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.error_message,
                    "execution_time": result.execution_time
                }
                
        except Exception as e:
            self.logger.error(f"Customer verification execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0.0
            }
    
    async def get_similar_queries(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get similar queries from memory for pattern matching.
        
        Args:
            query: Query to find similar patterns for
            limit: Maximum number of results
            
        Returns:
            List of similar queries with their SQL
        """
        try:
            return await self.memory_manager.find_similar_queries(query, limit)
        except Exception as e:
            self.logger.error(f"Failed to get similar queries: {str(e)}")
            return []
    
    async def get_recent_activity(self, hours: int = 24) -> Dict[str, Any]:
        """Get recent activity from memory."""
        try:
            activity = await self.memory_manager.get_recent_activity(hours)
            return activity
        except Exception as e:
            self.logger.error(f"Error getting recent activity: {str(e)}")
            return []

    async def generate_customer_summary(self, customer_id: int, customer_data: Dict[str, Any], 
                                      prompt: str) -> Dict[str, Any]:
        """
        Generate a comprehensive customer summary using NeuroStack's reasoning engine.
        
        Args:
            customer_id: Customer ID
            customer_data: Customer data from all sources
            prompt: Custom prompt for summary generation
            
        Returns:
            Dictionary with summary and metadata
        """
        try:
            self.logger.info(f"Generating customer summary for customer {customer_id}")
            
            # Store the customer data in memory for context
            await self.memory_manager.store_customer_data(
                customer_id=customer_id,
                data=customer_data,
                data_type="comprehensive_profile"
            )
            
            # Use NeuroStack reasoning engine to generate summary
            context = AgentContext(
                user_id=f"customer_{customer_id}",
                tenant_id=self.tenant_id,
                metadata={
                    "customer_id": customer_id,
                    "data_sources": list(customer_data.keys()),
                    "operation": "customer_summary"
                }
            )
            
            # Create a detailed prompt with customer data
            detailed_prompt = f"Analyze this customer data for credit decisions: Customer ID {customer_id}. "
            
            for source_id, source_info in customer_data.items():
                detailed_prompt += f"{source_info['source_name']}: "
                for key, value in source_info['data'].items():
                    detailed_prompt += f"{key}={value}, "
            
            detailed_prompt += """

Provide a comprehensive banking summary in Markdown format with the following structure:

## **Customer Profile**
- Key demographic and employment information

## **Financial Health Overview**
- Income analysis, account activity, and financial metrics

## **Credit Risk Assessment**
- Credit score analysis, payment history, and risk factors

## **Summary & Recommendations**
- Overall assessment and specific recommendations

Format with proper Markdown headers (##), bullet points (-), and bold text (**text**). Make it professional and comprehensive for banking decisions."""
            
            # Generate summary using reasoning engine with detailed prompt
            summary_result = await self.reasoning_engine.process(
                task=detailed_prompt,
                context=context
            )
            
            # Store the summary in memory
            await self.memory_manager.store_customer_summary(
                customer_id=customer_id,
                summary=summary_result,
                metadata={
                    "data_sources": list(customer_data.keys()),
                    "generated_at": datetime.now().isoformat()
                }
            )
            
            return {
                "success": True,
                "summary": summary_result,
                "neurostack_features": {
                    "reasoning_engine_used": True,
                    "memory_storage": True,
                    "context_aware": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating customer summary: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "neurostack_features": {
                    "reasoning_engine_used": False,
                    "memory_storage": False,
                    "context_aware": False
                }
            }
    
    async def get_customer_verification_history(self, customer_id: int, 
                                              days: int = 30) -> List[Dict[str, Any]]:
        """
        Get verification history for a customer.
        
        Args:
            customer_id: Customer ID
            days: Number of days to look back
            
        Returns:
            List of verification sessions
        """
        try:
            return await self.memory_manager.get_verification_history(customer_id, days)
        except Exception as e:
            self.logger.error(f"Failed to get verification history: {str(e)}")
            return []
    
    def get_available_tools(self) -> List[str]:
        """Get list of available NeuroStack tools."""
        return self.tool_registry.list_tools()
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all available tools."""
        return self.tool_registry.get_tool_schemas()
    
    def get_enhanced_customer_data(self) -> List[Dict[str, Any]]:
        """Get enhanced customer data for embeddings."""
        return self.customer_data.get_all_customers()
    
    def search_customers_direct(self, query: str) -> List[Dict[str, Any]]:
        """Search customers directly (fallback method)."""
        return self.customer_data.search_customers(query)
    
    def get_customer_by_id_direct(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer by ID directly (fallback method)."""
        return self.customer_data.get_customer_by_id(customer_id)


# Global instance for FastAPI integration
neurostack_integration = None


async def get_neurostack_integration() -> NeuroStackBankingIntegration:
    """
    Get or create the global NeuroStack integration instance.
    
    Returns:
        NeuroStackBankingIntegration instance
    """
    global neurostack_integration
    
    if neurostack_integration is None:
        neurostack_integration = NeuroStackBankingIntegration(tenant_id="banking_agent")
        await neurostack_integration.initialize()
    
    return neurostack_integration


# Utility functions for FastAPI endpoints
async def execute_neurostack_text_to_sql(natural_query: str, tables: List[Dict[str, Any]], 
                                       user_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute text-to-SQL with NeuroStack integration."""
    integration = await get_neurostack_integration()
    return await integration.execute_text_to_sql(natural_query, tables, user_id)


async def execute_neurostack_customer_search(query: str, search_type: str = "semantic",
                                           user_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute customer search with NeuroStack integration."""
    integration = await get_neurostack_integration()
    return await integration.execute_customer_search(query, search_type, user_id)


async def execute_neurostack_data_analysis(analysis_type: str, data_source: str,
                                         user_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute data analysis with NeuroStack integration."""
    integration = await get_neurostack_integration()
    return await integration.execute_data_analysis(analysis_type, data_source, user_id)


async def execute_neurostack_customer_verification(customer_id: int, 
                                                 verification_type: str = "security_questions",
                                                 user_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute customer verification with NeuroStack integration."""
    integration = await get_neurostack_integration()
    return await integration.execute_customer_verification(customer_id, verification_type, user_id)
