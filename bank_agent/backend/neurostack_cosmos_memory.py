"""
Enhanced NeuroStack Memory Layer with Azure Cosmos DB Integration

This module provides persistent memory storage, historical learning,
result analysis, and adaptive behavior for the banking agent.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Structured query result for analysis and learning."""
    query_id: str
    natural_query: str
    sql_generated: str
    result_count: int
    execution_time: float
    success: bool
    tables_used: List[str]
    query_type: str
    user_id: Optional[str]
    timestamp: datetime
    results_summary: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class QueryPattern:
    """Query pattern for learning and optimization."""
    pattern_id: str
    query_type: str
    common_phrases: List[str]
    table_combinations: List[List[str]]
    success_rate: float
    avg_execution_time: float
    usage_count: int
    last_used: datetime
    created_at: datetime


@dataclass
class UserBehavior:
    """User behavior patterns for adaptive optimization."""
    user_id: str
    preferred_query_types: List[str]
    common_tables: List[str]
    avg_query_complexity: float
    session_patterns: Dict[str, Any]
    last_activity: datetime
    total_queries: int


class CosmosDBMemoryManager:
    """
    Enhanced memory manager with Cosmos DB persistence,
    historical learning, and adaptive behavior.
    """
    
    def __init__(self, connection_string: str, database_name: str = "neurostack"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.database = None
        self.containers = {}
        
        # Initialize sentence transformer for semantic search
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize containers
        self._init_containers()
    
    def _init_containers(self):
        """Initialize Cosmos DB containers."""
        try:
            self.client = CosmosClient.from_connection_string(self.connection_string)
            self.database = self.client.get_database_client(self.database_name)
            
            # Create containers if they don't exist
            containers_config = {
                "query_results": PartitionKey(path="/query_type"),
                "query_patterns": PartitionKey(path="/query_type"),
                "user_behaviors": PartitionKey(path="/user_id"),
                "semantic_embeddings": PartitionKey(path="/embedding_type"),
                "query_analytics": PartitionKey(path="/analysis_type"),
                "investigation_executions": PartitionKey(path="/execution_id")
            }
            
            for container_name, partition_key in containers_config.items():
                try:
                    self.containers[container_name] = self.database.create_container_if_not_exists(
                        id=container_name,
                        partition_key=partition_key
                    )
                    logger.info(f"Container {container_name} initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize container {container_name}: {str(e)}")
                    # Create a mock container for fallback
                    self.containers[container_name] = MockContainer(container_name)
                    
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {str(e)}")
            # Fallback to mock containers
            self._init_mock_containers()
    
    def _init_mock_containers(self):
        """Initialize mock containers for fallback."""
        logger.warning("Using mock containers - no persistent storage")
        self.containers = {
            "query_results": MockContainer("query_results"),
            "query_patterns": MockContainer("query_patterns"),
            "user_behaviors": MockContainer("user_behaviors"),
            "semantic_embeddings": MockContainer("semantic_embeddings"),
            "query_analytics": MockContainer("query_analytics"),
            "investigation_executions": MockContainer("investigation_executions")
        }
    
    async def store_query_result(self, query_data: Dict[str, Any]) -> str:
        """
        Store query result with comprehensive analysis.
        
        Args:
            query_data: Complete query data including results
            
        Returns:
            Query result ID
        """
        try:
            query_id = str(uuid.uuid4())
            
            # Create structured query result
            query_result = QueryResult(
                query_id=query_id,
                natural_query=query_data.get("query", ""),
                sql_generated=query_data.get("sql", ""),
                result_count=query_data.get("result_count", 0),
                execution_time=query_data.get("execution_time", 0.0),
                success=query_data.get("success", False),
                tables_used=query_data.get("tables", []),
                query_type=query_data.get("query_type", "general"),
                user_id=query_data.get("user_id"),
                timestamp=datetime.now(),
                results_summary=self._analyze_results(query_data.get("data", [])),
                error_message=query_data.get("error")
            )
            
            # Store in Cosmos DB
            container = self.containers["query_results"]
            await container.create_item(asdict(query_result))
            
            # Update patterns and user behavior
            await self._update_query_patterns(query_result)
            await self._update_user_behavior(query_result)
            
            # Generate semantic embedding
            await self._store_semantic_embedding(query_result)
            
            logger.info(f"Query result stored successfully: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"Failed to store query result: {str(e)}")
            raise
    
    def _analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze query results for insights."""
        if not results:
            return {"empty_results": True}
        
        try:
            df = pd.DataFrame(results)
            
            analysis = {
                "total_rows": len(results),
                "columns": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
                "categorical_columns": df.select_dtypes(include=['object']).columns.tolist()
            }
            
            # Add statistical analysis for numeric columns
            if analysis["numeric_columns"]:
                analysis["statistics"] = df[analysis["numeric_columns"]].describe().to_dict()
            
            # Add value counts for categorical columns
            if analysis["categorical_columns"]:
                analysis["value_counts"] = {}
                for col in analysis["categorical_columns"][:5]:  # Limit to first 5 columns
                    analysis["value_counts"][col] = df[col].value_counts().head(10).to_dict()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze results: {str(e)}")
            return {"analysis_error": str(e)}
    
    async def _update_query_patterns(self, query_result: QueryResult):
        """Update query patterns based on new result."""
        try:
            # Find existing pattern or create new one
            pattern_id = f"pattern_{query_result.query_type}_{hash(tuple(query_result.tables_used))}"
            
            container = self.containers["query_patterns"]
            
            # Try to get existing pattern
            try:
                existing_pattern = await container.read_item(pattern_id, query_result.query_type)
                pattern = QueryPattern(**existing_pattern)
                
                # Update existing pattern
                pattern.usage_count += 1
                pattern.last_used = datetime.now()
                pattern.success_rate = (pattern.success_rate * (pattern.usage_count - 1) + 
                                      (1 if query_result.success else 0)) / pattern.usage_count
                pattern.avg_execution_time = (pattern.avg_execution_time * (pattern.usage_count - 1) + 
                                            query_result.execution_time) / pattern.usage_count
                
            except:
                # Create new pattern
                pattern = QueryPattern(
                    pattern_id=pattern_id,
                    query_type=query_result.query_type,
                    common_phrases=self._extract_common_phrases(query_result.natural_query),
                    table_combinations=[query_result.tables_used],
                    success_rate=1.0 if query_result.success else 0.0,
                    avg_execution_time=query_result.execution_time,
                    usage_count=1,
                    last_used=datetime.now(),
                    created_at=datetime.now()
                )
            
            # Store updated pattern
            await container.upsert_item(asdict(pattern))
            
        except Exception as e:
            logger.error(f"Failed to update query patterns: {str(e)}")
    
    def _extract_common_phrases(self, query: str) -> List[str]:
        """Extract common phrases from query for pattern matching."""
        # Simple phrase extraction - can be enhanced with NLP
        phrases = []
        query_lower = query.lower()
        
        # Common banking phrases
        banking_phrases = [
            "income", "salary", "credit", "risk", "customer", "account",
            "balance", "transaction", "loan", "payment", "transfer"
        ]
        
        for phrase in banking_phrases:
            if phrase in query_lower:
                phrases.append(phrase)
        
        return phrases
    
    async def _update_user_behavior(self, query_result: QueryResult):
        """Update user behavior patterns."""
        if not query_result.user_id:
            logger.warning("No user_id provided for behavior update")
            return
        
        try:
            container = self.containers["user_behaviors"]
            user_id = query_result.user_id
            
            logger.info(f"Updating user behavior for user_id: {user_id}")
            
            try:
                existing_behavior = await container.read_item(user_id, user_id)
                behavior = UserBehavior(**existing_behavior)
                logger.info(f"Found existing behavior for user {user_id}")
                
                # Update behavior
                behavior.total_queries += 1
                behavior.last_activity = datetime.now()
                
                # Update preferred query types
                if query_result.query_type not in behavior.preferred_query_types:
                    behavior.preferred_query_types.append(query_result.query_type)
                
                # Update common tables
                for table in query_result.tables_used:
                    if table not in behavior.common_tables:
                        behavior.common_tables.append(table)
                
                # Update average complexity (simple heuristic)
                complexity = len(query_result.natural_query.split()) + len(query_result.tables_used)
                behavior.avg_query_complexity = (behavior.avg_query_complexity * (behavior.total_queries - 1) + 
                                               complexity) / behavior.total_queries
                
            except Exception as e:
                logger.info(f"Creating new behavior for user {user_id}: {str(e)}")
                # Create new behavior
                behavior = UserBehavior(
                    user_id=user_id,
                    preferred_query_types=[query_result.query_type],
                    common_tables=query_result.tables_used,
                    avg_query_complexity=len(query_result.natural_query.split()) + len(query_result.tables_used),
                    session_patterns={},
                    last_activity=datetime.now(),
                    total_queries=1
                )
            
            await container.upsert_item(asdict(behavior))
            logger.info(f"Successfully updated user behavior for {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update user behavior: {str(e)}")
            logger.error(f"Query result details: user_id={query_result.user_id}, query_type={query_result.query_type}")
    
    async def _store_semantic_embedding(self, query_result: QueryResult):
        """Store semantic embedding for similarity search."""
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(query_result.natural_query)
            
            embedding_data = {
                "id": f"embedding_{query_result.query_id}",
                "query_id": query_result.query_id,
                "embedding_type": "query",
                "embedding": embedding.tolist(),
                "query_text": query_result.natural_query,
                "query_type": query_result.query_type,
                "timestamp": datetime.now().isoformat()
            }
            
            container = self.containers["semantic_embeddings"]
            await container.create_item(embedding_data)
            
        except Exception as e:
            logger.error(f"Failed to store semantic embedding: {str(e)}")
    
    async def get_similar_queries(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar queries using semantic search."""
        try:
            # Generate embedding for input query
            query_embedding = self.embedding_model.encode(query)
            
            # Get all embeddings (in production, use vector search)
            container = self.containers["semantic_embeddings"]
            embeddings = await container.read_all_items()
            
            # Calculate similarities
            similarities = []
            for embedding_data in embeddings:
                stored_embedding = np.array(embedding_data["embedding"])
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                similarities.append((similarity, embedding_data))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for similarity, embedding_data in similarities[:limit]:
                # Get the actual query result
                query_result = await self.get_query_result(embedding_data["query_id"])
                if query_result:
                    results.append({
                        "query": query_result["natural_query"],
                        "sql": query_result["sql_generated"],
                        "similarity": float(similarity),
                        "query_type": query_result["query_type"],
                        "success": query_result["success"]
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get similar queries: {str(e)}")
            return []
    
    async def get_query_result(self, query_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific query result by ID."""
        try:
            container = self.containers["query_results"]
            # Note: This is a simplified lookup - in production, you'd need proper indexing
            items = await container.read_all_items()
            for item in items:
                if item.get("query_id") == query_id:
                    return item
            return None
        except Exception as e:
            logger.error(f"Failed to get query result: {str(e)}")
            return None
    
    async def get_query_patterns(self, query_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get query patterns for learning and optimization."""
        try:
            container = self.containers["query_patterns"]
            
            if query_type:
                patterns = await container.read_all_items()
                return [p for p in patterns if p.get("query_type") == query_type]
            else:
                return await container.read_all_items()
                
        except Exception as e:
            logger.error(f"Failed to get query patterns: {str(e)}")
            return []
    
    async def get_user_behavior(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user behavior patterns."""
        try:
            container = self.containers["user_behaviors"]
            return await container.read_item(user_id, user_id)
        except Exception as e:
            logger.error(f"Failed to get user behavior: {str(e)}")
            return None
    
    async def get_query_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive query analytics."""
        try:
            container = self.containers["query_results"]
            all_results = await container.read_all_items()
            
            # Filter by time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_results = [
                r for r in all_results 
                if datetime.fromisoformat(r["timestamp"]) > cutoff_time
            ]
            
            if not recent_results:
                return {"message": "No recent queries found"}
            
            # Calculate analytics
            analytics = {
                "total_queries": len(recent_results),
                "success_rate": sum(1 for r in recent_results if r["success"]) / len(recent_results),
                "avg_execution_time": sum(r["execution_time"] for r in recent_results) / len(recent_results),
                "query_types": {},
                "most_used_tables": {},
                "user_activity": {}
            }
            
            # Query type distribution
            for result in recent_results:
                query_type = result.get("query_type", "unknown")
                analytics["query_types"][query_type] = analytics["query_types"].get(query_type, 0) + 1
            
            # Table usage
            for result in recent_results:
                for table in result.get("tables_used", []):
                    analytics["most_used_tables"][table] = analytics["most_used_tables"].get(table, 0) + 1
            
            # User activity
            for result in recent_results:
                user_id = result.get("user_id", "anonymous")
                analytics["user_activity"][user_id] = analytics["user_activity"].get(user_id, 0) + 1
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get query analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_optimization_suggestions(self, query: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get optimization suggestions based on historical patterns."""
        try:
            suggestions = []
            
            # Get similar successful queries
            similar_queries = await self.get_similar_queries(query, limit=3)
            successful_similar = [q for q in similar_queries if q["success"]]
            
            if successful_similar:
                suggestions.append({
                    "type": "similar_successful_query",
                    "message": f"Found {len(successful_similar)} similar successful queries",
                    "examples": successful_similar[:2]
                })
            
            # Get user-specific patterns
            if user_id:
                user_behavior = await self.get_user_behavior(user_id)
                if user_behavior:
                    suggestions.append({
                        "type": "user_preference",
                        "message": f"User prefers {user_behavior['preferred_query_types']} queries",
                        "recommendation": f"Consider using {user_behavior['preferred_query_types'][0]} style queries"
                    })
            
            # Get query type patterns
            query_type = self._classify_query_type(query)
            patterns = await self.get_query_patterns(query_type)
            
            if patterns:
                best_pattern = max(patterns, key=lambda p: p["success_rate"])
                if best_pattern["success_rate"] > 0.8:
                    suggestions.append({
                        "type": "high_success_pattern",
                        "message": f"High success rate pattern found for {query_type} queries",
                        "success_rate": best_pattern["success_rate"],
                        "avg_time": best_pattern["avg_execution_time"]
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get optimization suggestions: {str(e)}")
            return []
    
    def _classify_query_type(self, query: str) -> str:
        """Classify query type for pattern matching."""
        query_lower = query.lower()
        
        if "income" in query_lower or "salary" in query_lower:
            return "income_analysis"
        elif "credit" in query_lower or "risk" in query_lower:
            return "credit_analysis"
        elif "customer" in query_lower and "search" in query_lower:
            return "customer_search"
        elif "join" in query_lower or "multiple" in query_lower:
            return "multi_table"
        else:
            return "general_query"


class MockContainer:
    """Mock container for fallback when Cosmos DB is not available."""
    
    def __init__(self, name: str):
        self.name = name
        self.items = []
    
    async def create_item(self, item: Dict[str, Any]):
        """Mock create item."""
        item["id"] = item.get("id", str(uuid.uuid4()))
        self.items.append(item)
        return item
    
    async def upsert_item(self, item: Dict[str, Any]):
        """Mock upsert item."""
        item["id"] = item.get("id", str(uuid.uuid4()))
        # Remove existing item with same ID if exists
        self.items = [i for i in self.items if i.get("id") != item.get("id")]
        self.items.append(item)
        return item
    
    async def read_item(self, id: str, partition_key: str):
        """Mock read item."""
        for item in self.items:
            # For user behaviors, check both id and user_id
            if item.get("id") == id or item.get("user_id") == id:
                return item
        raise Exception("Item not found")
    
    async def read_all_items(self):
        """Mock read all items."""
        return self.items.copy()


# Global memory manager instance
cosmos_memory_manager = None


async def get_cosmos_memory_manager() -> CosmosDBMemoryManager:
    """Get or create the global Cosmos DB memory manager."""
    global cosmos_memory_manager
    
    if cosmos_memory_manager is None:
        connection_string = os.getenv("AZURE_COSMOS_DB_CONNECTION_STRING")
        database_name = os.getenv("AZURE_COSMOS_DB_DATABASE", "neurostack")
        
        if connection_string:
            cosmos_memory_manager = CosmosDBMemoryManager(connection_string, database_name)
            logger.info("Cosmos DB Memory Manager initialized successfully")
        else:
            logger.warning("No Cosmos DB connection string found - using mock memory manager")
            cosmos_memory_manager = CosmosDBMemoryManager("mock", "mock")
    
    return cosmos_memory_manager
