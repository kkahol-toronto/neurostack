"""
NeuroStack Memory Integration for Banking Agent.

This module provides memory management for banking data sources,
including customer profiles, query patterns, and verification history.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import hashlib
import uuid

from neurostack.core.memory import MemoryManager, VectorMemory, WorkingMemory, LongTermMemory
from neurostack.core.agents import AgentContext

logger = logging.getLogger(__name__)


class BankingMemoryManager:
    """
    Enhanced memory manager for banking operations.
    
    This class extends NeuroStack's MemoryManager with banking-specific
    functionality for customer data, query patterns, and verification history.
    """
    
    def __init__(self, tenant_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.memory_manager = MemoryManager(tenant_id)
        self.logger = logging.getLogger(f"{__name__}.BankingMemoryManager")
        
        # Banking-specific memory caches
        self._customer_cache = {}
        self._query_patterns = {}
        self._verification_history = {}
        self._query_results = {}  # Store actual query results for learning
        
    async def store_customer_profile(self, customer_data: Dict[str, Any]) -> str:
        """
        Store customer profile in vector memory for semantic search.
        
        Args:
            customer_data: Customer demographic and financial data
            
        Returns:
            Memory item ID
        """
        try:
            # Create customer profile content for embedding
            profile_content = self._create_customer_profile_content(customer_data)
            
            # Generate customer embedding
            customer_id = customer_data.get("customer_id")
            
            # Store in vector memory for semantic search
            memory_id = await self.memory_manager.vector_memory.store(
                content=profile_content,
                metadata={
                    "customer_id": customer_id,
                    "first_name": customer_data.get("first_name"),
                    "last_name": customer_data.get("last_name"),
                    "state": customer_data.get("state"),
                    "annual_income": customer_data.get("annual_income"),
                    "employment_status": customer_data.get("employment_status"),
                    "customer_segment": customer_data.get("customer_segment"),
                    "memory_type": "customer_profile",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Cache in working memory for quick access
            await self.memory_manager.working_memory.store(
                f"customer_{customer_id}",
                {
                    "profile": customer_data,
                    "memory_id": memory_id,
                    "last_accessed": datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"Customer profile stored - customer_id: {customer_id}, memory_id: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store customer profile: {str(e)}")
            raise
    
    async def store_query_result(self, query_data: Dict[str, Any]) -> str:
        """
        Store query results for learning and pattern recognition.
        
        Args:
            query_data: Complete query data including results
            
        Returns:
            Memory item ID
        """
        try:
            # Store in working memory for quick access
            memory_id = str(uuid.uuid4())
            
            # Store in working memory
            await self.memory_manager.working_memory.store(
                "query_results",
                {
                    **query_data,
                    "memory_id": memory_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Store in vector memory for semantic search
            await self.memory_manager.vector_memory.store(
                content=query_data.get("query", ""),
                metadata={
                    "sql": query_data.get("sql", ""),
                    "result_count": query_data.get("result_count", 0),
                    "query_type": query_data.get("query_type", ""),
                    "success": query_data.get("success", False),
                    "memory_type": "query_result",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"Query result stored", 
                           query_type=query_data.get("query_type"),
                           result_count=query_data.get("result_count"))
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store query result: {str(e)}")
            raise
    
    async def search_customers_semantic(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search customers using semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching customers with similarity scores
        """
        try:
            # Search in vector memory
            results = await self.memory_manager.vector_memory.search(
                query=query,
                limit=limit,
                filter_metadata={"memory_type": "customer_profile"}
            )
            
            # Format results
            customers = []
            for result in results:
                customer_data = {
                    "customer_id": result.metadata.get("customer_id"),
                    "first_name": result.metadata.get("first_name"),
                    "last_name": result.metadata.get("last_name"),
                    "state": result.metadata.get("state"),
                    "annual_income": result.metadata.get("annual_income"),
                    "similarity_score": result.similarity_score,
                    "memory_id": result.id
                }
                customers.append(customer_data)
            
            # Store search pattern
            await self.memory_manager.working_memory.store(
                "search_pattern",
                {
                    "query": query,
                    "results_count": len(customers),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return customers
            
        except Exception as e:
            self.logger.error(f"Semantic customer search failed: {str(e)}")
            return []
    
    async def store_query_pattern(self, query: str, sql_generated: str, 
                                tables_used: List[str], success: bool) -> str:
        """
        Store query pattern for learning and optimization.
        
        Args:
            query: Natural language query
            sql_generated: Generated SQL
            tables_used: Tables used in the query
            success: Whether the query was successful
            
        Returns:
            Memory item ID
        """
        try:
            # Store in vector memory for pattern matching
            memory_id = await self.memory_manager.vector_memory.store(
                content=query,
                metadata={
                    "sql_generated": sql_generated,
                    "tables_used": tables_used,
                    "success": success,
                    "query_type": self._classify_query_type(query) if hasattr(self, '_classify_query_type') else "general_query",
                    "memory_type": "query_pattern",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Store in working memory for recent patterns
            await self.memory_manager.working_memory.store(
                "recent_query_patterns",
                {
                    "query": query,
                    "sql": sql_generated,
                    "tables": tables_used,
                    "success": success,
                    "memory_id": memory_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store query pattern: {str(e)}")
            raise
    
    async def find_similar_queries(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar queries for pattern matching.
        
        Args:
            query: Query to find similar patterns for
            limit: Maximum number of results
            
        Returns:
            List of similar queries with their SQL
        """
        try:
            # Mock search implementation
            results = []
            # In a real implementation, this would search vector memory
            
            similar_queries = []
            for result in results:
                similar_queries.append({
                    "query": result.content,
                    "sql": result.metadata.get("sql_generated"),
                    "tables_used": result.metadata.get("tables_used", []),
                    "success": result.metadata.get("success", False),
                    "similarity_score": result.similarity_score,
                    "query_type": result.metadata.get("query_type")
                })
            
            return similar_queries
            
        except Exception as e:
            self.logger.error(f"Failed to find similar queries: {str(e)}")
            return []
    
    async def _get_recent_memory_items(self, memory_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent memory items of a specific type."""
        try:
            # In a real implementation, this would query the working memory
            # For now, return mock data to demonstrate the concept
            return [
                {
                    "type": memory_type,
                    "timestamp": datetime.now().isoformat(),
                    "data": f"Mock {memory_type} data"
                }
            ]
        except Exception as e:
            self.logger.error(f"Error getting recent memory items: {str(e)}")
            return []
    
    async def store_verification_session(self, customer_id: int, 
                                       questions: List[Dict[str, Any]], 
                                       answers: List[str], 
                                       success: bool) -> str:
        """
        Store customer verification session.
        
        Args:
            customer_id: Customer being verified
            questions: Verification questions asked
            answers: Customer answers
            success: Whether verification was successful
            
        Returns:
            Memory item ID
        """
        try:
            # Store in long-term memory for audit trail (mock implementation)
            memory_id = str(uuid.uuid4())
            # In a real implementation, this would store in persistent storage
            
            # Store in working memory for recent verifications
            await self.memory_manager.working_memory.store(
                f"recent_verification_{customer_id}",
                {
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                    "memory_id": memory_id
                }
            )
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store verification session: {str(e)}")
            raise
    
    async def get_verification_history(self, customer_id: int, 
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
            # This would query long-term memory for verification history
            # For now, return mock data
            return [
                {
                    "session_id": str(uuid.uuid4()),
                    "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                    "success": True,
                    "questions_count": 2
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get verification history: {str(e)}")
            return []
    
    async def store_data_analysis_result(self, analysis_type: str, 
                                       data_source: str, 
                                       results: Dict[str, Any], 
                                       insights: str) -> str:
        """
        Store data analysis results for pattern learning.
        
        Args:
            analysis_type: Type of analysis performed
            data_source: Data source analyzed
            results: Analysis results
            insights: Generated insights
            
        Returns:
            Memory item ID
        """
        try:
            # Store in long-term memory (mock implementation)
            memory_id = str(uuid.uuid4())
            # In a real implementation, this would store in persistent storage
            
            # Store insights in vector memory for semantic search
            await self.memory_manager.vector_memory.store(
                content=insights,
                metadata={
                    "analysis_type": analysis_type,
                    "data_source": data_source,
                    "memory_type": "analysis_insights",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis result: {str(e)}")
            raise
    
    async def get_recent_activity(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get recent activity across all memory types.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary of recent activities
        """
        try:
            # Get recent working memory items (mock implementation)
            recent_queries = []
            recent_searches = []
            recent_verifications = []
            
            return {
                "recent_queries": recent_queries,
                "recent_searches": recent_searches,
                "recent_verifications": recent_verifications,
                "summary": {
                    "total_queries": len(recent_queries),
                    "total_searches": len(recent_searches),
                    "total_verifications": len(recent_verifications)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get recent activity: {str(e)}")
            return {}
    
    def _create_customer_profile_content(self, customer_data: Dict[str, Any]) -> str:
        """Create content string for customer profile embedding."""
        return f"""
        Customer Profile: {customer_data.get('first_name')} {customer_data.get('last_name')}
        ID: {customer_data.get('customer_id')}
        State: {customer_data.get('state')}
        Annual Income: ${customer_data.get('annual_income')}
        Employment: {customer_data.get('employment_status')}
        Segment: {customer_data.get('customer_segment')}
        Address: {customer_data.get('address', 'N/A')}
        Phone: {customer_data.get('phone', 'N/A')}
        Email: {customer_data.get('email', 'N/A')}
        """
    
    def _classify_query_type(self, query: str) -> str:
        """Classify query type for pattern learning."""
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
    
    # Convenience methods for accessing underlying memory managers
    @property
    def working_memory(self):
        return self.memory_manager.working_memory
    
    @property
    def vector_memory(self):
        return self.memory_manager.vector_memory
    
    @property
    def long_term_memory(self):
        return self.memory_manager.long_term_memory

    async def store_verification_result(self, customer_id: int, verification_data: Dict[str, Any]) -> str:
        """Store customer verification results."""
        try:
            memory_id = await self.memory_manager.long_term_memory.store(
                content=json.dumps(verification_data),
                metadata={
                    "customer_id": customer_id,
                    "verification_type": verification_data.get("type"),
                    "result": verification_data.get("result"),
                    "timestamp": datetime.now().isoformat(),
                    "memory_type": "verification_result"
                }
            )
            
            # Cache in working memory
            await self.memory_manager.working_memory.store(
                f"verification_{customer_id}_{datetime.now().timestamp()}",
                verification_data
            )
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store verification result: {str(e)}")
            raise

    async def store_customer_data(self, customer_id: int, data: Dict[str, Any], 
                                data_type: str = "comprehensive_profile") -> str:
        """
        Store comprehensive customer data from all sources.
        
        Args:
            customer_id: Customer ID
            data: Customer data from all sources
            data_type: Type of data being stored
            
        Returns:
            Memory item ID
        """
        try:
            # Store in long-term memory
            memory_id = await self.memory_manager.long_term_memory.store(
                content=json.dumps(data),
                metadata={
                    "customer_id": customer_id,
                    "data_type": data_type,
                    "sources_count": len(data),
                    "timestamp": datetime.now().isoformat(),
                    "memory_type": "customer_data"
                }
            )
            
            # Cache in working memory for quick access
            await self.memory_manager.working_memory.store(
                f"customer_data_{customer_id}",
                {
                    "data": data,
                    "memory_id": memory_id,
                    "last_accessed": datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"Customer data stored - customer_id: {customer_id}, memory_id: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store customer data: {str(e)}")
            raise

    async def store_customer_summary(self, customer_id: int, summary: str, 
                                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store customer summary generated by LLM.
        
        Args:
            customer_id: Customer ID
            summary: LLM-generated summary
            metadata: Additional metadata
            
        Returns:
            Memory item ID
        """
        try:
            # Store in long-term memory
            memory_id = await self.memory_manager.long_term_memory.store(
                content=summary,
                metadata={
                    "customer_id": customer_id,
                    "summary_type": "llm_generated",
                    "timestamp": datetime.now().isoformat(),
                    "memory_type": "customer_summary",
                    **(metadata or {})
                }
            )
            
            # Cache in working memory
            await self.memory_manager.working_memory.store(
                f"customer_summary_{customer_id}",
                {
                    "summary": summary,
                    "memory_id": memory_id,
                    "last_accessed": datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"Customer summary stored - customer_id: {customer_id}, memory_id: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store customer summary: {str(e)}")
            raise


class EnhancedCustomerData:
    """
    Enhanced customer data with additional fields for better embeddings.
    
    This class provides comprehensive customer data that can be used
    for generating rich embeddings and semantic search.
    """
    
    def __init__(self):
        self.customers = self._generate_enhanced_customers()
    
    def _generate_enhanced_customers(self) -> List[Dict[str, Any]]:
        """Generate enhanced customer data with additional fields."""
        from faker import Faker
        fake = Faker()
        
        customers = []
        for i in range(1, 11):
            # Basic demographic data
            first_name = fake.first_name()
            last_name = fake.last_name()
            state = fake.state_abbr()
            annual_income = fake.random_int(min=30000, max=200000, step=5000)
            
            # Enhanced data for better embeddings
            customer = {
                "customer_id": i,
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d"),
                "annual_income": annual_income,
                "state": state,
                "employment_status": fake.random_element(["Full-time", "Part-time", "Self-employed", "Retired"]),
                "customer_segment": fake.random_element(["Premium", "Standard", "Basic", "VIP"]),
                "address": fake.address(),
                "phone": fake.phone_number(),
                "email": fake.email(),
                "ssn": fake.ssn(),
                
                # Additional fields for rich embeddings
                "occupation": fake.job(),
                "education_level": fake.random_element(["High School", "Bachelor's", "Master's", "PhD"]),
                "marital_status": fake.random_element(["Single", "Married", "Divorced", "Widowed"]),
                "number_of_dependents": fake.random_int(min=0, max=5),
                "home_ownership": fake.random_element(["Own", "Rent", "Mortgage"]),
                "credit_score": fake.random_int(min=300, max=850),
                "account_age_months": fake.random_int(min=1, max=120),
                "total_accounts": fake.random_int(min=1, max=10),
                "average_monthly_balance": fake.random_int(min=1000, max=50000),
                "transaction_frequency": fake.random_element(["Low", "Medium", "High"]),
                "preferred_contact_method": fake.random_element(["Email", "Phone", "SMS", "Mail"]),
                "loyalty_program_member": fake.boolean(),
                "online_banking_user": fake.boolean(),
                "mobile_app_user": fake.boolean(),
                "preferred_language": fake.random_element(["English", "Spanish", "French", "German"]),
                "timezone": fake.timezone(),
                "last_login_date": fake.date_time_this_year().isoformat(),
                "risk_profile": fake.random_element(["Conservative", "Moderate", "Aggressive"]),
                "investment_preferences": fake.random_elements(
                    ["Stocks", "Bonds", "Mutual Funds", "ETFs", "Real Estate", "Cryptocurrency"], 
                    unique=True, 
                    length=fake.random_int(min=1, max=4)
                ),
                "banking_goals": fake.random_elements(
                    ["Save for retirement", "Buy a home", "Start a business", "Travel", "Education"], 
                    unique=True, 
                    length=fake.random_int(min=1, max=3)
                ),
                "life_events": fake.random_elements(
                    ["Graduation", "Marriage", "Birth of child", "Job change", "Relocation"], 
                    unique=True, 
                    length=fake.random_int(min=0, max=3)
                ),
                "customer_satisfaction_score": fake.random_int(min=1, max=10),
                "support_tickets_last_year": fake.random_int(min=0, max=5),
                "product_holdings": fake.random_elements(
                    ["Checking Account", "Savings Account", "Credit Card", "Mortgage", "Personal Loan", "Investment Account"], 
                    unique=True, 
                    length=fake.random_int(min=2, max=5)
                )
            }
            customers.append(customer)
        
        return customers
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer by ID."""
        for customer in self.customers:
            if customer["customer_id"] == customer_id:
                return customer
        return None
    
    def search_customers(self, query: str) -> List[Dict[str, Any]]:
        """Search customers by name, address, phone, or email."""
        query_lower = query.lower()
        results = []
        
        for customer in self.customers:
            if (query_lower in customer["first_name"].lower() or
                query_lower in customer["last_name"].lower() or
                query_lower in customer["address"].lower() or
                query_lower in customer["phone"] or
                query_lower in customer["email"].lower()):
                results.append(customer)
        
        return results
    
    def get_all_customers(self) -> List[Dict[str, Any]]:
        """Get all customers."""
        return self.customers
