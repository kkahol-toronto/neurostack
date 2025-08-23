# 🧠 NeuroStack Developer Guide

## 🎯 Overview

NeuroStack is an enterprise-grade agentic AI platform that provides developers with the building blocks to create intelligent, memory-enabled, and reasoning-capable AI agents. This guide will walk you through the process of integrating NeuroStack into your applications.

## 🏗️ Architecture Overview

NeuroStack is built with a modular, layered architecture:

```
NeuroStack
├── Core Components
│   ├── Agents (Orchestration & Management)
│   ├── Memory (Working, Vector, Long-term)
│   ├── Reasoning (AI-powered decision making)
│   ├── Tools (Extensible tool system)
│   └── Protocols (MCP, A2A communication)
├── Integrations
│   ├── Azure (OpenAI, Cognitive Services)
│   ├── GCP (Vertex AI, Cloud Functions)
│   └── On-premise (Local deployments)
└── Layers
    ├── Infrastructure (Deployment & scaling)
    ├── Application (Business logic)
    ├── Cognition (AI capabilities)
    └── Governance (Security & compliance)
```

## 🚀 Quick Start Guide

> **Note**: NeuroStack is currently a local library under development. It's not yet published to PyPI. We're focusing on building a complete, stable implementation before any public release.

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/kkahol-toronto/neurostack.git
cd neurostack

# Install in development mode
pip install -e .

# Set up environment variables
cp env.template .env
# Edit .env with your configuration
```

### 2. Basic Usage

```python
from src.neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

# Initialize core components
memory_manager = MemoryManager()
reasoning_engine = ReasoningEngine(model="gpt-4")
tool_registry = ToolRegistry()

# Create an agent
agent = Agent(
    name="my_agent",
    memory_manager=memory_manager,
    reasoning_engine=reasoning_engine,
    tool_registry=tool_registry
)

# Use the agent
response = await agent.process("Hello, how can you help me?")
print(response)
```

## 📚 Core Components Deep Dive

### 1. Agents (`neurostack.core.agents`)

Agents are the main orchestrators in NeuroStack. They coordinate between memory, reasoning, and tools.

```python
from src.neurostack.core.agents import Agent, AgentOrchestrator, AgentConfig

# Simple agent configuration
config = AgentConfig(
    name="customer_service_agent",
    description="Handles customer inquiries",
    capabilities=["text_processing", "data_retrieval"],
    memory_enabled=True,
    reasoning_enabled=True
)

# Create agent
agent = Agent(config)

# Agent orchestration (multiple agents)
orchestrator = AgentOrchestrator()
orchestrator.add_agent(agent)
orchestrator.add_agent(another_agent)

# Process with multiple agents
result = await orchestrator.process("Complex multi-agent task")
```

### 2. Memory Management (`neurostack.core.memory`)

NeuroStack provides three types of memory:

```python
from src.neurostack.core.memory import MemoryManager, VectorMemory, WorkingMemory

# Initialize memory manager
memory_manager = MemoryManager()

# Working Memory (temporary, session-based)
working_memory = WorkingMemory()
working_memory.store("current_session", {"user_id": "123", "context": "..."})

# Vector Memory (semantic search)
vector_memory = VectorMemory()
await vector_memory.store_embedding("customer_profile", customer_embedding)
similar_profiles = await vector_memory.search("high value customer", limit=5)

# Long-term Memory (persistent storage)
long_term_memory = memory_manager.get_long_term_memory()
await long_term_memory.store("customer_interaction", interaction_data)
```

### 3. Reasoning Engine (`neurostack.core.reasoning`)

The reasoning engine provides AI-powered decision making:

```python
from src.neurostack.core.reasoning import ReasoningEngine

# Initialize reasoning engine
reasoning_engine = ReasoningEngine(
    model="gpt-4",
    temperature=0.7,
    max_tokens=1000
)

# Simple reasoning
result = await reasoning_engine.reason(
    context="Customer inquiry about loan",
    question="What information do I need to collect?",
    available_tools=["customer_lookup", "credit_check"]
)

# Chain reasoning (multiple steps)
chain_result = await reasoning_engine.chain_reason([
    "Analyze customer request",
    "Identify required data",
    "Generate response plan"
], context="Loan application")
```

### 4. Tools (`neurostack.core.tools`)

Tools are the building blocks for agent capabilities:

```python
from src.neurostack.core.tools import Tool, ToolRegistry, ToolResult

# Create a custom tool
class CustomerLookupTool(Tool):
    def __init__(self):
        super().__init__(
            name="customer_lookup",
            description="Look up customer information by ID or name",
            parameters={
                "customer_id": {"type": "string", "required": False},
                "customer_name": {"type": "string", "required": False}
            }
        )
    
    async def execute(self, parameters: dict) -> ToolResult:
        customer_id = parameters.get("customer_id")
        customer_name = parameters.get("customer_name")
        
        # Your tool logic here
        customer_data = await self.lookup_customer(customer_id, customer_name)
        
        return ToolResult(
            success=True,
            data=customer_data,
            metadata={"source": "customer_database"}
        )

# Register tools
tool_registry = ToolRegistry()
tool_registry.register_tool(CustomerLookupTool())
tool_registry.register_tool(AnotherTool())

# Use tools
tool = tool_registry.get_tool("customer_lookup")
result = await tool.execute({"customer_id": "123"})
```

## 🔧 Integration Patterns

### Pattern 1: FastAPI Integration

This is the pattern we used in the banking agent:

```python
from fastapi import FastAPI, Depends
from src.neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

app = FastAPI()

# Global NeuroStack instance
neurostack_agent = None

async def get_neurostack_agent():
    global neurostack_agent
    if neurostack_agent is None:
        # Initialize NeuroStack components
        memory_manager = MemoryManager()
        reasoning_engine = ReasoningEngine(model="gpt-4")
        tool_registry = ToolRegistry()
        
        # Register your tools
        tool_registry.register_tool(YourCustomTool())
        
        # Create agent
        neurostack_agent = Agent(
            name="api_agent",
            memory_manager=memory_manager,
            reasoning_engine=reasoning_engine,
            tool_registry=tool_registry
        )
    
    return neurostack_agent

@app.post("/api/process")
async def process_request(
    request: dict,
    agent: Agent = Depends(get_neurostack_agent)
):
    result = await agent.process(request["query"])
    return {"result": result}
```

### Pattern 2: Standalone Application

For standalone applications:

```python
import asyncio
from src.neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

class MyApplication:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.reasoning_engine = ReasoningEngine(model="gpt-4")
        self.tool_registry = ToolRegistry()
        self.agent = None
    
    async def initialize(self):
        # Register your tools
        self.tool_registry.register_tool(MyCustomTool())
        
        # Create agent
        self.agent = Agent(
            name="my_app_agent",
            memory_manager=self.memory_manager,
            reasoning_engine=self.reasoning_engine,
            tool_registry=self.tool_registry
        )
    
    async def process_request(self, request: str):
        return await self.agent.process(request)

# Usage
async def main():
    app = MyApplication()
    await app.initialize()
    
    result = await app.process_request("Process this data")
    print(result)

asyncio.run(main())
```

### Pattern 3: Multi-Agent System

For complex systems with multiple agents:

```python
from src.neurostack.core.agents import AgentOrchestrator, AgentConfig

class MultiAgentSystem:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.memory_manager = MemoryManager()
        self.reasoning_engine = ReasoningEngine(model="gpt-4")
    
    async def setup_agents(self):
        # Create specialized agents
        data_agent = Agent(
            AgentConfig(
                name="data_agent",
                description="Handles data processing",
                capabilities=["data_analysis", "data_cleaning"]
            ),
            memory_manager=self.memory_manager,
            reasoning_engine=self.reasoning_engine
        )
        
        customer_agent = Agent(
            AgentConfig(
                name="customer_agent", 
                description="Handles customer interactions",
                capabilities=["customer_service", "verification"]
            ),
            memory_manager=self.memory_manager,
            reasoning_engine=self.reasoning_engine
        )
        
        # Add to orchestrator
        self.orchestrator.add_agent(data_agent)
        self.orchestrator.add_agent(customer_agent)
    
    async def process_complex_request(self, request: str):
        return await self.orchestrator.process(request)
```

## 🛠️ Creating Custom Tools

### Tool Structure

```python
from src.neurostack.core.tools import Tool, ToolResult
from typing import Dict, Any

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_custom_tool",
            description="Description of what this tool does",
            parameters={
                "param1": {
                    "type": "string",
                    "required": True,
                    "description": "Description of parameter"
                },
                "param2": {
                    "type": "integer", 
                    "required": False,
                    "default": 10,
                    "description": "Optional parameter"
                }
            }
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        try:
            # Your tool logic here
            param1 = parameters["param1"]
            param2 = parameters.get("param2", 10)
            
            # Process the request
            result = await self.process_data(param1, param2)
            
            return ToolResult(
                success=True,
                data=result,
                metadata={
                    "processing_time": 0.5,
                    "source": "my_custom_tool"
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"error_type": type(e).__name__}
            )
    
    async def process_data(self, param1: str, param2: int):
        # Your actual processing logic
        return {"processed": param1, "count": param2}
```

### Tool Categories

1. **Data Tools**: Database queries, file operations, API calls
2. **Analysis Tools**: Data processing, calculations, reporting
3. **Communication Tools**: Email, messaging, notifications
4. **Integration Tools**: Third-party service connections
5. **Decision Tools**: Business logic, rule engines

## 🧠 Memory Patterns

### Pattern 1: Customer Profile Memory

```python
class CustomerMemoryManager:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.vector_memory = memory_manager.get_vector_memory()
        self.long_term_memory = memory_manager.get_long_term_memory()
    
    async def store_customer_profile(self, customer_data: dict):
        # Store in vector memory for semantic search
        embedding = await self.create_embedding(customer_data)
        await self.vector_memory.store_embedding(
            f"customer_{customer_data['id']}", 
            embedding,
            metadata=customer_data
        )
        
        # Store in long-term memory for persistence
        await self.long_term_memory.store(
            f"customer_profile_{customer_data['id']}",
            customer_data
        )
    
    async def search_similar_customers(self, query: str, limit: int = 5):
        return await self.vector_memory.search(query, limit=limit)
    
    async def get_customer_history(self, customer_id: str):
        return await self.long_term_memory.get(f"customer_profile_{customer_id}")
```

### Pattern 2: Query Pattern Memory

```python
class QueryPatternMemory:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.working_memory = memory_manager.get_working_memory()
        self.vector_memory = memory_manager.get_vector_memory()
    
    async def store_query_pattern(self, query: str, result: dict, user_id: str):
        # Store in working memory for recent patterns
        self.working_memory.store(
            f"recent_query_{user_id}",
            {"query": query, "result": result, "timestamp": datetime.now()}
        )
        
        # Store in vector memory for similarity search
        embedding = await self.create_embedding(query)
        await self.vector_memory.store_embedding(
            f"query_pattern_{user_id}_{datetime.now().timestamp()}",
            embedding,
            metadata={"query": query, "user_id": user_id}
        )
    
    async def find_similar_queries(self, query: str, user_id: str, limit: int = 5):
        return await self.vector_memory.search(
            query, 
            limit=limit,
            filter_metadata={"user_id": user_id}
        )
```

## 🔐 Security and Best Practices

### 1. Environment Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

class NeuroStackConfig:
    def __init__(self):
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
        self.cosmos_db_connection = os.getenv("AZURE_COSMOS_DB_CONNECTION_STRING")
        
        # Validate required config
        if not all([self.azure_openai_endpoint, self.azure_openai_key]):
            raise ValueError("Missing required Azure OpenAI configuration")
```

### 2. Error Handling

```python
class SafeNeuroStackAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
    
    async def safe_process(self, request: str):
        try:
            return await self.agent.process(request)
        except Exception as e:
            logger.error(f"Agent processing failed: {str(e)}")
            return {
                "success": False,
                "error": "Processing failed",
                "fallback_response": "I'm having trouble processing that request."
            }
```

### 3. Rate Limiting

```python
import asyncio
from datetime import datetime, timedelta

class RateLimitedAgent:
    def __init__(self, agent: Agent, max_requests_per_minute: int = 60):
        self.agent = agent
        self.max_requests = max_requests_per_minute
        self.request_times = []
    
    async def process(self, request: str):
        # Check rate limit
        now = datetime.now()
        self.request_times = [t for t in self.request_times if now - t < timedelta(minutes=1)]
        
        if len(self.request_times) >= self.max_requests:
            raise Exception("Rate limit exceeded")
        
        self.request_times.append(now)
        return await self.agent.process(request)
```

## 🧪 Testing Your NeuroStack Integration

### 1. Unit Tests

```python
import pytest
from src.neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

class TestNeuroStackIntegration:
    @pytest.fixture
    async def agent(self):
        memory_manager = MemoryManager()
        reasoning_engine = ReasoningEngine(model="gpt-4")
        tool_registry = ToolRegistry()
        
        return Agent(
            name="test_agent",
            memory_manager=memory_manager,
            reasoning_engine=reasoning_engine,
            tool_registry=tool_registry
        )
    
    async def test_agent_initialization(self, agent):
        assert agent.name == "test_agent"
        assert agent.memory_manager is not None
        assert agent.reasoning_engine is not None
    
    async def test_agent_processing(self, agent):
        result = await agent.process("Hello")
        assert result is not None
        assert "response" in result
```

### 2. Integration Tests

```python
class TestFullIntegration:
    async def test_end_to_end_workflow(self):
        # Setup
        app = MyApplication()
        await app.initialize()
        
        # Test workflow
        result1 = await app.process_request("Store customer data")
        assert result1["success"] == True
        
        result2 = await app.process_request("Retrieve customer data")
        assert result2["success"] == True
        assert "customer_data" in result2
```

## 📊 Monitoring and Observability

### 1. Logging

```python
import logging
from src.neurostack.core.agents import Agent

class MonitoredAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"neurostack.agent.{self.name}")
    
    async def process(self, request: str):
        self.logger.info(f"Processing request: {request[:100]}...")
        start_time = time.time()
        
        try:
            result = await super().process(request)
            processing_time = time.time() - start_time
            
            self.logger.info(f"Request processed successfully in {processing_time:.2f}s")
            return result
        
        except Exception as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise
```

### 2. Metrics

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: datetime = None

class MetricsCollector:
    def __init__(self):
        self.metrics = {}
    
    def record_request(self, agent_name: str, success: bool, response_time: float):
        if agent_name not in self.metrics:
            self.metrics[agent_name] = AgentMetrics()
        
        metrics = self.metrics[agent_name]
        metrics.total_requests += 1
        metrics.last_request_time = datetime.now()
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # Update average response time
        total_time = metrics.average_response_time * (metrics.total_requests - 1) + response_time
        metrics.average_response_time = total_time / metrics.total_requests
```

## 🚀 Deployment Patterns

### 1. Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: neurostack-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: neurostack-app
  template:
    metadata:
      labels:
        app: neurostack-app
    spec:
      containers:
      - name: neurostack-app
        image: neurostack-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: neurostack-secrets
              key: azure-openai-endpoint
        - name: AZURE_OPENAI_KEY
          valueFrom:
            secretKeyRef:
              name: neurostack-secrets
              key: azure-openai-key
```

## 📚 Common Use Cases

### 1. Customer Service Agent

```python
class CustomerServiceAgent:
    def __init__(self):
        self.agent = Agent(
            name="customer_service",
            memory_manager=MemoryManager(),
            reasoning_engine=ReasoningEngine(model="gpt-4"),
            tool_registry=ToolRegistry()
        )
        
        # Register customer service tools
        self.agent.tool_registry.register_tool(CustomerLookupTool())
        self.agent.tool_registry.register_tool(OrderStatusTool())
        self.agent.tool_registry.register_tool(RefundTool())
    
    async def handle_inquiry(self, customer_id: str, inquiry: str):
        context = f"Customer {customer_id} inquiry: {inquiry}"
        return await self.agent.process(context)
```

### 2. Data Analysis Agent

```python
class DataAnalysisAgent:
    def __init__(self):
        self.agent = Agent(
            name="data_analyst",
            memory_manager=MemoryManager(),
            reasoning_engine=ReasoningEngine(model="gpt-4"),
            tool_registry=ToolRegistry()
        )
        
        # Register data analysis tools
        self.agent.tool_registry.register_tool(DataQueryTool())
        self.agent.tool_registry.register_tool(StatisticalAnalysisTool())
        self.agent.tool_registry.register_tool(VisualizationTool())
    
    async def analyze_data(self, dataset: str, analysis_type: str):
        context = f"Analyze {dataset} using {analysis_type}"
        return await self.agent.process(context)
```

### 3. Content Generation Agent

```python
class ContentGenerationAgent:
    def __init__(self):
        self.agent = Agent(
            name="content_generator",
            memory_manager=MemoryManager(),
            reasoning_engine=ReasoningEngine(model="gpt-4"),
            tool_registry=ToolRegistry()
        )
        
        # Register content tools
        self.agent.tool_registry.register_tool(ResearchTool())
        self.agent.tool_registry.register_tool(PlagiarismCheckTool())
        self.agent.tool_registry.register_tool(SEOOptimizationTool())
    
    async def generate_content(self, topic: str, content_type: str):
        context = f"Generate {content_type} about {topic}"
        return await self.agent.process(context)
```

## 🔄 Migration Guide

### From Simple AI to NeuroStack

If you're migrating from a simple AI implementation:

```python
# Before: Simple OpenAI call
import openai

def simple_ai_response(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# After: NeuroStack with memory and tools
from src.neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

class EnhancedAI:
    def __init__(self):
        self.agent = Agent(
            name="enhanced_ai",
            memory_manager=MemoryManager(),
            reasoning_engine=ReasoningEngine(model="gpt-4"),
            tool_registry=ToolRegistry()
        )
    
    async def enhanced_response(self, prompt: str, user_id: str):
        # Add context from memory
        user_history = await self.agent.memory_manager.get_user_history(user_id)
        enhanced_prompt = f"User history: {user_history}\nCurrent request: {prompt}"
        
        return await self.agent.process(enhanced_prompt)
```

## 🆘 Troubleshooting

### Common Issues

1. **Memory Initialization Failed**
   ```python
   # Check your Cosmos DB connection string
   AZURE_COSMOS_DB_CONNECTION_STRING=your_connection_string
   ```

2. **Tool Registration Failed**
   ```python
   # Ensure your tool inherits from Tool base class
   class MyTool(Tool):
       def __init__(self):
           super().__init__(name="my_tool", description="...")
   ```

3. **Reasoning Engine Timeout**
   ```python
   # Increase timeout for complex reasoning
   reasoning_engine = ReasoningEngine(
       model="gpt-4",
       timeout=30  # 30 seconds
   )
   ```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Create agent with debug mode
agent = Agent(
    name="debug_agent",
    debug=True,  # Enable debug mode
    memory_manager=MemoryManager(),
    reasoning_engine=ReasoningEngine(model="gpt-4"),
    tool_registry=ToolRegistry()
)
```

## 📞 Support and Resources

### Documentation
- [NeuroStack API Reference](link-to-api-docs)
- [Integration Examples](link-to-examples)
- [Best Practices Guide](link-to-best-practices)

### Community
- [GitHub Issues](link-to-github)
- [Discord Community](link-to-discord)
- [Stack Overflow](link-to-stackoverflow)

### Training
- [NeuroStack Academy](link-to-academy)
- [Video Tutorials](link-to-tutorials)
- [Workshop Materials](link-to-workshops)

---

**🎉 Congratulations!** You're now ready to build intelligent, memory-enabled AI agents with NeuroStack. Start with the quick start guide and gradually explore the advanced features as your needs grow.

**Remember**: NeuroStack is designed to be modular - you can start simple and add complexity as needed. The key is to begin with a clear understanding of your use case and build incrementally.
