"""
Agent-to-Agent (A2A) protocol implementation.

This module provides A2A protocol support for agent communication
and coordination.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import structlog
from pydantic import BaseModel, Field

from ..agents.base import AgentMessage

logger = structlog.get_logger(__name__)


class A2AMessage(BaseModel):
    """A2A message structure."""
    id: UUID = Field(default_factory=uuid4)
    sender: str
    recipient: str
    message_type: str
    content: Any
    priority: int = 0
    timestamp: float = Field(default_factory=lambda: __import__("time").time())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class A2ARequest(BaseModel):
    """A2A request structure."""
    id: UUID = Field(default_factory=uuid4)
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    sender: str
    recipient: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class A2AResponse(BaseModel):
    """A2A response structure."""
    id: UUID
    request_id: UUID
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class A2AProtocol:
    """
    Agent-to-Agent protocol implementation.
    
    This class provides A2A protocol support for agent communication
    and coordination as specified in the protocol.
    """
    
    def __init__(self):
        self.logger = logger.bind(protocol="a2a")
        self._agents: Dict[str, Any] = {}
        self._message_handlers: Dict[str, callable] = {}
        self._request_handlers: Dict[str, callable] = {}
    
    def register_agent(self, agent_id: str, agent: Any) -> None:
        """
        Register an agent with the A2A protocol.
        
        Args:
            agent_id: The agent ID
            agent: The agent instance
        """
        self._agents[agent_id] = agent
        self.logger.info("Agent registered", agent_id=agent_id)
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the A2A protocol.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            True if agent was unregistered, False if not found
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            self.logger.info("Agent unregistered", agent_id=agent_id)
            return True
        return False
    
    def register_message_handler(self, message_type: str, handler: callable) -> None:
        """
        Register a message handler.
        
        Args:
            message_type: The type of message to handle
            handler: The handler function
        """
        self._message_handlers[message_type] = handler
        self.logger.info("Message handler registered", message_type=message_type)
    
    def register_request_handler(self, method: str, handler: callable) -> None:
        """
        Register a request handler.
        
        Args:
            method: The method to handle
            handler: The handler function
        """
        self._request_handlers[method] = handler
        self.logger.info("Request handler registered", method=method)
    
    async def send_message(self, message: A2AMessage) -> bool:
        """
        Send a message to an agent.
        
        Args:
            message: The message to send
            
        Returns:
            True if message was sent successfully
        """
        try:
            recipient = self._agents.get(message.recipient)
            if not recipient:
                self.logger.warning("Recipient not found", recipient=message.recipient)
                return False
            
            # Convert to AgentMessage format
            agent_message = AgentMessage(
                sender=message.sender,
                recipient=message.recipient,
                content=message.content,
                message_type=message.message_type,
                priority=message.priority,
                timestamp=message.timestamp,
                metadata=message.metadata
            )
            
            # Send to recipient
            await recipient.receive_message(agent_message)
            
            self.logger.info("Message sent", 
                           sender=message.sender, 
                           recipient=message.recipient,
                           message_type=message.message_type)
            return True
            
        except Exception as e:
            self.logger.error("Failed to send message", error=str(e))
            return False
    
    async def broadcast_message(self, message: A2AMessage, 
                              exclude_sender: bool = True) -> List[str]:
        """
        Broadcast a message to all agents.
        
        Args:
            message: The message to broadcast
            exclude_sender: Whether to exclude the sender from broadcast
            
        Returns:
            List of agent IDs that received the message
        """
        recipients = []
        
        for agent_id in self._agents.keys():
            if exclude_sender and agent_id == message.sender:
                continue
            
            message_copy = A2AMessage(
                sender=message.sender,
                recipient=agent_id,
                message_type=message.message_type,
                content=message.content,
                priority=message.priority,
                timestamp=message.timestamp,
                metadata=message.metadata
            )
            
            if await self.send_message(message_copy):
                recipients.append(agent_id)
        
        self.logger.info("Message broadcasted", 
                        sender=message.sender, 
                        recipients_count=len(recipients))
        return recipients
    
    async def handle_request(self, request: A2ARequest) -> A2AResponse:
        """
        Handle an A2A request.
        
        Args:
            request: The request to handle
            
        Returns:
            The response to the request
        """
        try:
            handler = self._request_handlers.get(request.method)
            if not handler:
                return A2AResponse(
                    id=uuid4(),
                    request_id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Method '{request.method}' not found"
                    }
                )
            
            result = await handler(request)
            
            return A2AResponse(
                id=uuid4(),
                request_id=request.id,
                result=result
            )
            
        except Exception as e:
            self.logger.error("A2A request handling failed", error=str(e))
            return A2AResponse(
                id=uuid4(),
                request_id=request.id,
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            )
    
    async def call_agent(self, agent_id: str, method: str, 
                        params: Dict[str, Any], caller_id: str) -> A2AResponse:
        """
        Call a method on an agent.
        
        Args:
            agent_id: The target agent ID
            method: The method to call
            params: The method parameters
            caller_id: The calling agent ID
            
        Returns:
            The response from the agent
        """
        request = A2ARequest(
            method=method,
            params=params,
            sender=caller_id,
            recipient=agent_id
        )
        
        # Send request to agent
        success = await self.send_message(A2AMessage(
            sender=caller_id,
            recipient=agent_id,
            message_type="request",
            content=request.dict()
        ))
        
        if not success:
            return A2AResponse(
                id=uuid4(),
                request_id=request.id,
                error={
                    "code": -32001,
                    "message": f"Agent '{agent_id}' not available"
                }
            )
        
        # For now, return a mock response
        # In a real implementation, this would wait for the agent's response
        return A2AResponse(
            id=uuid4(),
            request_id=request.id,
            result=f"Method '{method}' called on agent '{agent_id}'"
        )
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an agent.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Agent information or None if not found
        """
        agent = self._agents.get(agent_id)
        if not agent:
            return None
        
        return {
            "id": agent_id,
            "name": getattr(agent, 'name', agent_id),
            "capabilities": getattr(agent, 'capabilities', []),
            "status": getattr(agent, 'state', 'unknown').value if hasattr(agent, 'state') else 'unknown'
        }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent information
        """
        agents = []
        for agent_id in self._agents.keys():
            info = self.get_agent_info(agent_id)
            if info:
                agents.append(info)
        return agents
    
    def get_protocol_info(self) -> Dict[str, Any]:
        """
        Get protocol information.
        
        Returns:
            Dictionary with protocol information
        """
        return {
            "name": "agent-to-agent",
            "version": "1.0.0",
            "capabilities": {
                "messaging": True,
                "request_response": True,
                "broadcast": True,
                "agent_discovery": True
            },
            "registered_agents": len(self._agents),
            "message_handlers": len(self._message_handlers),
            "request_handlers": len(self._request_handlers)
        } 