# Credit Limit Agent Frontend

A React-based UI for the NeuroStack Credit Limit Agent that demonstrates data layer management and natural language query capabilities.

## 🚀 Features

- **Data Source Management**: Visual interface for selecting and configuring data sources
- **Natural Language Queries**: Convert natural language to SQL using Azure OpenAI
- **Interactive Cards**: Click to toggle, double-click to query data sources
- **Real-time Feedback**: Visual indicators for enabled/disabled data sources
- **Category Organization**: Data sources organized by banking categories
- **Query Results**: Display SQL queries and results in a user-friendly format

## 🛠️ Prerequisites

- Node.js 16+ and npm
- MySQL database with bank agent data (see `../data/README.md`)
- Azure OpenAI service configured

## 📦 Installation

### 1. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 2. Install Backend Dependencies
```bash
npm install express mysql2 cors dotenv
npm install -D nodemon
```

### 3. Environment Configuration
Create a `.env` file in the frontend directory:
```bash
# Azure OpenAI Configuration
REACT_APP_AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
REACT_APP_AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
REACT_APP_AZURE_OPENAI_API_VERSION=2024-02-15-preview
REACT_APP_AZURE_OPENAI_KEY=your-api-key

# Backend API Configuration
REACT_APP_API_BASE_URL=http://localhost:3001
```

Create a `.env` file in the root directory for the backend:
```bash
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=bank_agent_db
```

## 🚀 Running the Application

### 1. Start the Backend Server
```bash
node server.js
```
The server will start on http://localhost:3001

### 2. Start the Frontend Development Server
```bash
cd frontend
npm start
```
The React app will start on http://localhost:3000

## 🎯 How to Use

### Data Source Management
1. **View Data Sources**: The main interface shows all available data sources as cards
2. **Toggle Sources**: Click on any data source card to enable/disable it for credit decisions
3. **Visual Feedback**: Enabled sources have green borders and checkmarks
4. **Category Overview**: See counts of enabled/disabled sources by category

### Natural Language Queries
1. **Double-click** any data source card to open the query interface
2. **Enter Query**: Type a natural language query (e.g., "Show me customers with income above $100,000")
3. **Execute**: Click "Execute Query" to convert to SQL and run against the database
4. **View Results**: See the generated SQL and query results

### Data Source Categories
- **👥 Demographics**: Customer basic information
- **🏦 Banking**: Internal banking relationship data
- **📊 Credit Bureau**: External credit information
- **💰 Income**: Income verification and debt ratios
- **🔗 Open Banking**: Transaction and alternative data
- **⚠️ Fraud**: Risk assessment and compliance
- **📈 Economic**: Regional economic indicators

## 🏗️ Architecture

### Frontend Components
- `App.tsx`: Main application component with theme and layout
- `DataLayer.tsx`: Container for all data source management
- `DataSource.tsx`: Individual data source card with interactions
- `api.ts`: Service for Azure OpenAI and database API calls

### Backend API
- `server.js`: Express server with MySQL integration
- Database query execution
- CORS support for frontend communication
- Health check endpoints

### Data Flow
1. User interacts with data source cards
2. Frontend sends natural language queries to Azure OpenAI
3. Azure OpenAI converts queries to SQL
4. Backend executes SQL against MySQL database
5. Results displayed in the UI

## 🔧 Configuration

### Azure OpenAI Setup
1. Create an Azure OpenAI resource
2. Deploy a model (GPT-4 recommended)
3. Get your endpoint, deployment name, and API key
4. Update the `.env` file with your credentials

### Database Connection
Ensure your MySQL database is running and contains the bank agent data:
```bash
# Check database connection
mysql -u root -p bank_agent_db
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:3001/api/health
```

### Sample Query
```bash
curl -X POST http://localhost:3001/api/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT COUNT(*) FROM customer_demographics"}'
```

## 🎨 UI Features

### Interactive Elements
- **Hover Effects**: Cards scale and show tooltips on hover
- **Click Actions**: Toggle data source enablement
- **Double-click**: Open query interface
- **Visual States**: Clear indication of enabled/disabled states

### Responsive Design
- Material-UI components for consistent styling
- Responsive grid layout
- Mobile-friendly interface

### Color Coding
- Each data source category has a unique color
- Enabled/disabled states clearly indicated
- Success/error states for query results

## 🔍 Troubleshooting

### Common Issues

**Frontend won't start**
```bash
# Check Node.js version
node --version

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Backend connection failed**
```bash
# Check MySQL is running
brew services list | grep mysql

# Verify database exists
mysql -u root -e "SHOW DATABASES;"
```

**Azure OpenAI errors**
- Verify your endpoint URL is correct
- Check your API key is valid
- Ensure your deployment name matches exactly
- Verify the API version is supported

**Query execution fails**
- Check the generated SQL syntax
- Verify table and column names exist
- Check database permissions

## 📈 Next Steps

This UI demonstrates the data layer of the NeuroStack architecture. Future enhancements could include:

1. **Processing Layer**: Add drag-and-drop tools for data processing
2. **Decision Engine**: Visual credit decision workflow builder
3. **Real-time Analytics**: Live dashboard with decision metrics
4. **Model Training**: Interface for training and deploying ML models
5. **Audit Trail**: Track all decisions and their reasoning

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details 