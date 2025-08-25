# 🏦 Banking Agent - NeuroStack-Powered AI Banking Assistant

A comprehensive banking agent application that demonstrates the full power of NeuroStack. This intelligent banking assistant uses AI-powered reasoning, memory management, and multi-step investigation workflows to make informed credit decisions.

## 🧠 NeuroStack Integration

The Banking Agent is built entirely on NeuroStack, showcasing how to create enterprise-grade AI applications with:

- **🧠 Intelligent Reasoning**: AI-powered credit risk assessment and decision making
- **💾 Memory Management**: Customer profiles, transaction history, and decision logs
- **🔧 Tool Registry**: Data analysis, email generation, and report creation
- **🤖 Agent Orchestration**: Multi-step investigation workflows
- **📊 Rich Visualizations**: Interactive data analysis and reporting

### **NeuroStack Components Used**

| Component | Usage | Description |
|-----------|-------|-------------|
| **Memory Manager** | Customer profiles, transaction history, decision logs | Stores and retrieves customer data, investigation results, and decision documentation |
| **Reasoning Engine** | Credit risk assessment, fraud detection, decision making | Uses Azure OpenAI to analyze customer data and make intelligent decisions |
| **Tool Registry** | Data analysis, email generation, report creation | Extensible tools for processing banking data and generating reports |
| **Agent Orchestration** | Multi-step investigation workflows | Coordinates complex investigation processes with multiple steps |
| **Vector Memory** | Semantic search and similarity matching | Finds similar customer profiles and historical decisions |

## 🏗️ Architecture

```
bank_agent/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Dashboard.tsx           # Main dashboard with session management
│   │   │   ├── DataSimulationStudio.tsx # AI-powered investigation studio
│   │   │   ├── DecisionDocumentation.tsx # Decision documentation viewer
│   │   │   └── ...           # Other UI components
│   │   ├── services/         # API services
│   │   ├── types/            # TypeScript types
│   │   └── themes/           # Theme management
│   └── package.json
├── backend/                  # FastAPI Python backend with NeuroStack
│   ├── main.py              # FastAPI application with NeuroStack integration
│   ├── investigation_service.py # Core investigation logic using NeuroStack
│   ├── neurostack_integration.py # NeuroStack component integration
│   ├── neurostack_memory.py # Memory management with NeuroStack
│   ├── neurostack_tools.py  # Custom tools for banking operations
│   ├── models.py            # Data models
│   ├── requirements.txt
│   └── .env                 # Environment variables
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 16+** and **npm** (for frontend)
- **Python 3.8+** and **pip** (for backend)
- **Azure OpenAI** account and deployment
- **Azure CosmosDB** (optional, for persistent memory)

### 1. Backend Setup

```bash
cd bank_agent/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp ../env.template .env

# Update .env with your Azure OpenAI credentials
# Edit .env file with your actual values

# Start the backend
python main.py
```

The backend will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### 2. Frontend Setup

```bash
cd bank_agent/frontend

# Install dependencies
npm install

# Start the frontend
npm start
```

The frontend will be available at:
- **App**: http://localhost:3000

### 3. Test the Integration

```bash
# Test backend API
cd bank_agent/backend
python test_api.py

# Test NeuroStack integration
python test_neurostack_integration.py
```

## 🎨 Features

### **Frontend (React + TypeScript)**

#### **🎨 Modern UI with Theme Support**
- **Multiple Themes**: Corporate, Matrix, Vibrant, Readable themes
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live data source status and investigation progress
- **Interactive Components**: Drag-and-drop, real-time charts, and visualizations

#### **📊 Data Simulation & Visualization Studio**
- **AI-Powered Investigation**: Multi-step investigation workflows
- **Interactive Visualizations**: Charts, graphs, and data analysis
- **Real-time Progress**: Live investigation status and progress tracking
- **Decision Documentation**: Comprehensive decision reports and audit trails

#### **🔍 Customer Management**
- **Customer Search**: Find and select customers for investigation
- **Profile Management**: View customer demographics and financial data
- **Session Management**: Track investigation sessions and results
- **Decision History**: View past decisions and reasoning

### **Backend (FastAPI + NeuroStack)**

#### **🧠 NeuroStack-Powered Intelligence**
- **AI Reasoning Engine**: Uses Azure OpenAI for intelligent decision making
- **Memory Management**: Customer profiles, transaction history, decision logs
- **Tool Registry**: Extensible tools for data analysis and reporting
- **Agent Orchestration**: Multi-step investigation workflows

#### **🏦 Banking-Specific Features**
- **Credit Risk Assessment**: AI-powered credit limit decisions
- **Fraud Detection**: Pattern recognition and anomaly detection
- **Customer Profiling**: Comprehensive customer analysis
- **Decision Documentation**: Automated report generation

#### **📊 Data Management**
- **Mock Databases**: Comprehensive demo data for testing
- **Real-time Processing**: Live data analysis and visualization
- **Audit Trails**: Complete decision documentation and reasoning
- **Email Integration**: Automated customer communication

## 🔧 Configuration

### **Backend Environment Variables (.env)**

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional: Azure CosmosDB for persistent memory
AZURE_COSMOS_DB_CONNECTION_STRING=your_cosmos_db_connection_string

# Optional: APIM endpoints for load balancing
AZURE_COGNITIVE_SERVICES_ENDPOINT=your_apim_endpoint
AZURE_COGNITIVE_SERVICES_KEY=your_apim_key

# Application Configuration
RAG_MAX_CONTEXT_TOKENS=8000
SYSTEM_PROMPT=You are an intelligent banking assistant...
```

## 🧠 How NeuroStack Powers the Banking Agent

### **1. Memory Management**

The banking agent uses NeuroStack's multi-layered memory system:

```python
# Customer profile storage
await memory_manager.store_customer_profile(customer_id, profile_data)

# Transaction history
await memory_manager.store_transactions(customer_id, transactions)

# Decision logs
await memory_manager.store_decision(decision_id, decision_data)
```

### **2. AI-Powered Reasoning**

NeuroStack's reasoning engine powers intelligent decision making:

```python
# Credit risk assessment
risk_assessment = await reasoning_engine.assess_credit_risk(
    customer_data=customer_profile,
    transaction_history=transactions,
    credit_request=request_amount
)

# Fraud detection
fraud_analysis = await reasoning_engine.detect_fraud(
    customer_behavior=behavior_patterns,
    transaction_data=recent_transactions
)
```

### **3. Multi-Step Investigation Workflows**

NeuroStack's agent orchestration enables complex workflows:

```python
# Investigation workflow
investigation_steps = [
    "Basic Credit Profile Analysis",
    "Payment History Review", 
    "Income Verification",
    "Risk Assessment",
    "Decision Making"
]

results = await agent_orchestrator.execute_investigation(
    customer_id=customer_id,
    steps=investigation_steps,
    execution_mode="sequential"
)
```

### **4. Tool Registry**

Extensible tools for banking operations:

```python
# Register banking-specific tools
tool_registry.register_tool(CreditAnalysisTool())
tool_registry.register_tool(EmailGenerationTool())
tool_registry.register_tool(ReportGenerationTool())
tool_registry.register_tool(FraudDetectionTool())
```

## 📊 Key Features in Action

### **1. Intelligent Credit Decisions**

The banking agent uses NeuroStack to make intelligent credit decisions:

1. **Data Collection**: Gathers customer profile, transaction history, and credit bureau data
2. **AI Analysis**: Uses NeuroStack's reasoning engine to analyze risk factors
3. **Pattern Recognition**: Identifies patterns in customer behavior and similar cases
4. **Decision Making**: Generates intelligent credit recommendations
5. **Documentation**: Creates comprehensive decision documentation

### **2. Multi-Step Investigations**

Complex investigation workflows powered by NeuroStack:

1. **Investigation Planning**: AI generates investigation strategy based on request
2. **Step Execution**: Orchestrates multiple investigation steps
3. **Data Analysis**: Processes and analyzes customer data
4. **Risk Assessment**: Evaluates credit risk and fraud potential
5. **Decision Generation**: Creates final decision with reasoning
6. **Documentation**: Generates comprehensive reports

### **3. Memory-Enabled Interactions**

The agent remembers and learns from interactions:

- **Customer History**: Remembers past decisions and interactions
- **Pattern Learning**: Learns from similar cases and outcomes
- **Context Awareness**: Maintains conversation context across sessions
- **Audit Trails**: Complete documentation of all decisions and reasoning

## 🧪 Testing

### **Run All Tests**

```bash
cd bank_agent/backend

# Run all tests
python -m pytest

# Run specific test files
python test_neurostack_integration.py
python test_investigation_service.py
python test_memory_management.py
```

### **Test Coverage**

The banking agent includes comprehensive tests:

- **Unit Tests**: Individual component testing
- **Integration Tests**: NeuroStack integration testing
- **API Tests**: End-to-end API testing
- **Memory Tests**: Memory management testing
- **Tool Tests**: Custom tool functionality testing

## 🚀 Deployment

### **Docker Deployment**

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Kubernetes Deployment**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: banking-agent-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: banking-agent-backend
  template:
    metadata:
      labels:
        app: banking-agent-backend
    spec:
      containers:
      - name: banking-agent-backend
        image: banking-agent-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-secrets
              key: openai-endpoint
```

## 📚 Documentation

### **NeuroStack Integration**
- **[NEUROSTACK_INTEGRATION.md](backend/NEUROSTACK_INTEGRATION.md)** - Detailed integration guide
- **[neurostack_memory.py](backend/neurostack_memory.py)** - Memory management implementation
- **[neurostack_tools.py](backend/neurostack_tools.py)** - Custom tools implementation

### **API Documentation**
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

### **Frontend Documentation**
- **Component Library**: See `frontend/src/components/`
- **API Services**: See `frontend/src/services/`
- **Theme System**: See `frontend/src/themes/`

## 🎯 Use Cases

### **Credit Risk Assessment**
- **Customer Profiling**: Comprehensive customer analysis
- **Risk Scoring**: AI-powered risk assessment
- **Decision Making**: Intelligent credit limit decisions
- **Documentation**: Automated decision documentation

### **Fraud Detection**
- **Pattern Recognition**: Identify suspicious patterns
- **Anomaly Detection**: Detect unusual behavior
- **Risk Assessment**: Evaluate fraud potential
- **Alert Generation**: Automated fraud alerts

### **Customer Service**
- **Intelligent Chatbots**: Memory-enabled customer interactions
- **Personalized Responses**: Context-aware customer service
- **Issue Resolution**: AI-powered problem solving
- **Follow-up Management**: Automated follow-up processes

### **Compliance & Reporting**
- **Regulatory Compliance**: Automated compliance checking
- **Audit Trails**: Complete decision documentation
- **Report Generation**: Automated report creation
- **Data Governance**: Secure data handling

## 🔗 Related Documentation

- **[NeuroStack Main README](../README.md)** - Main NeuroStack documentation
- **[NeuroStack Developer Guide](../NEUROSTACK_DEVELOPER_GUIDE.md)** - Comprehensive development guide
- **[NeuroStack Quick Reference](../NEUROSTACK_QUICK_REFERENCE.md)** - Quick patterns and examples

## 🤝 Contributing

We welcome contributions to the Banking Agent! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- 📚 **Documentation**: Check our comprehensive guides
- 🐛 **Issues**: Report bugs on GitHub
- 💬 **Discussions**: Join our community discussions
- 📧 **Email**: Contact us for enterprise support

---

**🏦 Banking Agent** - Demonstrating the power of NeuroStack in real-world banking applications. 🧠✨
