"""
Base agent classes and interfaces.

This module defines the core agent abstractions that all agents
in the NeuroStack platform must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class AgentState(str, Enum):
    """Possible states of an agent."""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    description: str = ""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    tools: List[str] = field(default_factory=list)
    memory_enabled: bool = True
    reasoning_enabled: bool = True
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentContext(BaseModel):
    """Context passed to agents during execution."""
    session_id: UUID = Field(default_factory=uuid4)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    conversation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class AgentMessage(BaseModel):
    """Message passed between agents."""
    id: UUID = Field(default_factory=uuid4)
    sender: str
    recipient: str
    content: Any
    message_type: str = "task"
    priority: int = 0
    timestamp: float = Field(default_factory=lambda: __import__("time").time())
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class Agent(ABC):
    """
    Base class for all agents in the NeuroStack platform.
    
    This abstract class defines the interface that all agents must implement.
    Agents are autonomous entities that can reason, use tools, and communicate
    with other agents.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.state = AgentState.IDLE
        self.context: Optional[AgentContext] = None
        self.logger = logger.bind(agent_name=config.name)
        
        # Initialize components
        self._memory = None
        self._reasoning = None
        self._tools = []
        
    @property
    def name(self) -> str:
        """Get the agent's name."""
        return self.config.name
    
    @property
    def memory(self):
        """Get the agent's memory manager."""
        if self._memory is None and self.config.memory_enabled:
            from ..memory import MemoryManager
            self._memory = MemoryManager(self.config.tenant_id)
        return self._memory
    
    @property
    def reasoning(self):
        """Get the agent's reasoning engine."""
        if self._reasoning is None and self.config.reasoning_enabled:
            from ..reasoning import ReasoningEngine
            self._reasoning = ReasoningEngine(self.config.model)
        return self._reasoning
    
    @property
    def tools(self) -> List:
        """Get the agent's available tools."""
        return self._tools
    
    def add_tool(self, tool) -> None:
        """Add a tool to the agent's toolkit."""
        self._tools.append(tool)
        self.logger.info("Tool added", tool_name=tool.name)
    
    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the agent's toolkit."""
        self._tools = [t for t in self._tools if t.name != tool_name]
        self.logger.info("Tool removed", tool_name=tool_name)
    
    @abstractmethod
    async def execute(self, task: Any, context: Optional[AgentContext] = None) -> Any:
        """
        Execute a task with the given context.
        
        Args:
            task: The task to execute
            context: Optional context for the execution
            
        Returns:
            The result of the task execution
        """
        pass
    
    async def receive_message(self, message: AgentMessage) -> None:
        """
        Receive a message from another agent.
        
        Args:
            message: The message to receive
        """
        self.logger.info("Message received", 
                        sender=message.sender, 
                        message_type=message.message_type)
        
        # Store in memory if available
        if self.memory:
            await self.memory.store_message(message)
    
    async def send_message(self, recipient: str, content: Any, 
                          message_type: str = "task") -> AgentMessage:
        """
        Send a message to another agent.
        
        Args:
            recipient: The recipient agent's name
            content: The message content
            message_type: Type of message
            
        Returns:
            The created message
        """
        message = AgentMessage(
            sender=self.name,
            recipient=recipient,
            content=content,
            message_type=message_type
        )
        
        self.logger.info("Message sent", 
                        recipient=recipient, 
                        message_type=message_type)
        
        return message
    
    async def start(self) -> None:
        """Start the agent."""
        self.state = AgentState.IDLE
        self.logger.info("Agent started")
    
    async def stop(self) -> None:
        """Stop the agent."""
        self.state = AgentState.IDLE
        self.logger.info("Agent stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "name": self.name,
            "state": self.state.value,
            "tools_count": len(self.tools),
            "memory_enabled": self.config.memory_enabled,
            "reasoning_enabled": self.config.reasoning_enabled,
            "tenant_id": self.config.tenant_id,
        }


class SimpleAgent(Agent):
    """
    A simple agent implementation for basic tasks.
    
    This agent provides a basic implementation that can be extended
    for specific use cases.
    """
    
    async def execute(self, task: Any, context: Optional[AgentContext] = None) -> Any:
        """
        Execute a simple task.
        
        Args:
            task: The task to execute
            context: Optional context for the execution
            
        Returns:
            The result of the task execution
        """
        self.state = AgentState.RUNNING
        self.context = context or AgentContext()
        
        try:
            self.logger.info("Executing task", task_type=type(task).__name__)
            
            # Use reasoning engine if available
            if self.reasoning:
                result = await self.reasoning.process(task, self.context)
            else:
                result = f"Task completed: {task}"
            
            # Store result in memory if available
            if self.memory:
                await self.memory.store_result(task, result)
            
            self.state = AgentState.COMPLETED
            return result
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.logger.error("Task execution failed", error=str(e))
            raise 