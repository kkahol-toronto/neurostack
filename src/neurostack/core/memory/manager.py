"""
Memory manager for coordinating different memory types.

This module provides a unified interface for managing short-term
working memory, long-term storage, and vector-based semantic memory.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import structlog
from pydantic import BaseModel

from ..agents.base import AgentContext, AgentMessage

logger = structlog.get_logger(__name__)


class MemoryItem(BaseModel):
    """A memory item with metadata."""
    id: UUID
    content: Any
    memory_type: str
    timestamp: float
    metadata: Dict[str, Any] = {}
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None


class MemoryManager:
    """
    Unified memory manager for NeuroStack agents.
    
    This class coordinates different types of memory (working, long-term,
    vector) and provides a unified interface for storing and retrieving
    information.
    """
    
    def __init__(self, tenant_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.logger = logger.bind(tenant_id=tenant_id)
        
        # Initialize memory components
        self._working_memory = None
        self._vector_memory = None
        self._long_term_memory = None
        
    @property
    def working_memory(self):
        """Get the working memory instance."""
        if self._working_memory is None:
            from .working import WorkingMemory
            self._working_memory = WorkingMemory(self.tenant_id)
        return self._working_memory
    
    @property
    def vector_memory(self):
        """Get the vector memory instance."""
        if self._vector_memory is None:
            from .vector import VectorMemory
            self._vector_memory = VectorMemory(self.tenant_id)
        return self._vector_memory
    
    @property
    def long_term_memory(self):
        """Get the long-term memory instance."""
        if self._long_term_memory is None:
            from .long_term import LongTermMemory
            self._long_term_memory = LongTermMemory(self.tenant_id)
        return self._long_term_memory
    
    async def store_message(self, message: AgentMessage) -> None:
        """
        Store an agent message in memory.
        
        Args:
            message: The message to store
        """
        # Store in working memory for immediate access
        await self.working_memory.store("message", message)
        
        # Store in vector memory for semantic search
        await self.vector_memory.store(
            content=str(message.content),
            metadata={
                "message_id": str(message.id),
                "sender": message.sender,
                "recipient": message.recipient,
                "message_type": message.message_type,
                "timestamp": message.timestamp
            }
        )
        
        self.logger.info("Message stored", message_id=str(message.id))
    
    async def store_result(self, task: Any, result: Any) -> None:
        """
        Store a task result in memory.
        
        Args:
            task: The original task
            result: The result of the task
        """
        # Store in working memory
        await self.working_memory.store("task_result", {
            "task": task,
            "result": result
        })
        
        # Store in vector memory for semantic search
        await self.vector_memory.store(
            content=str(result),
            metadata={
                "task": str(task),
                "type": "task_result"
            }
        )
        
        self.logger.info("Task result stored")
    
    async def store_context(self, context: AgentContext) -> None:
        """
        Store agent context in memory.
        
        Args:
            context: The agent context
        """
        await self.working_memory.store("context", context)
        self.logger.info("Context stored", session_id=str(context.session_id))
    
    async def retrieve_recent(self, limit: int = 10) -> List[MemoryItem]:
        """
        Retrieve recent memory items.
        
        Args:
            limit: Maximum number of items to retrieve
            
        Returns:
            List of recent memory items
        """
        return await self.working_memory.retrieve_recent(limit)
    
    async def search_semantic(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """
        Search memory semantically.
        
        Args:
            query: The search query
            limit: Maximum number of results
            
        Returns:
            List of relevant memory items
        """
        return await self.vector_memory.search(query, limit)
    
    async def get_context(self) -> Optional[AgentContext]:
        """
        Get the current context.
        
        Returns:
            The current context or None
        """
        items = await self.working_memory.retrieve_by_type("context", limit=1)
        if items:
            return items[0].content
        return None
    
    async def get_conversation_history(self, conversation_id: str, 
                                     limit: int = 50) -> List[MemoryItem]:
        """
        Get conversation history.
        
        Args:
            conversation_id: The conversation ID
            limit: Maximum number of messages
            
        Returns:
            List of conversation messages
        """
        return await self.working_memory.retrieve_by_metadata(
            {"conversation_id": conversation_id}, limit
        )
    
    async def store_user_profile(self, user_id: str, profile: Dict[str, Any]) -> None:
        """
        Store user profile information.
        
        Args:
            user_id: The user ID
            profile: The profile data
        """
        await self.long_term_memory.store_user_profile(user_id, profile)
        self.logger.info("User profile stored", user_id=user_id)
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information.
        
        Args:
            user_id: The user ID
            
        Returns:
            The user profile or None
        """
        return await self.long_term_memory.get_user_profile(user_id)
    
    async def store_knowledge(self, content: str, metadata: Dict[str, Any]) -> None:
        """
        Store knowledge in long-term memory.
        
        Args:
            content: The knowledge content
            metadata: Additional metadata
        """
        # Store in vector memory for semantic search
        await self.vector_memory.store(content, metadata)
        
        # Store in long-term memory for persistence
        await self.long_term_memory.store_knowledge(content, metadata)
        
        self.logger.info("Knowledge stored")
    
    async def search_knowledge(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """
        Search stored knowledge.
        
        Args:
            query: The search query
            limit: Maximum number of results
            
        Returns:
            List of relevant knowledge items
        """
        return await self.vector_memory.search(query, limit)
    
    async def clear_working_memory(self) -> None:
        """Clear working memory."""
        await self.working_memory.clear()
        self.logger.info("Working memory cleared")
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        working_stats = await self.working_memory.get_stats()
        vector_stats = await self.vector_memory.get_stats()
        long_term_stats = await self.long_term_memory.get_stats()
        
        return {
            "working_memory": working_stats,
            "vector_memory": vector_stats,
            "long_term_memory": long_term_stats,
            "tenant_id": self.tenant_id
        } 