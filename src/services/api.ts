import axios from 'axios';
import { QueryResult } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3001';

export class ApiService {
  private static instance: ApiService;
  private azureOpenAIEndpoint: string;
  private azureOpenAIDeploymentName: string;
  private azureOpenAIApiVersion: string;
  private azureOpenAIKey: string;

  constructor() {
    this.azureOpenAIEndpoint = process.env.REACT_APP_AZURE_OPENAI_ENDPOINT || '';
    this.azureOpenAIDeploymentName = process.env.REACT_APP_AZURE_OPENAI_DEPLOYMENT_NAME || '';
    this.azureOpenAIApiVersion = process.env.REACT_APP_AZURE_OPENAI_API_VERSION || '2024-02-15-preview';
    this.azureOpenAIKey = process.env.REACT_APP_AZURE_OPENAI_KEY || '';
  }

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  async convertTextToSQL(naturalLanguageQuery: string, tableName: string, fields: string[]): Promise<QueryResult> {
    try {
      const prompt = this.buildSQLPrompt(naturalLanguageQuery, tableName, fields);
      
      const response = await axios.post(
        `${this.azureOpenAIEndpoint}/openai/deployments/${this.azureOpenAIDeploymentName}/chat/completions?api-version=${this.azureOpenAIApiVersion}`,
        {
          messages: [
            {
              role: "system",
              content: "You are a SQL expert. Convert natural language queries to MySQL SQL statements. Only return the SQL query, no explanations."
            },
            {
              role: "user",
              content: prompt
            }
          ],
          max_tokens: 500,
          temperature: 0.1
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'api-key': this.azureOpenAIKey
          }
        }
      );

      const sqlQuery = response.data.choices[0].message.content.trim();
      
      // Execute the SQL query against the database
      const queryResult = await this.executeSQLQuery(sqlQuery);
      
      return {
        success: true,
        data: queryResult.data,
        sql: sqlQuery,
        executionTime: queryResult.executionTime
      };

    } catch (error) {
      console.error('Error converting text to SQL:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  private buildSQLPrompt(query: string, tableName: string, fields: string[]): string {
    return `
Table: ${tableName}
Available fields: ${fields.join(', ')}

Natural language query: "${query}"

Convert this to a MySQL SELECT statement. Use appropriate WHERE clauses, ORDER BY, and LIMIT as needed.
Only return the SQL query, no explanations or markdown formatting.
    `.trim();
  }

  private async executeSQLQuery(sqlQuery: string): Promise<{ data: any[], executionTime: number }> {
    try {
      const startTime = Date.now();
      
      const response = await axios.post(`${API_BASE_URL}/api/query`, {
        sql: sqlQuery
      });

      const executionTime = Date.now() - startTime;
      
      return {
        data: response.data.results || [],
        executionTime
      };

    } catch (error) {
      console.error('Error executing SQL query:', error);
      throw new Error('Failed to execute SQL query');
    }
  }

  async getDataSources(): Promise<any[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/datasources`);
      return response.data;
    } catch (error) {
      console.error('Error fetching data sources:', error);
      return [];
    }
  }

  async getSampleData(tableName: string, limit: number = 5): Promise<any[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/sample/${tableName}?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching sample data:', error);
      return [];
    }
  }
}

export default ApiService.getInstance();
