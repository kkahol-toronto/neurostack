"""
Long-term memory for persistent storage.

This module provides persistent storage for long-term memory including
user profiles, knowledge bases, and conversation history.
"""

import time
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import structlog
from pydantic import BaseModel

from .manager import MemoryItem

logger = structlog.get_logger(__name__)


class LongTermItem(BaseModel):
    """A long-term memory item."""
    id: UUID
    content: Any
    item_type: str
    timestamp: float
    metadata: Dict[str, Any] = {}
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None


class LongTermMemory:
    """
    Long-term memory for persistent storage.
    
    This class provides persistent storage for data that needs to be
    retained across sessions, such as user profiles and knowledge bases.
    """
    
    def __init__(self, tenant_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.logger = logger.bind(tenant_id=tenant_id, memory_type="long_term")
        
        # In-memory storage (in a real implementation, this would be a database)
        self._items: List[LongTermItem] = []
        self._user_profiles: Dict[str, Dict[str, Any]] = {}
        self._knowledge_base: List[LongTermItem] = []
        
    async def store_user_profile(self, user_id: str, profile: Dict[str, Any]) -> None:
        """
        Store user profile information.
        
        Args:
            user_id: The user ID
            profile: The profile data
        """
        self._user_profiles[user_id] = profile
        self.logger.info("User profile stored", user_id=user_id)
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information.
        
        Args:
            user_id: The user ID
            
        Returns:
            The user profile or None
        """
        return self._user_profiles.get(user_id)
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> None:
        """
        Update user profile information.
        
        Args:
            user_id: The user ID
            updates: The profile updates
        """
        if user_id in self._user_profiles:
            self._user_profiles[user_id].update(updates)
        else:
            self._user_profiles[user_id] = updates
        
        self.logger.info("User profile updated", user_id=user_id)
    
    async def delete_user_profile(self, user_id: str) -> bool:
        """
        Delete user profile.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if profile was deleted, False if not found
        """
        if user_id in self._user_profiles:
            del self._user_profiles[user_id]
            self.logger.info("User profile deleted", user_id=user_id)
            return True
        return False
    
    async def store_knowledge(self, content: str, metadata: Dict[str, Any]) -> UUID:
        """
        Store knowledge in the knowledge base.
        
        Args:
            content: The knowledge content
            metadata: Additional metadata
            
        Returns:
            The ID of the stored item
        """
        item_id = uuid4()
        timestamp = time.time()
        
        item = LongTermItem(
            id=item_id,
            content=content,
            item_type="knowledge",
            timestamp=timestamp,
            metadata=metadata,
            tenant_id=self.tenant_id
        )
        
        self._knowledge_base.append(item)
        self.logger.info("Knowledge stored", item_id=str(item_id))
        return item_id
    
    async def get_knowledge(self, item_id: UUID) -> Optional[LongTermItem]:
        """
        Get knowledge by ID.
        
        Args:
            item_id: The item ID
            
        Returns:
            The knowledge item or None
        """
        for item in self._knowledge_base:
            if item.id == item_id:
                return item
        return None
    
    async def search_knowledge(self, query: str, limit: int = 10) -> List[LongTermItem]:
        """
        Search knowledge base by content.
        
        Args:
            query: The search query
            limit: Maximum number of results
            
        Returns:
            List of matching knowledge items
        """
        # Simple text search (in a real implementation, this would use vector search)
        results = []
        query_lower = query.lower()
        
        for item in self._knowledge_base:
            if query_lower in str(item.content).lower():
                results.append(item)
                if len(results) >= limit:
                    break
        
        return results
    
    async def delete_knowledge(self, item_id: UUID) -> bool:
        """
        Delete knowledge by ID.
        
        Args:
            item_id: The item ID
            
        Returns:
            True if item was deleted, False if not found
        """
        for i, item in enumerate(self._knowledge_base):
            if item.id == item_id:
                del self._knowledge_base[i]
                self.logger.info("Knowledge deleted", item_id=str(item_id))
                return True
        return False
    
    async def store_conversation(self, conversation_id: str, 
                               messages: List[Dict[str, Any]]) -> None:
        """
        Store conversation history.
        
        Args:
            conversation_id: The conversation ID
            messages: List of conversation messages
        """
        timestamp = time.time()
        
        for message in messages:
            item = LongTermItem(
                id=uuid4(),
                content=message,
                item_type="conversation",
                timestamp=timestamp,
                metadata={"conversation_id": conversation_id},
                tenant_id=self.tenant_id
            )
            self._items.append(item)
        
        self.logger.info("Conversation stored", conversation_id=conversation_id)
    
    async def get_conversation(self, conversation_id: str) -> List[LongTermItem]:
        """
        Get conversation history.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            List of conversation messages
        """
        messages = []
        for item in self._items:
            if (item.item_type == "conversation" and 
                item.metadata.get("conversation_id") == conversation_id):
                messages.append(item)
        
        return sorted(messages, key=lambda x: x.timestamp)
    
    async def store_general(self, content: Any, item_type: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> UUID:
        """
        Store general data in long-term memory.
        
        Args:
            content: The content to store
            item_type: Type of the item
            metadata: Optional metadata
            
        Returns:
            The ID of the stored item
        """
        item_id = uuid4()
        timestamp = time.time()
        
        item = LongTermItem(
            id=item_id,
            content=content,
            item_type=item_type,
            timestamp=timestamp,
            metadata=metadata or {},
            tenant_id=self.tenant_id
        )
        
        self._items.append(item)
        self.logger.info("General item stored", item_id=str(item_id), item_type=item_type)
        return item_id
    
    async def get_by_type(self, item_type: str, limit: int = 10) -> List[LongTermItem]:
        """
        Get items by type.
        
        Args:
            item_type: The type of items to retrieve
            limit: Maximum number of items
            
        Returns:
            List of items of the specified type
        """
        items = []
        for item in self._items:
            if item.item_type == item_type:
                items.append(item)
                if len(items) >= limit:
                    break
        
        return sorted(items, key=lambda x: x.timestamp, reverse=True)
    
    async def clear(self) -> None:
        """Clear all long-term memory."""
        self._items.clear()
        self._user_profiles.clear()
        self._knowledge_base.clear()
        self.logger.info("Long-term memory cleared")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get long-term memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        type_counts = {}
        for item in self._items:
            type_counts[item.item_type] = type_counts.get(item.item_type, 0) + 1
        
        return {
            "total_items": len(self._items),
            "user_profiles": len(self._user_profiles),
            "knowledge_items": len(self._knowledge_base),
            "type_counts": type_counts,
            "tenant_id": self.tenant_id
        } 