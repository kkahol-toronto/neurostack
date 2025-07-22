"""
Azure integration example for NeuroStack.

This example demonstrates how to use NeuroStack with Azure services
including Azure OpenAI, Azure Functions, and Azure Cognitive Services.
"""

import asyncio
import structlog
from typing import Any

from neurostack import AgentOrchestrator, AgentConfig, SimpleAgent, AgentContext, AzureIntegration


# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


class AzureAIAgent(SimpleAgent):
    """An agent that uses Azure AI services."""
    
    def __init__(self, config: AgentConfig, azure_integration: AzureIntegration):
        super().__init__(config)
        self.azure_integration = azure_integration
    
    async def execute(self, task: Any, context=None) -> Any:
        """Execute a task using Azure AI services."""
        from neurostack.core.agents.base import AgentState
        self.state = AgentState.RUNNING
        
        try:
            if isinstance(task, str):
                if "generate" in task.lower() or "text" in task.lower():
                    # Use Azure OpenAI for text generation
                    if self.azure_integration.openai:
                        result = await self.azure_integration.openai.generate_text(task)
                    else:
                        result = f"Azure OpenAI not available. Task: {task}"
                
                elif "analyze" in task.lower() and "image" in task.lower():
                    # Use Azure Cognitive Services for image analysis
                    if self.azure_integration.cognitive_services:
                        # This would need an actual image URL
                        image_url = "https://example.com/image.jpg"
                        result = await self.azure_integration.cognitive_services.analyze_image(image_url)
                    else:
                        result = f"Azure Cognitive Services not available. Task: {task}"
                
                elif "function" in task.lower():
                    # Use Azure Functions
                    if self.azure_integration.functions:
                        function_data = {"task": task, "context": str(context)}
                        result = await self.azure_integration.functions.invoke_function("process-task", function_data)
                    else:
                        result = f"Azure Functions not available. Task: {task}"
                
                else:
                    result = f"Azure AI processing completed for: {task}"
            else:
                result = f"Processed Azure task: {task}"
            
            self.state = AgentState.COMPLETED
            return result
            
        except Exception as e:
            self.state = AgentState.ERROR
            raise


async def main():
    """Main example function."""
    print("🚀 Starting NeuroStack Azure Integration Example")
    
    # Azure configuration for APIM setup (you would load this from environment variables)
    azure_config = {
        "openai": {
            "endpoint": "https://your-apim-gateway.azure-api.net/",  # Your APIM endpoint
            "key": "your-apim-subscription-key",  # Your APIM subscription key
            "deployment_name": "gpt-4"  # Your model deployment name
        },
        "functions": {
            "function_url": "https://your-function-app.azurewebsites.net/api/",
            "function_key": "your-function-key"
        },
        "container_instances": {
            "subscription_id": "your-subscription-id",
            "resource_group": "your-resource-group",
            "location": "eastus"
        }
    }
    
    # Initialize Azure integration
    print("\n🔧 Initializing Azure integration...")
    azure_integration = AzureIntegration(azure_config)
    
    # Note: In a real scenario, you would have actual Azure credentials
    # For this example, we'll show the structure but skip actual initialization
    print("⚠️  Azure integration created (credentials not provided for demo)")
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Create Azure AI agent
    azure_agent = AzureAIAgent(
        AgentConfig(
            name="azure_ai_agent",
            description="Agent that uses Azure AI services",
            model="azure-gpt-4",
            memory_enabled=True,
            reasoning_enabled=True
        ),
        azure_integration
    )
    
    # Register agent
    orchestrator.register_agent("azure_ai_agent", azure_agent)
    
    print(f"📊 Registered agents: {orchestrator.list_agents()}")
    
    # Create context
    context = AgentContext(
        user_id="azure_user",
        tenant_id="azure_tenant",
        conversation_id="azure_conversation"
    )
    
    # Run Azure-specific workflow
    print("\n🔄 Running Azure AI workflow...")
    
    workflow_steps = [
        {
            "id": "text_generation",
            "agent": "azure_ai_agent",
            "task": "Generate a summary of Azure AI capabilities"
        },
        {
            "id": "image_analysis",
            "agent": "azure_ai_agent", 
            "task": "Analyze image content for object detection",
            "dependencies": ["text_generation"]
        },
        {
            "id": "function_processing",
            "agent": "azure_ai_agent",
            "task": "Process data using Azure Functions",
            "dependencies": ["image_analysis"]
        }
    ]
    
    result = await orchestrator.run_simple_workflow(workflow_steps, context)
    
    print(f"\n✅ Workflow completed with state: {result.state.value}")
    
    if result.results:
        print("\n📋 Results:")
        for step_id, step_result in result.results.items():
            print(f"  {step_id}: {step_result}")
    
    if result.errors:
        print("\n❌ Errors:")
        for step_id, error in result.errors.items():
            print(f"  {step_id}: {error}")
    
    # Check Azure integration health
    print("\n🏥 Azure Integration Health Check:")
    health = await azure_integration.health_check()
    print(f"  Overall Status: {health.get('overall_status', 'unknown')}")
    
    if 'services' in health:
        for service in health['services']:
            if isinstance(service, dict):
                service_name = service.get('service', 'unknown')
                status = service.get('status', 'unknown')
                print(f"  {service_name}: {status}")
    
    # Get system status
    print("\n📊 System Status:")
    status = orchestrator.get_system_status()
    print(f"  Agents: {status['agents_count']}")
    print(f"  Workflows: {status['workflows_count']}")
    
    print("\n🎉 Azure Integration Example completed!")


if __name__ == "__main__":
    asyncio.run(main()) 