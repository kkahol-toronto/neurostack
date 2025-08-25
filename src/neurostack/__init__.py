"""
NeuroStack - Enterprise-grade agentic AI platform.

A flexible, modular library for building multi-agent systems with advanced
reasoning, memory, and orchestration capabilities.
"""

from .core.agents import Agent, AgentOrchestrator, AgentConfig, SimpleAgent, AgentContext, AgentMessage
from .core.memory import MemoryManager, VectorMemory, WorkingMemory
from .core.reasoning import ReasoningEngine
from .core.tools import Tool, ToolRegistry, ToolResult, ToolCall
from .core.protocols import MCPProtocol, A2AProtocol
from .integrations import AzureIntegration, GCPIntegration

__version__ = "0.1.0"
__all__ = [
    "Agent",
    "AgentOrchestrator",
    "AgentConfig", 
    "SimpleAgent",
    "AgentContext",
    "AgentMessage",
    "MemoryManager",
    "VectorMemory",
    "WorkingMemory",
    "ReasoningEngine",
    "Tool",
    "ToolRegistry",
    "ToolResult",
    "ToolCall",
    "MCPProtocol",
    "A2AProtocol",
    "AzureIntegration",
    "GCPIntegration",
] 