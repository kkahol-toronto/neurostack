"""
Simple example demonstrating NeuroStack usage.

This example shows how to create agents, set up memory, and run
simple workflows using the NeuroStack library.
"""

import asyncio
import structlog
from typing import Any

from neurostack import AgentOrchestrator, AgentConfig, SimpleAgent, AgentContext


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


class DataAnalysisAgent(SimpleAgent):
    """An agent that performs data analysis tasks."""
    
    async def execute(self, task: Any, context=None) -> Any:
        """Execute a data analysis task."""
        from neurostack.core.agents.base import AgentState
        self.state = AgentState.RUNNING
        
        try:
            if isinstance(task, str):
                if "analyze" in task.lower():
                    result = f"Analysis completed for: {task}"
                elif "summarize" in task.lower():
                    result = f"Summary generated for: {task}"
                else:
                    result = f"Data processing completed for: {task}"
            else:
                result = f"Processed data: {task}"
            
            # Don't use memory for now to isolate the issue
            # if self.memory:
            #     await self.memory.store_result(task, result)
            
            self.state = AgentState.COMPLETED
            return result
            
        except Exception as e:
            self.state = AgentState.ERROR
            raise


class ReportGenerationAgent(SimpleAgent):
    """An agent that generates reports."""
    
    async def execute(self, task: Any, context=None) -> Any:
        """Execute a report generation task."""
        from neurostack.core.agents.base import AgentState
        self.state = AgentState.RUNNING
        
        try:
            if isinstance(task, str):
                if "report" in task.lower():
                    result = f"Report generated: {task}"
                else:
                    result = f"Document created: {task}"
            else:
                result = f"Generated report for: {task}"
            
            # Don't use memory for now to isolate the issue
            # if self.memory:
            #     await self.memory.store_result(task, result)
            
            self.state = AgentState.COMPLETED
            return result
            
        except Exception as e:
            self.state = AgentState.ERROR
            raise


async def main():
    """Main example function."""
    print("🚀 Starting NeuroStack Simple Example")
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Create agents with memory disabled
    data_agent = DataAnalysisAgent(AgentConfig(
        name="data_analyst",
        description="Agent for data analysis tasks",
        model="gpt-4",
        memory_enabled=False,  # Disable memory
        reasoning_enabled=False  # Disable reasoning for now
    ))
    
    report_agent = ReportGenerationAgent(AgentConfig(
        name="report_generator",
        description="Agent for report generation",
        model="gpt-4",
        memory_enabled=False,  # Disable memory
        reasoning_enabled=False  # Disable reasoning for now
    ))
    
    # Register agents
    orchestrator.register_agent("data_analyst", data_agent)
    orchestrator.register_agent("report_generator", report_agent)
    
    print(f"📊 Registered agents: {orchestrator.list_agents()}")
    
    # Create context
    context = AgentContext(
        user_id="example_user",
        tenant_id="example_tenant",
        conversation_id="example_conversation"
    )
    
    # Run a simple workflow
    print("\n🔄 Running simple workflow...")
    
    workflow_steps = [
        {
            "id": "analyze_data",
            "agent": "data_analyst",
            "task": "Analyze sales data for Q4 2023"
        },
        {
            "id": "generate_report",
            "agent": "report_generator",
            "task": "Generate quarterly sales report based on {step.analyze_data}",
            "dependencies": ["analyze_data"]
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
    
    # Get system status
    print("\n📊 System Status:")
    status = orchestrator.get_system_status()
    print(f"  Agents: {status['agents_count']}")
    print(f"  Workflows: {status['workflows_count']}")
    
    print("\n🎉 Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main()) 