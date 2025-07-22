"""
Agent orchestrator for managing multi-agent workflows.

This module provides the orchestration capabilities for coordinating
multiple agents in complex workflows.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

import structlog
from pydantic import BaseModel, Field

from .base import Agent, AgentContext, AgentMessage

logger = structlog.get_logger(__name__)


class WorkflowState(str, Enum):
    """Possible states of a workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """A step in a workflow."""
    id: str
    agent_name: str
    task: Any
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    workflow_id: UUID
    state: WorkflowState
    results: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowDefinition(BaseModel):
    """Definition of a workflow."""
    name: str
    description: str = ""
    steps: List[WorkflowStep] = Field(default_factory=list)
    max_concurrent: int = 5
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentOrchestrator:
    """
    Orchestrator for managing multi-agent workflows.
    
    This class coordinates the execution of multiple agents in complex
    workflows, handling dependencies, error recovery, and state management.
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.workflows: Dict[UUID, WorkflowDefinition] = {}
        self.active_workflows: Dict[UUID, WorkflowResult] = {}
        self.logger = logger.bind(component="orchestrator")
        
    def register_agent(self, name: str, agent: Agent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            name: The name to register the agent under
            agent: The agent instance
        """
        self.agents[name] = agent
        self.logger.info("Agent registered", agent_name=name)
    
    def unregister_agent(self, name: str) -> None:
        """
        Unregister an agent from the orchestrator.
        
        Args:
            name: The name of the agent to unregister
        """
        if name in self.agents:
            del self.agents[name]
            self.logger.info("Agent unregistered", agent_name=name)
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name.
        
        Args:
            name: The name of the agent
            
        Returns:
            The agent instance or None if not found
        """
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """
        Get a list of all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())
    
    def create_workflow(self, definition: WorkflowDefinition) -> UUID:
        """
        Create a new workflow from a definition.
        
        Args:
            definition: The workflow definition
            
        Returns:
            The workflow ID
        """
        workflow_id = uuid4()
        self.workflows[workflow_id] = definition
        self.logger.info("Workflow created", 
                        workflow_id=str(workflow_id), 
                        workflow_name=definition.name)
        return workflow_id
    
    async def run_workflow(self, workflow_id: UUID, 
                          context: Optional[AgentContext] = None) -> WorkflowResult:
        """
        Run a workflow by ID.
        
        Args:
            workflow_id: The ID of the workflow to run
            context: Optional context for the workflow
            
        Returns:
            The result of the workflow execution
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        definition = self.workflows[workflow_id]
        result = WorkflowResult(
            workflow_id=workflow_id,
            state=WorkflowState.RUNNING
        )
        
        self.active_workflows[workflow_id] = result
        context = context or AgentContext()
        
        try:
            self.logger.info("Starting workflow", 
                           workflow_id=str(workflow_id), 
                           workflow_name=definition.name)
            
            # Execute steps in dependency order
            completed_steps = set()
            step_results = {}
            
            while len(completed_steps) < len(definition.steps):
                # Find steps that can be executed
                executable_steps = [
                    step for step in definition.steps
                    if step.id not in completed_steps and
                    all(dep in completed_steps for dep in step.dependencies)
                ]
                
                if not executable_steps:
                    # Check for circular dependencies
                    remaining_steps = [
                        step.id for step in definition.steps
                        if step.id not in completed_steps
                    ]
                    raise ValueError(f"Circular dependency detected in steps: {remaining_steps}")
                
                # Execute steps concurrently (up to max_concurrent)
                import asyncio
                tasks = []
                for step in executable_steps[:definition.max_concurrent]:
                    task = self._execute_step(step, context, step_results)
                    tasks.append(task)
                
                if tasks:
                    step_results_batch = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for step, step_result in zip(executable_steps[:definition.max_concurrent], step_results_batch):
                        if isinstance(step_result, Exception):
                            result.errors[step.id] = str(step_result)
                            result.state = WorkflowState.FAILED
                            self.logger.error("Step failed", 
                                            step_id=step.id, 
                                            error=str(step_result))
                        else:
                            step_results[step.id] = step_result
                            completed_steps.add(step.id)
                            self.logger.info("Step completed", step_id=step.id)
            
            result.results = step_results
            result.state = WorkflowState.COMPLETED
            self.logger.info("Workflow completed", workflow_id=str(workflow_id))
            
        except Exception as e:
            result.state = WorkflowState.FAILED
            result.errors["workflow"] = str(e)
            self.logger.error("Workflow failed", 
                            workflow_id=str(workflow_id), 
                            error=str(e))
        
        finally:
            # Clean up
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
        
        return result
    
    async def _execute_step(self, step: WorkflowStep, context: AgentContext, 
                           step_results: Dict[str, Any]) -> Any:
        """
        Execute a single workflow step.
        
        Args:
            step: The step to execute
            context: The workflow context
            step_results: Results from previous steps
            
        Returns:
            The result of the step execution
        """
        agent = self.get_agent(step.agent_name)
        if not agent:
            raise ValueError(f"Agent {step.agent_name} not found")
        
        # Prepare task with context from previous steps
        task = self._prepare_task(step.task, step_results)
        
        # Execute the step
        result = await agent.execute(task, context)
        return result
    
    def _prepare_task(self, task: Any, step_results: Dict[str, Any]) -> Any:
        """
        Prepare a task with context from previous step results.
        
        Args:
            task: The original task
            step_results: Results from previous steps
            
        Returns:
            The prepared task
        """
        # If task is a string, try to substitute placeholders
        if isinstance(task, str):
            for step_id, result in step_results.items():
                placeholder = f"{{step.{step_id}}}"
                if placeholder in task:
                    task = task.replace(placeholder, str(result))
        
        return task
    
    async def run_simple_workflow(self, steps: List[Dict[str, Any]], 
                                 context: Optional[AgentContext] = None) -> WorkflowResult:
        """
        Run a simple workflow defined as a list of step dictionaries.
        
        Args:
            steps: List of step definitions
            context: Optional context for the workflow
            
        Returns:
            The result of the workflow execution
        """
        # Convert step dictionaries to WorkflowStep objects
        workflow_steps = []
        for i, step_dict in enumerate(steps):
            step = WorkflowStep(
                id=step_dict.get("id", f"step_{i}"),
                agent_name=step_dict["agent"],
                task=step_dict["task"],
                dependencies=step_dict.get("dependencies", []),
                timeout=step_dict.get("timeout"),
                max_retries=step_dict.get("max_retries", 3),
                metadata=step_dict.get("metadata", {})
            )
            workflow_steps.append(step)
        
        definition = WorkflowDefinition(
            name="simple_workflow",
            steps=workflow_steps
        )
        
        workflow_id = self.create_workflow(definition)
        return await self.run_workflow(workflow_id, context)
    
    def get_workflow_status(self, workflow_id: UUID) -> Optional[WorkflowResult]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            The workflow result or None if not found
        """
        return self.active_workflows.get(workflow_id)
    
    def cancel_workflow(self, workflow_id: UUID) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            workflow_id: The workflow ID to cancel
            
        Returns:
            True if workflow was cancelled, False if not found
        """
        if workflow_id in self.active_workflows:
            result = self.active_workflows[workflow_id]
            result.state = WorkflowState.CANCELLED
            del self.active_workflows[workflow_id]
            self.logger.info("Workflow cancelled", workflow_id=str(workflow_id))
            return True
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the overall status of the orchestrator.
        
        Returns:
            Dictionary with system status information
        """
        return {
            "agents_count": len(self.agents),
            "agents": [agent.get_status() for agent in self.agents.values()],
            "workflows_count": len(self.workflows),
            "active_workflows_count": len(self.active_workflows),
            "active_workflows": [
                {
                    "workflow_id": str(wf_id),
                    "state": result.state.value
                }
                for wf_id, result in self.active_workflows.items()
            ]
        } 