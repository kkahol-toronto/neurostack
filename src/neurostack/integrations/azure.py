"""
Azure integration for NeuroStack.

This module provides Azure-specific integrations for the NeuroStack library,
including Azure Cognitive Services, Azure Functions, Azure Container Instances,
and other Azure services.
"""

import asyncio
import structlog
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

logger = structlog.get_logger(__name__)


class AzureService(ABC):
    """Abstract base class for Azure services."""
    
    def __init__(self, connection_string: str = None, subscription_id: str = None):
        self.connection_string = connection_string
        self.subscription_id = subscription_id
        self.logger = logger.bind(service=self.__class__.__name__)
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the Azure service connection."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Azure service."""
        pass


class AzureCognitiveServices(AzureService):
    """Azure Cognitive Services integration using APIM endpoint."""
    
    def __init__(self, endpoint: str, key: str, deployment_name: str = None):
        super().__init__()
        self.endpoint = endpoint
        self.key = key
        self.deployment_name = deployment_name
        self.client = None
    
    async def initialize(self) -> bool:
        """Initialize Azure Cognitive Services client using APIM."""
        try:
            # For APIM-based setup, we'll use the same endpoint as OpenAI
            # but with different API paths for vision tasks
            self.client = {
                "endpoint": self.endpoint,
                "key": self.key,
                "deployment": self.deployment_name
            }
            self.logger.info("Azure Cognitive Services (APIM) initialized")
            return True
        except Exception as e:
            self.logger.error("Failed to initialize Azure Cognitive Services", error=str(e))
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Azure Cognitive Services health."""
        try:
            if self.client:
                return {"status": "healthy", "service": "cognitive_services"}
            return {"status": "not_initialized", "service": "cognitive_services"}
        except Exception as e:
            return {"status": "error", "service": "cognitive_services", "error": str(e)}
    
    async def analyze_image(self, image_url: str, prompt: str = "Analyze this image and describe what you see") -> Dict[str, Any]:
        """Analyze an image using GPT-4V through APIM endpoint."""
        try:
            if not self.client:
                raise ValueError("Azure Cognitive Services not initialized")
            
            # Use GPT-4V for image analysis through APIM
            import aiohttp
            import base64
            import json
            
            # Prepare the request for GPT-4V
            headers = {
                "Content-Type": "application/json",
                "api-key": self.key
            }
            
            # Create the message with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
            
            # Build the APIM endpoint URL
            api_url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions"
            
            payload = {
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        return {
                            "description": content,
                            "analysis_type": "gpt4v",
                            "model": self.deployment_name,
                            "prompt": prompt
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"API call failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            self.logger.error("Image analysis failed", error=str(e))
            return {"error": str(e)}
    
    async def analyze_image_with_base64(self, image_base64: str, prompt: str = "Analyze this image and describe what you see") -> Dict[str, Any]:
        """Analyze an image using base64 encoded image data through APIM endpoint."""
        try:
            if not self.client:
                raise ValueError("Azure Cognitive Services not initialized")
            
            import aiohttp
            import json
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.key
            }
            
            # Create the message with base64 image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            api_url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions"
            
            payload = {
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        return {
                            "description": content,
                            "analysis_type": "gpt4v_base64",
                            "model": self.deployment_name,
                            "prompt": prompt
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"API call failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            self.logger.error("Image analysis failed", error=str(e))
            return {"error": str(e)}


class AzureOpenAI(AzureService):
    """Azure OpenAI integration."""
    
    def __init__(self, endpoint: str, key: str, deployment_name: str):
        super().__init__()
        self.endpoint = endpoint
        self.key = key
        self.deployment_name = deployment_name
        self.client = None
    
    async def initialize(self) -> bool:
        """Initialize Azure OpenAI client."""
        try:
            from openai import AzureOpenAI
            
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.key,
                api_version="2024-02-15-preview"
            )
            self.logger.info("Azure OpenAI initialized")
            return True
        except ImportError:
            self.logger.warning("Azure OpenAI SDK not available")
            return False
        except Exception as e:
            self.logger.error("Failed to initialize Azure OpenAI", error=str(e))
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Azure OpenAI health."""
        try:
            if self.client:
                # Simple health check
                return {"status": "healthy", "service": "azure_openai"}
            return {"status": "not_initialized", "service": "azure_openai"}
        except Exception as e:
            return {"status": "error", "service": "azure_openai", "error": str(e)}
    
    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using Azure OpenAI."""
        try:
            if not self.client:
                raise ValueError("Azure OpenAI not initialized")
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error("Text generation failed", error=str(e))
            return f"Error: {str(e)}"


class AzureFunctions(AzureService):
    """Azure Functions integration."""
    
    def __init__(self, function_url: str, function_key: str = None):
        super().__init__()
        self.function_url = function_url
        self.function_key = function_key
    
    async def initialize(self) -> bool:
        """Initialize Azure Functions connection."""
        try:
            # Test connection
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.function_key:
                    headers["x-functions-key"] = self.function_key
                
                async with session.get(self.function_url, headers=headers) as response:
                    if response.status == 200:
                        self.logger.info("Azure Functions connection verified")
                        return True
                    else:
                        self.logger.warning("Azure Functions connection failed", status=response.status)
                        return False
        except Exception as e:
            self.logger.error("Failed to initialize Azure Functions", error=str(e))
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Azure Functions health."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.function_key:
                    headers["x-functions-key"] = self.function_key
                
                async with session.get(self.function_url, headers=headers) as response:
                    return {
                        "status": "healthy" if response.status == 200 else "error",
                        "service": "azure_functions",
                        "status_code": response.status
                    }
        except Exception as e:
            return {"status": "error", "service": "azure_functions", "error": str(e)}
    
    async def invoke_function(self, function_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke an Azure Function."""
        try:
            import aiohttp
            import json
            
            url = f"{self.function_url}/{function_name}"
            headers = {"Content-Type": "application/json"}
            if self.function_key:
                headers["x-functions-key"] = self.function_key
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Function invocation failed: {response.status}"}
        except Exception as e:
            self.logger.error("Function invocation failed", error=str(e))
            return {"error": str(e)}


class AzureContainerInstances(AzureService):
    """Azure Container Instances integration."""
    
    def __init__(self, subscription_id: str, resource_group: str, location: str):
        super().__init__(subscription_id=subscription_id)
        self.resource_group = resource_group
        self.location = location
        self.client = None
    
    async def initialize(self) -> bool:
        """Initialize Azure Container Instances client."""
        try:
            from azure.mgmt.containerinstance import ContainerInstanceManagementClient
            from azure.identity import DefaultAzureCredential
            
            credential = DefaultAzureCredential()
            self.client = ContainerInstanceManagementClient(
                credential=credential,
                subscription_id=self.subscription_id
            )
            self.logger.info("Azure Container Instances initialized")
            return True
        except ImportError:
            self.logger.warning("Azure Container Instances SDK not available")
            return False
        except Exception as e:
            self.logger.error("Failed to initialize Azure Container Instances", error=str(e))
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Azure Container Instances health."""
        try:
            if self.client:
                return {"status": "healthy", "service": "container_instances"}
            return {"status": "not_initialized", "service": "container_instances"}
        except Exception as e:
            return {"status": "error", "service": "container_instances", "error": str(e)}
    
    async def create_container_group(self, name: str, image: str, command: List[str] = None) -> Dict[str, Any]:
        """Create a container group in Azure Container Instances."""
        try:
            if not self.client:
                raise ValueError("Azure Container Instances not initialized")
            
            from azure.mgmt.containerinstance.models import (
                ContainerGroup, Container, ResourceRequests, ResourceRequirements
            )
            
            # Create container group
            container_group = ContainerGroup(
                location=self.location,
                containers=[
                    Container(
                        name=name,
                        image=image,
                        resources=ResourceRequirements(
                            requests=ResourceRequests(
                                memory_in_gb=1.0,
                                cpu=1.0
                            )
                        ),
                        command=command
                    )
                ],
                os_type="Linux",
                restart_policy="Never"
            )
            
            poller = self.client.container_groups.begin_create_or_update(
                resource_group_name=self.resource_group,
                container_group_name=name,
                container_group=container_group
            )
            
            result = poller.result()
            return {
                "name": result.name,
                "provisioning_state": result.provisioning_state,
                "ip_address": result.ip_address.ip if result.ip_address else None
            }
        except Exception as e:
            self.logger.error("Container group creation failed", error=str(e))
            return {"error": str(e)}


class AzureIntegration:
    """
    Main Azure integration class for NeuroStack.
    
    This class provides a unified interface for all Azure services
    used by the NeuroStack library.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logger.bind(integration="azure")
        
        # Initialize Azure services
        self.cognitive_services = None
        self.openai = None
        self.functions = None
        self.container_instances = None
        
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Azure services based on configuration."""
        # For APIM setup, we use the same endpoint and key for both services
        apim_endpoint = None
        apim_key = None
        deployment_name = None
        
        # Get APIM configuration from either openai or cognitive_services config
        if "openai" in self.config:
            oai_config = self.config["openai"]
            apim_endpoint = oai_config.get("endpoint")
            apim_key = oai_config.get("key")
            deployment_name = oai_config.get("deployment_name")
        
        # Azure OpenAI
        if apim_endpoint and apim_key and deployment_name:
            self.openai = AzureOpenAI(
                endpoint=apim_endpoint,
                key=apim_key,
                deployment_name=deployment_name
            )
        
        # Azure Cognitive Services (using same APIM endpoint)
        if apim_endpoint and apim_key and deployment_name:
            self.cognitive_services = AzureCognitiveServices(
                endpoint=apim_endpoint,
                key=apim_key,
                deployment_name=deployment_name
            )
        
        # Azure Functions
        if "functions" in self.config:
            func_config = self.config["functions"]
            self.functions = AzureFunctions(
                function_url=func_config.get("function_url"),
                function_key=func_config.get("function_key")
            )
        
        # Azure Container Instances
        if "container_instances" in self.config:
            ci_config = self.config["container_instances"]
            self.container_instances = AzureContainerInstances(
                subscription_id=ci_config.get("subscription_id"),
                resource_group=ci_config.get("resource_group"),
                location=ci_config.get("location")
            )
    
    async def initialize(self) -> bool:
        """Initialize all Azure services."""
        try:
            tasks = []
            
            if self.cognitive_services:
                tasks.append(self.cognitive_services.initialize())
            if self.openai:
                tasks.append(self.openai.initialize())
            if self.functions:
                tasks.append(self.functions.initialize())
            if self.container_instances:
                tasks.append(self.container_instances.initialize())
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count = sum(1 for r in results if r is True)
                self.logger.info("Azure services initialized", 
                               total=len(tasks), 
                               successful=success_count)
                return success_count == len(tasks)
            
            return True
        except Exception as e:
            self.logger.error("Failed to initialize Azure integration", error=str(e))
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all Azure services."""
        try:
            tasks = []
            
            if self.cognitive_services:
                tasks.append(self.cognitive_services.health_check())
            if self.openai:
                tasks.append(self.openai.health_check())
            if self.functions:
                tasks.append(self.functions.health_check())
            if self.container_instances:
                tasks.append(self.container_instances.health_check())
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return {
                    "integration": "azure",
                    "services": results,
                    "overall_status": "healthy" if all(
                        r.get("status") == "healthy" for r in results if isinstance(r, dict)
                    ) else "degraded"
                }
            
            return {"integration": "azure", "services": [], "overall_status": "no_services"}
        except Exception as e:
            return {"integration": "azure", "error": str(e), "overall_status": "error"}
    
    def get_service(self, service_name: str) -> Optional[AzureService]:
        """Get a specific Azure service by name."""
        services = {
            "cognitive_services": self.cognitive_services,
            "openai": self.openai,
            "functions": self.functions,
            "container_instances": self.container_instances
        }
        return services.get(service_name) 