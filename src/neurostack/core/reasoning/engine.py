"""
Reasoning engine for agent cognition and decision-making.

This module provides the core reasoning capabilities for agents,
including LLM integration, planning, and decision-making logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog
from pydantic import BaseModel

from ..agents.base import AgentContext

logger = structlog.get_logger(__name__)


class ReasoningResult(BaseModel):
    """Result of a reasoning operation."""
    content: str
    confidence: float = 0.0
    reasoning_steps: List[str] = []
    metadata: Dict[str, Any] = {}


class ReasoningEngine:
    """
    Reasoning engine for agent cognition and decision-making.
    
    This class provides the core reasoning capabilities for agents,
    including LLM integration, planning, and decision-making logic.
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.logger = logger.bind(model=model)
        
        # Initialize LLM client
        self._llm_client = None
        
    @property
    def llm_client(self):
        """Get the LLM client instance."""
        if self._llm_client is None:
            self._llm_client = self._create_llm_client()
        return self._llm_client
    
    def _create_llm_client(self):
        """Create an LLM client based on the model."""
        try:
            if self.model.startswith("gpt-"):
                import openai
                return OpenAIClient(self.model, self.temperature)
            elif self.model.startswith("claude-"):
                import anthropic
                return AnthropicClient(self.model, self.temperature)
            else:
                # Fallback to a simple client
                return SimpleLLMClient(self.model, self.temperature)
        except ImportError as e:
            self.logger.warning(f"LLM library not available: {e}")
            return SimpleLLMClient(self.model, self.temperature)
    
    async def process(self, task: Any, context: Optional[AgentContext] = None) -> str:
        """
        Process a task using reasoning.
        
        Args:
            task: The task to process
            context: Optional context for the task
            
        Returns:
            The reasoning result
        """
        try:
            # Convert task to string if needed
            if not isinstance(task, str):
                task = str(task)
            
            # Build prompt with context
            prompt = self._build_prompt(task, context)
            
            # Get response from LLM
            response = await self.llm_client.generate(prompt)
            
            self.logger.info("Task processed", task_length=len(task))
            return response
            
        except Exception as e:
            self.logger.error("Task processing failed", error=str(e))
            return f"Error processing task: {str(e)}"
    
    async def plan(self, goal: str, available_tools: List[str], 
                  context: Optional[AgentContext] = None) -> List[str]:
        """
        Create a plan to achieve a goal.
        
        Args:
            goal: The goal to achieve
            available_tools: List of available tools
            context: Optional context
            
        Returns:
            List of planned steps
        """
        try:
            prompt = f"""
            Goal: {goal}
            Available tools: {', '.join(available_tools)}
            
            Create a step-by-step plan to achieve this goal. 
            Each step should be a clear action that can be executed.
            
            Plan:
            """
            
            response = await self.llm_client.generate(prompt)
            
            # Parse the response into steps
            steps = self._parse_plan_response(response)
            
            self.logger.info("Plan created", goal=goal, steps_count=len(steps))
            return steps
            
        except Exception as e:
            self.logger.error("Planning failed", error=str(e))
            return [f"Error creating plan: {str(e)}"]
    
    async def decide(self, options: List[str], context: str, 
                    criteria: Optional[List[str]] = None) -> str:
        """
        Make a decision between options.
        
        Args:
            options: List of available options
            context: Context for the decision
            criteria: Optional criteria to consider
            
        Returns:
            The chosen option
        """
        try:
            prompt = f"""
            Context: {context}
            Options: {', '.join(options)}
            """
            
            if criteria:
                prompt += f"\nCriteria to consider: {', '.join(criteria)}"
            
            prompt += "\n\nChoose the best option and explain why:"
            
            response = await self.llm_client.generate(prompt)
            
            # Extract the chosen option
            chosen = self._extract_decision(response, options)
            
            self.logger.info("Decision made", options_count=len(options), chosen=chosen)
            return chosen
            
        except Exception as e:
            self.logger.error("Decision making failed", error=str(e))
            return options[0] if options else "No decision made"
    
    async def reflect(self, action: str, result: str, 
                     context: Optional[AgentContext] = None) -> str:
        """
        Reflect on an action and its result.
        
        Args:
            action: The action that was taken
            result: The result of the action
            context: Optional context
            
        Returns:
            Reflection on the action and result
        """
        try:
            prompt = f"""
            Action taken: {action}
            Result: {result}
            
            Reflect on this action and result. Consider:
            1. Was the action successful?
            2. What could have been done differently?
            3. What lessons can be learned?
            
            Reflection:
            """
            
            response = await self.llm_client.generate(prompt)
            
            self.logger.info("Reflection completed", action=action)
            return response
            
        except Exception as e:
            self.logger.error("Reflection failed", error=str(e))
            return f"Error reflecting: {str(e)}"
    
    def _build_prompt(self, task: str, context: Optional[AgentContext] = None) -> str:
        """
        Build a prompt for the LLM.
        
        Args:
            task: The task to process
            context: Optional context
            
        Returns:
            The formatted prompt
        """
        prompt = f"Task: {task}\n\n"
        
        if context:
            prompt += f"Context:\n"
            prompt += f"- Session ID: {context.session_id}\n"
            if context.user_id:
                prompt += f"- User ID: {context.user_id}\n"
            if context.tenant_id:
                prompt += f"- Tenant ID: {context.tenant_id}\n"
            if context.conversation_id:
                prompt += f"- Conversation ID: {context.conversation_id}\n"
            prompt += "\n"
        
        prompt += "Please provide a clear and helpful response to this task."
        return prompt
    
    def _parse_plan_response(self, response: str) -> List[str]:
        """
        Parse a plan response into individual steps.
        
        Args:
            response: The LLM response
            
        Returns:
            List of plan steps
        """
        lines = response.strip().split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Remove numbering/bullets
                step = line.lstrip('0123456789.-* ').strip()
                if step:
                    steps.append(step)
        
        return steps
    
    def _extract_decision(self, response: str, options: List[str]) -> str:
        """
        Extract the chosen option from a decision response.
        
        Args:
            response: The LLM response
            options: List of available options
            
        Returns:
            The chosen option
        """
        response_lower = response.lower()
        
        for option in options:
            if option.lower() in response_lower:
                return option
        
        # If no exact match, return the first option
        return options[0] if options else "No decision"


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, model: str, temperature: float):
        self.model = model
        self.temperature = temperature
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response to a prompt."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI client for GPT models."""
    
    async def generate(self, prompt: str) -> str:
        """Generate a response using OpenAI."""
        try:
            import openai
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error("OpenAI API call failed", error=str(e))
            return f"Error: {str(e)}"


class AnthropicClient(LLMClient):
    """Anthropic client for Claude models."""
    
    async def generate(self, prompt: str) -> str:
        """Generate a response using Anthropic."""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic()
            response = await client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error("Anthropic API call failed", error=str(e))
            return f"Error: {str(e)}"


class SimpleLLMClient(LLMClient):
    """Simple LLM client for testing and fallback."""
    
    async def generate(self, prompt: str) -> str:
        """Generate a simple response."""
        # Simple rule-based responses for testing
        prompt_lower = prompt.lower()
        
        if "analyze" in prompt_lower:
            return "Analysis completed successfully. The data shows positive trends."
        elif "summarize" in prompt_lower:
            return "Summary: Key points have been identified and documented."
        elif "plan" in prompt_lower:
            return "1. Gather information\n2. Analyze requirements\n3. Execute plan\n4. Review results"
        elif "decide" in prompt_lower or "choose" in prompt_lower:
            return "Based on the available information, the best option is the first one."
        else:
            return f"Processed: {prompt[:100]}..." 