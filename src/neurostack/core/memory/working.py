"""
Working memory for short-term storage.

This module provides in-memory storage for temporary data that agents
need to access quickly during their execution.
"""

import time
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import structlog
from pydantic import BaseModel

from .manager import MemoryItem

logger = structlog.get_logger(__name__)


class WorkingMemory:
    """
    Working memory for short-term storage.
    
    This class provides fast, in-memory storage for temporary data
    that agents need during their execution. Data is stored with
    timestamps and can be retrieved by type or metadata.
    """
    
    def __init__(self, tenant_id: Optional[str] = None, max_items: int = 1000):
        self.tenant_id = tenant_id
        self.max_items = max_items
        self.logger = logger.bind(tenant_id=tenant_id, memory_type="working")
        
        # In-memory storage
        self._items: List[MemoryItem] = []
        self._type_index: Dict[str, List[UUID]] = {}
        self._metadata_index: Dict[str, List[UUID]] = {}
        
    async def store(self, memory_type: str, content: Any, 
                   metadata: Optional[Dict[str, Any]] = None) -> UUID:
        """
        Store an item in working memory.
        
        Args:
            memory_type: Type of memory item
            content: The content to store
            metadata: Optional metadata
            
        Returns:
            The ID of the stored item
        """
        item_id = uuid4()
        timestamp = time.time()
        
        item = MemoryItem(
            id=item_id,
            content=content,
            memory_type=memory_type,
            timestamp=timestamp,
            metadata=metadata or {},
            tenant_id=self.tenant_id
        )
        
        # Add to main storage
        self._items.append(item)
        
        # Update type index
        if memory_type not in self._type_index:
            self._type_index[memory_type] = []
        self._type_index[memory_type].append(item_id)
        
        # Update metadata index
        if metadata:
            for key, value in metadata.items():
                index_key = f"{key}:{value}"
                if index_key not in self._metadata_index:
                    self._metadata_index[index_key] = []
                self._metadata_index[index_key].append(item_id)
        
        # Enforce size limit
        if len(self._items) > self.max_items:
            self._evict_oldest()
        
        self.logger.debug("Item stored", item_id=str(item_id), memory_type=memory_type)
        return item_id
    
    async def retrieve(self, item_id: UUID) -> Optional[MemoryItem]:
        """
        Retrieve an item by ID.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            The memory item or None if not found
        """
        for item in self._items:
            if item.id == item_id:
                return item
        return None
    
    async def retrieve_recent(self, limit: int = 10) -> List[MemoryItem]:
        """
        Retrieve the most recent items.
        
        Args:
            limit: Maximum number of items to retrieve
            
        Returns:
            List of recent memory items
        """
        sorted_items = sorted(self._items, key=lambda x: x.timestamp, reverse=True)
        return sorted_items[:limit]
    
    async def retrieve_by_type(self, memory_type: str, limit: int = 10) -> List[MemoryItem]:
        """
        Retrieve items by type.
        
        Args:
            memory_type: The type of items to retrieve
            limit: Maximum number of items to retrieve
            
        Returns:
            List of memory items of the specified type
        """
        if memory_type not in self._type_index:
            return []
        
        item_ids = self._type_index[memory_type][-limit:]
        items = []
        
        for item_id in item_ids:
            item = await self.retrieve(item_id)
            if item:
                items.append(item)
        
        return sorted(items, key=lambda x: x.timestamp, reverse=True)
    
    async def retrieve_by_metadata(self, metadata: Dict[str, Any], 
                                 limit: int = 10) -> List[MemoryItem]:
        """
        Retrieve items by metadata.
        
        Args:
            metadata: Metadata to match
            limit: Maximum number of items to retrieve
            
        Returns:
            List of memory items matching the metadata
        """
        matching_ids = set()
        
        for key, value in metadata.items():
            index_key = f"{key}:{value}"
            if index_key in self._metadata_index:
                if not matching_ids:
                    matching_ids = set(self._metadata_index[index_key])
                else:
                    matching_ids &= set(self._metadata_index[index_key])
        
        items = []
        for item_id in list(matching_ids)[:limit]:
            item = await self.retrieve(item_id)
            if item:
                items.append(item)
        
        return sorted(items, key=lambda x: x.timestamp, reverse=True)
    
    async def delete(self, item_id: UUID) -> bool:
        """
        Delete an item by ID.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            True if item was deleted, False if not found
        """
        for i, item in enumerate(self._items):
            if item.id == item_id:
                # Remove from main storage
                del self._items[i]
                
                # Remove from type index
                if item.memory_type in self._type_index:
                    self._type_index[item.memory_type] = [
                        mid for mid in self._type_index[item.memory_type] 
                        if mid != item_id
                    ]
                
                # Remove from metadata index
                for key, value in item.metadata.items():
                    index_key = f"{key}:{value}"
                    if index_key in self._metadata_index:
                        self._metadata_index[index_key] = [
                            mid for mid in self._metadata_index[index_key] 
                            if mid != item_id
                        ]
                
                self.logger.debug("Item deleted", item_id=str(item_id))
                return True
        
        return False
    
    async def clear(self) -> None:
        """Clear all items from working memory."""
        self._items.clear()
        self._type_index.clear()
        self._metadata_index.clear()
        self.logger.info("Working memory cleared")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get working memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        type_counts = {}
        for memory_type, item_ids in self._type_index.items():
            type_counts[memory_type] = len(item_ids)
        
        return {
            "total_items": len(self._items),
            "max_items": self.max_items,
            "type_counts": type_counts,
            "metadata_index_size": len(self._metadata_index),
            "tenant_id": self.tenant_id
        }
    
    def _evict_oldest(self) -> None:
        """Evict the oldest items to maintain size limit."""
        # Sort by timestamp and remove oldest items
        self._items.sort(key=lambda x: x.timestamp)
        items_to_remove = self._items[:len(self._items) - self.max_items]
        
        for item in items_to_remove:
            # Remove from type index
            if item.memory_type in self._type_index:
                self._type_index[item.memory_type] = [
                    mid for mid in self._type_index[item.memory_type] 
                    if mid != item.id
                ]
            
            # Remove from metadata index
            for key, value in item.metadata.items():
                index_key = f"{key}:{value}"
                if index_key in self._metadata_index:
                    self._metadata_index[index_key] = [
                        mid for mid in self._metadata_index[index_key] 
                        if mid != item.id
                    ]
        
        # Remove from main storage
        self._items = self._items[len(items_to_remove):]
        
        self.logger.debug("Evicted oldest items", count=len(items_to_remove)) 