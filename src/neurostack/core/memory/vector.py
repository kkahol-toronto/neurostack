"""
Vector memory for semantic search.

This module provides vector-based storage and retrieval for semantic
search capabilities using embeddings.
"""

import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import numpy as np
import structlog
from pydantic import BaseModel

from .manager import MemoryItem

logger = structlog.get_logger(__name__)


class VectorItem(BaseModel):
    """A vector memory item with embedding."""
    id: UUID
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = {}
    timestamp: float
    tenant_id: Optional[str] = None


class VectorMemory:
    """
    Vector memory for semantic search.
    
    This class provides vector-based storage and retrieval using
    embeddings for semantic similarity search.
    """
    
    def __init__(self, tenant_id: Optional[str] = None, 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.tenant_id = tenant_id
        self.embedding_model = embedding_model
        self.logger = logger.bind(tenant_id=tenant_id, memory_type="vector")
        
        # Storage
        self._items: List[VectorItem] = []
        self._embeddings: List[List[float]] = []
        self._embedding_model = None
        
    @property
    def embedding_model_instance(self):
        """Get the embedding model instance."""
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer(self.embedding_model)
            except ImportError:
                self.logger.warning("sentence-transformers not available, using simple embeddings")
                self._embedding_model = SimpleEmbeddingModel()
        return self._embedding_model
    
    async def store(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> UUID:
        """
        Store content with its embedding.
        
        Args:
            content: The text content to store
            metadata: Optional metadata
            
        Returns:
            The ID of the stored item
        """
        item_id = uuid4()
        timestamp = time.time()
        
        # Generate embedding
        embedding = await self._get_embedding(content)
        
        item = VectorItem(
            id=item_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            timestamp=timestamp,
            tenant_id=self.tenant_id
        )
        
        self._items.append(item)
        self._embeddings.append(embedding)
        
        self.logger.debug("Vector item stored", item_id=str(item_id))
        return item_id
    
    async def search(self, query: str, limit: int = 5, 
                    threshold: float = 0.5) -> List[MemoryItem]:
        """
        Search for similar content.
        
        Args:
            query: The search query
            limit: Maximum number of results
            threshold: Similarity threshold
            
        Returns:
            List of similar memory items
        """
        if not self._items:
            return []
        
        # Generate query embedding
        query_embedding = await self._get_embedding(query)
        
        # Calculate similarities
        similarities = []
        for i, item_embedding in enumerate(self._embeddings):
            similarity = self._cosine_similarity(query_embedding, item_embedding)
            if similarity >= threshold:
                similarities.append((similarity, i))
        
        # Sort by similarity and take top results
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_indices = [idx for _, idx in similarities[:limit]]
        
        # Convert to MemoryItem format
        results = []
        for idx in top_indices:
            item = self._items[idx]
            memory_item = MemoryItem(
                id=item.id,
                content=item.content,
                memory_type="vector",
                timestamp=item.timestamp,
                metadata=item.metadata,
                tenant_id=item.tenant_id
            )
            results.append(memory_item)
        
        self.logger.debug("Vector search completed", 
                         query_length=len(query), 
                         results_count=len(results))
        return results
    
    async def search_by_metadata(self, metadata: Dict[str, Any], 
                               query: str = "", limit: int = 5) -> List[MemoryItem]:
        """
        Search by metadata with optional semantic filtering.
        
        Args:
            metadata: Metadata to match
            query: Optional semantic query
            limit: Maximum number of results
            
        Returns:
            List of matching memory items
        """
        # Filter by metadata first
        matching_items = []
        matching_indices = []
        
        for i, item in enumerate(self._items):
            if self._metadata_matches(item.metadata, metadata):
                matching_items.append(item)
                matching_indices.append(i)
        
        if not query or not matching_items:
            # Return metadata matches only
            results = []
            for item in matching_items[:limit]:
                memory_item = MemoryItem(
                    id=item.id,
                    content=item.content,
                    memory_type="vector",
                    timestamp=item.timestamp,
                    metadata=item.metadata,
                    tenant_id=item.tenant_id
                )
                results.append(memory_item)
            return results
        
        # Apply semantic search on filtered results
        query_embedding = await self._get_embedding(query)
        
        similarities = []
        for i, item in zip(matching_indices, matching_items):
            similarity = self._cosine_similarity(query_embedding, item.embedding)
            similarities.append((similarity, item))
        
        # Sort by similarity and take top results
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for _, item in similarities[:limit]:
            memory_item = MemoryItem(
                id=item.id,
                content=item.content,
                memory_type="vector",
                timestamp=item.timestamp,
                metadata=item.metadata,
                tenant_id=item.tenant_id
            )
            results.append(memory_item)
        
        return results
    
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
                del self._items[i]
                del self._embeddings[i]
                self.logger.debug("Vector item deleted", item_id=str(item_id))
                return True
        return False
    
    async def clear(self) -> None:
        """Clear all vector memory."""
        self._items.clear()
        self._embeddings.clear()
        self.logger.info("Vector memory cleared")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        metadata_counts = {}
        for item in self._items:
            for key in item.metadata.keys():
                metadata_counts[key] = metadata_counts.get(key, 0) + 1
        
        return {
            "total_items": len(self._items),
            "embedding_model": self.embedding_model,
            "embedding_dimension": len(self._embeddings[0]) if self._embeddings else 0,
            "metadata_keys": list(metadata_counts.keys()),
            "tenant_id": self.tenant_id
        }
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
        """
        try:
            model = self.embedding_model_instance
            if hasattr(model, 'encode'):
                # SentenceTransformer
                embedding = model.encode(text)
                return embedding.tolist()
            else:
                # Simple embedding model
                return model.encode(text)
        except Exception as e:
            self.logger.error("Failed to generate embedding", error=str(e))
            # Return zero vector as fallback
            return [0.0] * 384  # Default dimension
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            self.logger.error("Failed to calculate similarity", error=str(e))
            return 0.0
    
    def _metadata_matches(self, item_metadata: Dict[str, Any], 
                         query_metadata: Dict[str, Any]) -> bool:
        """
        Check if item metadata matches query metadata.
        
        Args:
            item_metadata: The item's metadata
            query_metadata: The query metadata
            
        Returns:
            True if metadata matches
        """
        for key, value in query_metadata.items():
            if key not in item_metadata or item_metadata[key] != value:
                return False
        return True


class SimpleEmbeddingModel:
    """
    Simple embedding model for fallback when sentence-transformers is not available.
    
    This provides basic hash-based embeddings for testing purposes.
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def encode(self, text: str) -> List[float]:
        """
        Generate a simple hash-based embedding.
        
        Args:
            text: The text to embed
            
        Returns:
            A simple embedding vector
        """
        import hashlib
        
        # Create a hash of the text
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float values
        embedding = []
        for i in range(self.dimension):
            byte_idx = i % len(hash_bytes)
            embedding.append(float(hash_bytes[byte_idx]) / 255.0)
        
        return embedding 