# 🧠 NeuroStack Quick Reference

## 🚀 5-Minute Setup

> **Note**: NeuroStack is currently a local library under development. It's not yet published to PyPI. We're focusing on building a complete, stable implementation before any public release.

```python
# 1. Clone and import
git clone https://github.com/kkahol-toronto/neurostack.git
cd neurostack
pip install -e .

# Import from local library
from src.neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

# 2. Initialize components
memory_manager = MemoryManager()
reasoning_engine = ReasoningEngine(model="gpt-4")
tool_registry = ToolRegistry()

# 3. Create agent
agent = Agent(
    name="my_agent",
    memory_manager=memory_manager,
    reasoning_engine=reasoning_engine,
    tool_registry=tool_registry
)

# 4. Use it
response = await agent.process("Hello, how can you help me?")
```

## 🔧 Common Integration Patterns

### FastAPI Integration
```python
from fastapi import FastAPI, Depends
from neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

app = FastAPI()
neurostack_agent = None

async def get_agent():
    global neurostack_agent
    if neurostack_agent is None:
        memory_manager = MemoryManager()
        reasoning_engine = ReasoningEngine(model="gpt-4")
        tool_registry = ToolRegistry()
        
        neurostack_agent = Agent(
            name="api_agent",
            memory_manager=memory_manager,
            reasoning_engine=reasoning_engine,
            tool_registry=tool_registry
        )
    return neurostack_agent

@app.post("/api/process")
async def process_request(request: dict, agent: Agent = Depends(get_agent)):
    return await agent.process(request["query"])
```

### Standalone Application
```python
import asyncio
from neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

class MyApp:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.reasoning_engine = ReasoningEngine(model="gpt-4")
        self.tool_registry = ToolRegistry()
        self.agent = None
    
    async def initialize(self):
        self.agent = Agent(
            name="my_app_agent",
            memory_manager=self.memory_manager,
            reasoning_engine=self.reasoning_engine,
            tool_registry=self.tool_registry
        )
    
    async def process(self, request: str):
        return await self.agent.process(request)

# Usage
async def main():
    app = MyApp()
    await app.initialize()
    result = await app.process("Process this data")
    print(result)

asyncio.run(main())
```

## 🛠️ Creating Custom Tools

```python
from neurostack.core.tools import Tool, ToolResult

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="What this tool does",
            parameters={
                "param1": {"type": "string", "required": True},
                "param2": {"type": "integer", "required": False, "default": 10}
            }
        )
    
    async def execute(self, parameters: dict) -> ToolResult:
        try:
            param1 = parameters["param1"]
            param2 = parameters.get("param2", 10)
            
            # Your logic here
            result = await self.process_data(param1, param2)
            
            return ToolResult(
                success=True,
                data=result,
                metadata={"source": "my_tool"}
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

# Register and use
tool_registry.register_tool(MyCustomTool())
tool = tool_registry.get_tool("my_tool")
result = await tool.execute({"param1": "test"})
```

## 🧠 Memory Patterns

### Customer Profile Memory
```python
class CustomerMemory:
    def __init__(self, memory_manager):
        self.vector_memory = memory_manager.get_vector_memory()
        self.long_term_memory = memory_manager.get_long_term_memory()
    
    async def store_customer(self, customer_data: dict):
        # Vector memory for semantic search
        embedding = await self.create_embedding(customer_data)
        await self.vector_memory.store_embedding(
            f"customer_{customer_data['id']}", 
            embedding,
            metadata=customer_data
        )
        
        # Long-term memory for persistence
        await self.long_term_memory.store(
            f"customer_{customer_data['id']}",
            customer_data
        )
    
    async def search_customers(self, query: str, limit: int = 5):
        return await self.vector_memory.search(query, limit=limit)
```

### Query Pattern Memory
```python
class QueryMemory:
    def __init__(self, memory_manager):
        self.working_memory = memory_manager.get_working_memory()
        self.vector_memory = memory_manager.get_vector_memory()
    
    async def store_query(self, query: str, result: dict, user_id: str):
        # Working memory for recent queries
        self.working_memory.store(
            f"recent_{user_id}",
            {"query": query, "result": result, "timestamp": datetime.now()}
        )
        
        # Vector memory for similarity search
        embedding = await self.create_embedding(query)
        await self.vector_memory.store_embedding(
            f"query_{user_id}_{datetime.now().timestamp()}",
            embedding,
            metadata={"query": query, "user_id": user_id}
        )
    
    async def find_similar(self, query: str, user_id: str, limit: int = 5):
        return await self.vector_memory.search(
            query, 
            limit=limit,
            filter_metadata={"user_id": user_id}
        )
```

## 🔐 Security Patterns

### Environment Configuration
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
        self.cosmos_db_connection = os.getenv("AZURE_COSMOS_DB_CONNECTION_STRING")
        
        if not all([self.azure_openai_endpoint, self.azure_openai_key]):
            raise ValueError("Missing required configuration")
```

### Error Handling
```python
class SafeAgent:
    def __init__(self, agent):
        self.agent = agent
    
    async def safe_process(self, request: str):
        try:
            return await self.agent.process(request)
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return {
                "success": False,
                "error": "Processing failed",
                "fallback": "I'm having trouble with that request."
            }
```

## 🧪 Testing Patterns

### Unit Tests
```python
import pytest
from neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

class TestNeuroStack:
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
    
    async def test_agent_works(self, agent):
        result = await agent.process("Hello")
        assert result is not None
        assert "response" in result
```

### Integration Tests
```python
class TestIntegration:
    async def test_full_workflow(self):
        app = MyApplication()
        await app.initialize()
        
        result = await app.process("Test request")
        assert result["success"] == True
```

## 📊 Monitoring Patterns

### Logging
```python
import logging
from neurostack.core.agents import Agent

class MonitoredAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"neurostack.agent.{self.name}")
    
    async def process(self, request: str):
        self.logger.info(f"Processing: {request[:100]}...")
        start_time = time.time()
        
        try:
            result = await super().process(request)
            processing_time = time.time() - start_time
            self.logger.info(f"Success in {processing_time:.2f}s")
            return result
        except Exception as e:
            self.logger.error(f"Failed: {str(e)}")
            raise
```

### Metrics
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0

class MetricsCollector:
    def __init__(self):
        self.metrics = {}
    
    def record_request(self, agent_name: str, success: bool, response_time: float):
        if agent_name not in self.metrics:
            self.metrics[agent_name] = AgentMetrics()
        
        metrics = self.metrics[agent_name]
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # Update average
        total_time = metrics.average_response_time * (metrics.total_requests - 1) + response_time
        metrics.average_response_time = total_time / metrics.total_requests
```

## 🚀 Deployment Patterns

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes
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
```

## 📚 Common Use Cases

### Customer Service Agent
```python
class CustomerServiceAgent:
    def __init__(self):
        self.agent = Agent(
            name="customer_service",
            memory_manager=MemoryManager(),
            reasoning_engine=ReasoningEngine(model="gpt-4"),
            tool_registry=ToolRegistry()
        )
        
        # Register tools
        self.agent.tool_registry.register_tool(CustomerLookupTool())
        self.agent.tool_registry.register_tool(OrderStatusTool())
    
    async def handle_inquiry(self, customer_id: str, inquiry: str):
        context = f"Customer {customer_id} inquiry: {inquiry}"
        return await self.agent.process(context)
```

### Data Analysis Agent
```python
class DataAnalysisAgent:
    def __init__(self):
        self.agent = Agent(
            name="data_analyst",
            memory_manager=MemoryManager(),
            reasoning_engine=ReasoningEngine(model="gpt-4"),
            tool_registry=ToolRegistry()
        )
        
        # Register tools
        self.agent.tool_registry.register_tool(DataQueryTool())
        self.agent.tool_registry.register_tool(StatisticalAnalysisTool())
    
    async def analyze_data(self, dataset: str, analysis_type: str):
        context = f"Analyze {dataset} using {analysis_type}"
        return await self.agent.process(context)
```

## 🔄 Migration from Simple AI

```python
# Before: Simple OpenAI
import openai

def simple_ai_response(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# After: NeuroStack with memory
from neurostack import Agent, MemoryManager, ReasoningEngine, ToolRegistry

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
   # Check Cosmos DB connection
   AZURE_COSMOS_DB_CONNECTION_STRING=your_connection_string
   ```

2. **Tool Registration Failed**
   ```python
   # Ensure proper inheritance
   class MyTool(Tool):
       def __init__(self):
           super().__init__(name="my_tool", description="...")
   ```

3. **Reasoning Engine Timeout**
   ```python
   # Increase timeout
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

## 📋 Environment Variables

```bash
# Required
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional (for memory)
AZURE_COSMOS_DB_CONNECTION_STRING=your_cosmos_db_connection

# Optional (for APIM)
AZURE_COGNITIVE_SERVICES_ENDPOINT=your_apim_endpoint
AZURE_COGNITIVE_SERVICES_KEY=your_apim_key
```

## 🎯 Key Takeaways

1. **Start Simple**: Begin with basic agent setup, add complexity gradually
2. **Use Memory**: Leverage working, vector, and long-term memory for context
3. **Create Tools**: Build custom tools for your specific use cases
4. **Handle Errors**: Implement proper error handling and fallbacks
5. **Monitor Performance**: Add logging and metrics for observability
6. **Test Thoroughly**: Write unit and integration tests
7. **Secure Configuration**: Use environment variables for sensitive data

---

**💡 Pro Tip**: NeuroStack is modular - you can start with just the reasoning engine and add memory and tools as your needs grow!
