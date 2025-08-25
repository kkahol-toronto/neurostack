const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Database connection
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'bank_agent_db'
};

let dbConnection;

async function connectDB() {
  try {
    dbConnection = await mysql.createConnection(dbConfig);
    console.log('✅ Connected to MySQL database');
  } catch (error) {
    console.error('❌ Database connection failed:', error);
  }
}

// API Routes
app.get('/api/datasources', async (req, res) => {
  try {
    const [rows] = await dbConnection.execute(`
      SELECT 
        TABLE_NAME as tableName,
        COUNT(*) as fieldCount
      FROM INFORMATION_SCHEMA.COLUMNS 
      WHERE TABLE_SCHEMA = 'bank_agent_db' 
      GROUP BY TABLE_NAME
    `);
    
    res.json(rows);
  } catch (error) {
    console.error('Error fetching data sources:', error);
    res.status(500).json({ error: 'Failed to fetch data sources' });
  }
});

app.post('/api/query', async (req, res) => {
  try {
    const { sql } = req.body;
    
    if (!sql) {
      return res.status(400).json({ error: 'SQL query is required' });
    }

    console.log('Executing SQL:', sql);
    
    const [results] = await dbConnection.execute(sql);
    
    res.json({
      success: true,
      results: results,
      rowCount: results.length
    });
  } catch (error) {
    console.error('Error executing query:', error);
    res.status(500).json({ 
      error: 'Failed to execute query',
      details: error.message 
    });
  }
});

app.get('/api/sample/:tableName', async (req, res) => {
  try {
    const { tableName } = req.params;
    const limit = req.query.limit || 5;
    
    const [results] = await dbConnection.execute(
      `SELECT * FROM ${tableName} LIMIT ?`,
      [parseInt(limit)]
    );
    
    res.json(results);
  } catch (error) {
    console.error('Error fetching sample data:', error);
    res.status(500).json({ error: 'Failed to fetch sample data' });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    timestamp: new Date().toISOString(),
    database: dbConnection ? 'connected' : 'disconnected'
  });
});

// Start server
async function startServer() {
  await connectDB();
  
  app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
  });
}

startServer().catch(console.error);
