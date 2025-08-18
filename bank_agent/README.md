# Banking Agent

A comprehensive banking agent application with a React frontend and FastAPI backend, featuring Azure OpenAI-powered text-to-SQL capabilities.

## 🏗️ Architecture

```
bank_agent/
├── frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   └── data/          # Data sources
│   └── package.json
├── backend/           # FastAPI Python backend
│   ├── main.py        # FastAPI application
│   ├── start.py       # Startup script
│   ├── test_api.py    # API testing
│   ├── requirements.txt
│   └── .env           # Environment variables
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 16+** and **npm** (for frontend)
- **Python 3.8+** and **pip** (for backend)
- **Azure OpenAI** account and deployment

### 1. Backend Setup

```bash
cd bank_agent/backend

# Run setup script
./setup.sh

# Update .env with your Azure OpenAI credentials
# Edit .env file with your actual values

# Start the backend
python start.py
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
```

## 🎨 Features

### Frontend (React + TypeScript)
- 🎨 **Matrix-style UI** - Green and black cyberpunk theme
- 📊 **Data Source Management** - Toggle and manage data sources
- 🔍 **Natural Language Queries** - Convert text to SQL
- 📱 **Responsive Design** - Works on desktop and mobile
- ⚡ **Real-time Updates** - Live data source status

### Backend (FastAPI + Azure OpenAI)
- 🤖 **Text-to-SQL Conversion** - Using latest Azure OpenAI SDK
- 🔄 **CORS Support** - Seamless frontend integration
- 📊 **Mock Database** - Demo data for testing
- 🔍 **Health Monitoring** - API health checks
- 📚 **Auto-generated Docs** - Interactive API documentation

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Frontend Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

## 📊 Data Sources

The application includes mock data for:

- **Customer Demographics** - Basic customer information
- **Internal Banking Data** - Banking relationship data
- **Credit Bureau Data** - External credit information
- **Income & Ability-to-Pay** - Income verification data
- **Open Banking Data** - Transaction data
- **Fraud/KYC/Compliance** - Risk assessment data
- **Economic Indicators** - Regional economic data

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Data Endpoints
- `GET /api/datasources` - Get available data sources
- `GET /api/sample/{table_name}` - Get sample data

### Text-to-SQL Endpoints
- `POST /api/text-to-sql` - Convert natural language to SQL
- `POST /api/query` - Execute SQL query

## 🧪 Testing

### Backend Testing
```bash
cd bank_agent/backend
python test_api.py
```

### Frontend Testing
```bash
cd bank_agent/frontend
npm test
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Azure OpenAI credentials in `.env`
   - Ensure port 8000 is available
   - Verify Python dependencies are installed

2. **Frontend can't connect to backend**
   - Ensure backend is running on port 8000
   - Check CORS configuration
   - Verify API_BASE_URL in frontend

3. **Text-to-SQL not working**
   - Verify Azure OpenAI deployment is active
   - Check API key and endpoint URL
   - Ensure deployment name is correct

### Debug Mode

Set `DEBUG=true` in backend `.env` for:
- Auto-reload on code changes
- Detailed error messages
- Development logging

## 🚀 Deployment

### Backend Deployment
```bash
# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker (if Dockerfile is added)
docker build -t banking-agent-backend .
docker run -p 8000:8000 --env-file .env banking-agent-backend
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve with static server
npm install -g serve
serve -s build
```

## 📝 Development

### Adding New Features

1. **Backend**: Add new endpoints in `main.py`
2. **Frontend**: Create new components in `src/components/`
3. **Types**: Update TypeScript interfaces in `src/types/`
4. **Testing**: Add tests for new functionality

### Code Style

- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: Use TypeScript strict mode
- **API**: Follow RESTful conventions
- **Documentation**: Update README files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is part of the NeuroStack Banking Agent application.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check the test results
4. Open an issue with detailed error information
