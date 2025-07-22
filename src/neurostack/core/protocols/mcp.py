"""
Model Context Protocol (MCP) implementation.

This module provides MCP support for tool integration and
model context management.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class MCPRequest(BaseModel):
    """MCP request structure."""
    id: UUID = Field(default_factory=uuid4)
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    """MCP response structure."""
    id: UUID
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any] = Field(default_factory=dict)


class MCPProtocol:
    """
    Model Context Protocol implementation.
    
    This class provides MCP support for tool integration and
    model context management as specified in the protocol.
    """
    
    def __init__(self):
        self.logger = logger.bind(protocol="mcp")
        self._tools: Dict[str, MCPTool] = {}
        self._resources: Dict[str, Any] = {}
    
    def register_tool(self, tool: MCPTool) -> None:
        """
        Register an MCP tool.
        
        Args:
            tool: The MCP tool to register
        """
        self._tools[tool.name] = tool
        self.logger.info("MCP tool registered", tool_name=tool.name)
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister an MCP tool.
        
        Args:
            tool_name: The name of the tool to unregister
            
        Returns:
            True if tool was unregistered, False if not found
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            self.logger.info("MCP tool unregistered", tool_name=tool_name)
            return True
        return False
    
    def list_tools(self) -> List[MCPTool]:
        """
        List all registered MCP tools.
        
        Returns:
            List of registered MCP tools
        """
        return list(self._tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """
        Get an MCP tool by name.
        
        Args:
            tool_name: The name of the tool
            
        Returns:
            The MCP tool or None if not found
        """
        return self._tools.get(tool_name)
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle an MCP request.
        
        Args:
            request: The MCP request to handle
            
        Returns:
            The MCP response
        """
        try:
            if request.method == "tools/list":
                result = await self._handle_list_tools()
            elif request.method == "tools/call":
                result = await self._handle_call_tool(request.params)
            elif request.method == "resources/list":
                result = await self._handle_list_resources()
            elif request.method == "resources/read":
                result = await self._handle_read_resource(request.params)
            else:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Method '{request.method}' not found"
                    }
                )
            
            return MCPResponse(
                id=request.id,
                result=result
            )
            
        except Exception as e:
            self.logger.error("MCP request handling failed", error=str(e))
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            )
    
    async def _handle_list_tools(self) -> List[Dict[str, Any]]:
        """Handle tools/list request."""
        tools = []
        for tool in self._tools.values():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            })
        return tools
    
    async def _handle_call_tool(self, params: Dict[str, Any]) -> Any:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name is required")
        
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Execute the tool (this would integrate with the tool system)
        # For now, return a mock result
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Tool '{tool_name}' executed with arguments: {arguments}"
                }
            ]
        }
    
    async def _handle_list_resources(self) -> List[Dict[str, Any]]:
        """Handle resources/list request."""
        resources = []
        for name, resource in self._resources.items():
            resources.append({
                "uri": f"neurostack://{name}",
                "name": name,
                "description": str(resource)
            })
        return resources
    
    async def _handle_read_resource(self, params: Dict[str, Any]) -> Any:
        """Handle resources/read request."""
        uri = params.get("uri")
        if not uri:
            raise ValueError("Resource URI is required")
        
        # Parse URI and get resource
        if uri.startswith("neurostack://"):
            resource_name = uri[13:]  # Remove "neurostack://" prefix
            resource = self._resources.get(resource_name)
            if resource:
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "text/plain",
                            "text": str(resource)
                        }
                    ]
                }
        
        raise ValueError(f"Resource '{uri}' not found")
    
    def add_resource(self, name: str, resource: Any) -> None:
        """
        Add a resource to the MCP protocol.
        
        Args:
            name: The resource name
            resource: The resource data
        """
        self._resources[name] = resource
        self.logger.info("MCP resource added", resource_name=name)
    
    def remove_resource(self, name: str) -> bool:
        """
        Remove a resource from the MCP protocol.
        
        Args:
            name: The resource name
            
        Returns:
            True if resource was removed, False if not found
        """
        if name in self._resources:
            del self._resources[name]
            self.logger.info("MCP resource removed", resource_name=name)
            return True
        return False
    
    def get_protocol_info(self) -> Dict[str, Any]:
        """
        Get protocol information.
        
        Returns:
            Dictionary with protocol information
        """
        return {
            "name": "modelcontextprotocol",
            "version": "1.0.0",
            "capabilities": {
                "tools": {
                    "listChanged": True,
                    "call": True
                },
                "resources": {
                    "listChanged": True,
                    "read": True
                }
            }
        } 