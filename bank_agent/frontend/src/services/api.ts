import axios from 'axios';
import { QueryResult, TableInfo } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

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

  // Helper method to get auth headers
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  async convertTextToSQL(naturalLanguageQuery: string, tableName: string, fields: string[]): Promise<QueryResult> {
    try {
      const startTime = Date.now();
      
      // Call the backend API instead of Azure OpenAI directly
      const response = await axios.post(`${API_BASE_URL}/api/text-to-sql`, {
        natural_language_query: naturalLanguageQuery,
        table_name: tableName,
        fields: fields
      }, {
        headers: this.getAuthHeaders()
      });

      const executionTime = Date.now() - startTime;
      
      if (response.data.success) {
        return {
          success: true,
          data: response.data.data || [],
          sql: response.data.sql,
          executionTime: response.data.execution_time || executionTime
        };
      } else {
        return {
          success: false,
          error: response.data.error || 'Unknown error occurred'
        };
      }

    } catch (error) {
      console.error('Error converting text to SQL:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  async convertTextToSQLMultiTable(naturalLanguageQuery: string, tables: TableInfo[]): Promise<QueryResult> {
    try {
      const startTime = Date.now();
      
      // Call the backend API with multiple tables
      const response = await axios.post(`${API_BASE_URL}/api/text-to-sql`, {
        natural_language_query: naturalLanguageQuery,
        tables: tables.map(table => ({
          table_name: table.tableName,
          fields: table.fields,
          sample_data: table.sampleData
        }))
      }, {
        headers: this.getAuthHeaders()
      });

      const executionTime = Date.now() - startTime;
      
      if (response.data.success) {
        return {
          success: true,
          data: response.data.data || [],
          sql: response.data.sql,
          executionTime: response.data.execution_time || executionTime
        };
      } else {
        return {
          success: false,
          error: response.data.error || 'Unknown error occurred'
        };
      }

    } catch (error) {
      console.error('Error converting text to SQL with multiple tables:', error);
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

  async executeSQL(sqlQuery: string, tableName?: string): Promise<QueryResult> {
    try {
      const startTime = Date.now();
      
      const response = await axios.post(`${API_BASE_URL}/api/query`, {
        sql: sqlQuery,
        table_name: tableName
      });

      const executionTime = Date.now() - startTime;
      
      if (response.data.success) {
        return {
          success: true,
          data: response.data.data || [],
          sql: sqlQuery,
          executionTime: response.data.execution_time || executionTime
        };
      } else {
        return {
          success: false,
          error: response.data.error || 'Unknown error occurred'
        };
      }

    } catch (error) {
      console.error('Error executing SQL query:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
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

  async searchCustomers(query: string): Promise<{ success: boolean; customers: any[]; total_count: number; error?: string }> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/search-customers`, {
        query: query
      }, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error searching customers:', error);
      return {
        success: false,
        customers: [],
        total_count: 0,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Authentication methods
  async login(username: string, password: string): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        username,
        password
      });
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async register(userData: any): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, userData);
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async getProfile(): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/profile`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Get profile error:', error);
      throw error;
    }
  }

  async getUserBehavior(userId: string): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/users/${userId}/behavior`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Get user behavior error:', error);
      throw error;
    }
  }

  // NeuroStack enhanced features
  async getQueryAnalytics(hours: number = 24): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/neurostack/recent-activity?hours=${hours}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error getting query analytics:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getOptimizationSuggestions(query: string, userId?: string): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/neurostack/optimization-suggestions`, {
        query,
        user_id: userId
      }, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error getting optimization suggestions:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getSimilarQueries(query: string, limit: number = 5): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/neurostack/similar-queries`, {
        query,
        limit
      }, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error getting similar queries:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  // Customer data methods
  async getCustomerData(customerId: number, includeSummary: boolean = true): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/customer-data`, {
        customer_id: customerId,
        include_summary: includeSummary
      }, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error getting customer data:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }
}

export default ApiService.getInstance();
