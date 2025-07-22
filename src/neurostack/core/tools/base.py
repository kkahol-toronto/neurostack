"""
Base tool classes and registry.

This module defines the core tool abstractions and registry for
managing tools that agents can use.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class ToolCall(BaseModel):
    """A tool call request."""
    id: UUID = Field(default_factory=uuid4)
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    caller_id: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: __import__("time").time())


class ToolResult(BaseModel):
    """Result of a tool execution."""
    id: UUID = Field(default_factory=uuid4)
    tool_name: str
    result: Any
    success: bool = True
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Tool(ABC):
    """
    Base class for all tools in the NeuroStack platform.
    
    Tools are capabilities that agents can use to interact with
    external systems or perform specific actions.
    """
    
    def __init__(self, name: str, description: str = "", 
                 required_permissions: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.required_permissions = required_permissions or []
        self.logger = logger.bind(tool_name=name)
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        Execute the tool with the given arguments.
        
        Args:
            arguments: The arguments for the tool
            context: Optional context for the execution
            
        Returns:
            The result of the tool execution
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for this tool.
        
        Returns:
            Dictionary describing the tool's interface
        """
        return {
            "name": self.name,
            "description": self.description,
            "required_permissions": self.required_permissions,
            "arguments_schema": self._get_arguments_schema()
        }
    
    @abstractmethod
    def _get_arguments_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the tool's arguments.
        
        Returns:
            Dictionary describing the expected arguments
        """
        pass


class SimpleTool(Tool):
    """
    A simple tool implementation for basic operations.
    
    This tool provides a basic implementation that can be extended
    for specific use cases.
    """
    
    def __init__(self, name: str, description: str = "", 
                 execute_func=None, arguments_schema: Optional[Dict[str, Any]] = None):
        super().__init__(name, description)
        self._execute_func = execute_func
        self._arguments_schema = arguments_schema or {}
    
    async def execute(self, arguments: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        Execute the tool.
        
        Args:
            arguments: The arguments for the tool
            context: Optional context for the execution
            
        Returns:
            The result of the tool execution
        """
        import time
        start_time = time.time()
        
        try:
            if self._execute_func:
                if context:
                    result = await self._execute_func(arguments, context)
                else:
                    result = await self._execute_func(arguments)
            else:
                result = f"Tool {self.name} executed with arguments: {arguments}"
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                tool_name=self.name,
                result=result,
                success=True,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error("Tool execution failed", error=str(e))
            
            return ToolResult(
                tool_name=self.name,
                result=None,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _get_arguments_schema(self) -> Dict[str, Any]:
        """Get the arguments schema."""
        return self._arguments_schema


class ToolRegistry:
    """
    Registry for managing tools.
    
    This class provides a centralized registry for tools that agents
    can discover and use.
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self.logger = logger.bind(component="tool_registry")
    
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool in the registry.
        
        Args:
            tool: The tool to register
        """
        self._tools[tool.name] = tool
        self.logger.info("Tool registered", tool_name=tool.name)
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            tool_name: The name of the tool to unregister
            
        Returns:
            True if tool was unregistered, False if not found
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            self.logger.info("Tool unregistered", tool_name=tool_name)
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: The name of the tool
            
        Returns:
            The tool instance or None if not found
        """
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """
        Get a list of all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """
        Get schemas for all registered tools.
        
        Returns:
            Dictionary mapping tool names to their schemas
        """
        return {name: tool.get_schema() for name, tool in self._tools.items()}
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any],
                          context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        Execute a tool by name.
        
        Args:
            tool_name: The name of the tool to execute
            arguments: The arguments for the tool
            context: Optional context for the execution
            
        Returns:
            The result of the tool execution
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                tool_name=tool_name,
                result=None,
                success=False,
                error_message=f"Tool '{tool_name}' not found"
            )
        
        return await tool.execute(arguments, context)
    
    def get_tools_by_permission(self, permissions: List[str]) -> List[Tool]:
        """
        Get tools that require the specified permissions.
        
        Args:
            permissions: List of permissions to check
            
        Returns:
            List of tools that require the specified permissions
        """
        matching_tools = []
        
        for tool in self._tools.values():
            if all(perm in permissions for perm in tool.required_permissions):
                matching_tools.append(tool)
        
        return matching_tools


# Built-in tools
class CalculatorTool(SimpleTool):
    """A simple calculator tool."""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform basic mathematical calculations",
            execute_func=self._calculate,
            arguments_schema={
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            }
        )
    
    async def _calculate(self, arguments: Dict[str, Any]) -> str:
        """Perform calculation."""
        expression = arguments.get("expression", "")
        
        try:
            # Simple evaluation (in production, use a safer method)
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"


class WebSearchTool(SimpleTool):
    """A web search tool."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information",
            execute_func=self._search,
            arguments_schema={
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            }
        )
    
    async def _search(self, arguments: Dict[str, Any]) -> str:
        """Perform web search."""
        query = arguments.get("query", "")
        return f"Search results for '{query}': [Mock results - implement actual search]"


class FileReadTool(SimpleTool):
    """A file reading tool."""
    
    def __init__(self):
        super().__init__(
            name="file_read",
            description="Read contents of a file",
            execute_func=self._read_file,
            arguments_schema={
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            }
        )
    
    async def _read_file(self, arguments: Dict[str, Any]) -> str:
        """Read file contents."""
        file_path = arguments.get("file_path", "")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return f"File contents: {content[:500]}..."  # Truncate for safety
        except Exception as e:
            return f"Error reading file: {str(e)}"


# Global tool registry instance
tool_registry = ToolRegistry()

# Register built-in tools
tool_registry.register_tool(CalculatorTool())
tool_registry.register_tool(WebSearchTool())
tool_registry.register_tool(FileReadTool()) 