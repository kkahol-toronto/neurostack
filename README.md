# NeuroStack

A Python library implementing the NeuroStack 8-layer agentic AI architecture, designed for building sophisticated multi-agent systems with advanced reasoning, memory, and orchestration capabilities.

## 🏗️ Architecture Overview

NeuroStack implements an 8-layer architecture for agentic AI systems:

1. **Infrastructure Layer** - Cloud services and infrastructure management
2. **Agent Internet Layer** - Network connectivity and communication protocols
3. **Protocol Layer** - Standardized communication (MCP, A2A)
4. **Tooling & Enrichment Layer** - External tool integration and data enrichment
5. **Cognition & Reasoning Layer** - LLM integration and decision-making
6. **Memory & Personalization Layer** - Short-term, long-term, and vector memory
7. **Application Layer** - Business logic and use case implementations
8. **Operations & Governance Layer** - Monitoring, logging, and governance

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd neurostack
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   
   **On macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```
   
   **On Windows:**
   ```bash
   venv\Scripts\activate
   ```

4. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

### Running the Example

1. **Make sure your virtual environment is activated:**
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Run the basic example:**
   ```bash
   python examples/simple_agent_example.py
   ```

3. **Run the Azure integration example:**
   ```bash
   # Install Azure dependencies
   pip install -e .[azure]
   
   # Run the example
   python examples/azure_integration_example.py
   ```

4. **Run the GCP integration example:**
   ```bash
   # Install GCP dependencies
   pip install -e .[gcp]
   
   # Run the example
   python examples/gcp_integration_example.py
   ```

5. **Test your cloud setup:**
   ```bash
   # Test Azure APIM setup
   python examples/test_apim_setup.py
   
   # Test GCP setup
   python examples/test_gcp_setup.py
   ```

You should see output similar to:
```
🚀 Starting NeuroStack Simple Example
📊 Registered agents: ['data_analyst', 'report_generator']

🔄 Running simple workflow...

✅ Workflow completed with state: completed

📋 Results:
  analyze_data: Analysis completed for: Analyze sales data for Q4 2023
  generate_report: Report generated: Generate quarterly sales report based on Analysis completed for: Analyze sales data for Q4 2023

📊 System Status:
  Agents: 2
  Workflows: 1

🎉 Example completed successfully!
```

## 📚 Usage Examples

### Basic Agent Creation

```python
from neurostack import AgentConfig, SimpleAgent, AgentOrchestrator

# Create an agent configuration
config = AgentConfig(
    name="my_agent",
    description="A custom agent for specific tasks",
    model="gpt-4",
    memory_enabled=True,
    reasoning_enabled=True
)

# Create the agent
agent = SimpleAgent(config)

# Create an orchestrator
orchestrator = AgentOrchestrator()

# Register the agent
orchestrator.register_agent("my_agent", agent)
```

### Running a Simple Workflow

```python
import asyncio
from neurostack import AgentOrchestrator, AgentContext

async def run_workflow():
    orchestrator = AgentOrchestrator()
    
    # Define workflow steps
    workflow_steps = [
        {
            "id": "step1",
            "agent": "agent1",
            "task": "Process data"
        },
        {
            "id": "step2", 
            "agent": "agent2",
            "task": "Generate report based on {step.step1}",
            "dependencies": ["step1"]
        }
    ]
    
    # Create context
    context = AgentContext(
        user_id="user123",
        tenant_id="tenant456"
    )
    
    # Run the workflow
    result = await orchestrator.run_simple_workflow(workflow_steps, context)
    
    print(f"Workflow completed: {result.state}")
    print(f"Results: {result.results}")

# Run the workflow
asyncio.run(run_workflow())
```

## 🏛️ Core Components

### Agents
- **Agent**: Abstract base class for all agents
- **SimpleAgent**: Basic agent implementation
- **AgentConfig**: Configuration for agent behavior
- **AgentContext**: Execution context and metadata

### Orchestration
- **AgentOrchestrator**: Manages multi-agent workflows
- **WorkflowDefinition**: Defines workflow structure
- **WorkflowStep**: Individual steps in a workflow

### Memory
- **MemoryManager**: Unified memory interface
- **WorkingMemory**: Short-term, fast-access memory
- **VectorMemory**: Semantic search capabilities
- **LongTermMemory**: Persistent storage

### Reasoning
- **ReasoningEngine**: LLM integration and decision-making
- **LLMClient**: Abstract interface for language models
- **OpenAIClient**: OpenAI GPT integration
- **AnthropicClient**: Anthropic Claude integration

### Tools
- **Tool**: Abstract base class for tools
- **ToolRegistry**: Tool management and discovery
- **SimpleTool**: Basic tool implementations

### Protocols
- **MCPProtocol**: Model Context Protocol implementation
- **A2AProtocol**: Agent-to-Agent communication

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# GCP Configuration (for cloud integrations)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GCP_PROJECT_ID=your_project_id

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/neurostack

# Redis Configuration
REDIS_URL=redis://localhost:6379
```

### Agent Configuration

```python
from neurostack import AgentConfig

config = AgentConfig(
    name="custom_agent",
    description="A custom agent for specific tasks",
    model="gpt-4",                    # LLM model to use
    temperature=0.7,                  # Creativity level (0.0-1.0)
    max_tokens=1000,                  # Maximum response length
    memory_enabled=True,              # Enable memory features
    reasoning_enabled=True,           # Enable reasoning engine
    tenant_id="tenant123",           # Multi-tenant support
    tools=["calculator", "web_search"] # Available tools
)
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=neurostack tests/
```

## 📦 Development

### Project Structure

```
neurostack/
├── src/neurostack/           # Main package source
│   ├── core/                # Core components
│   │   ├── agents/          # Agent implementations
│   │   ├── memory/          # Memory management
│   │   ├── reasoning/       # Reasoning engine
│   │   ├── tools/           # Tool system
│   │   └── protocols/       # Communication protocols
│   ├── layers/              # 8-layer architecture
│   ├── integrations/        # Cloud integrations
│   └── utils/               # Utilities
├── examples/                # Usage examples
├── tests/                   # Test suite
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Adding New Components

1. **Create a new agent:**
   ```python
   from neurostack import Agent, AgentConfig
   
   class CustomAgent(Agent):
       async def execute(self, task, context=None):
           # Your custom logic here
           return result
   ```

2. **Add new tools:**
   ```python
   from neurostack import Tool
   
   class CustomTool(Tool):
       def __init__(self):
           super().__init__("custom_tool", "Description")
       
       async def execute(self, *args, **kwargs):
           # Tool implementation
           return result
   ```

3. **Extend memory:**
   ```python
   from neurostack import MemoryManager
   
   class CustomMemory(MemoryManager):
       async def store_knowledge(self, content, metadata):
           # Custom storage logic
           pass
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions for questions and ideas

## 🗺️ Roadmap

- [ ] Complete 8-layer architecture implementation
- [ ] GCP integration (Vertex AI, Cloud Run, etc.)
- [ ] LangGraph compatibility layer
- [ ] Advanced memory systems (vector databases)
- [ ] Real-time agent communication
- [ ] Web UI for workflow management
- [ ] Performance monitoring and analytics
- [ ] Enterprise features (RBAC, audit logs)

---

**NeuroStack** - Building the future of agentic AI systems 🚀 