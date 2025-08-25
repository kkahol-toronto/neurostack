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
    console.log('🔍 getAuthHeaders: Token from localStorage:', token ? token.substring(0, 50) + '...' : 'No token');
    console.log('🔍 getAuthHeaders: User from localStorage:', localStorage.getItem('user'));
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
      console.log('🔍 API Service: Making request to customer-data endpoint');
      console.log('🔍 API Service: Customer ID:', customerId);
      console.log('🔍 API Service: Include Summary:', includeSummary);
      const authHeaders = this.getAuthHeaders();
      console.log('🔍 API Service: Auth Headers:', authHeaders);
      console.log('🔍 API Service: Token exists:', !!authHeaders.Authorization);
      console.log('🔍 API Service: Token value:', authHeaders.Authorization ? authHeaders.Authorization.substring(0, 50) + '...' : 'No token');
      
      const response = await axios.post(`${API_BASE_URL}/api/customer-data`, {
        customer_id: customerId,
        include_summary: includeSummary
      }, {
        headers: this.getAuthHeaders()
      });
      
      console.log('🔍 API Service: Response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting customer data:', error);
      if (axios.isAxiosError(error)) {
        console.error('❌ API Service: Response status:', error.response?.status);
        console.error('❌ API Service: Response data:', error.response?.data);
      }
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  // Report Management Methods
  async createReport(reportData: any): Promise<any> {
    try {
      console.log('🔍 API Service: Creating report with data:', reportData);
      const response = await axios.post(`${API_BASE_URL}/api/reports`, reportData, {
        headers: this.getAuthHeaders()
      });
      console.log('🔍 API Service: Report creation response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ API Service: Error creating report:', error);
      if (error.response) {
        console.error('❌ API Service: Error response:', error.response.data);
      }
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getReports(customerId?: number, status?: string, limit?: number, offset?: number): Promise<any> {
    try {
      const params = new URLSearchParams();
      if (customerId) params.append('customer_id', customerId.toString());
      if (status) params.append('status', status);
      if (limit) params.append('limit', limit.toString());
      if (offset) params.append('offset', offset.toString());

      const response = await axios.get(`${API_BASE_URL}/api/reports?${params}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting reports:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getReport(reportId: string): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/reports/${reportId}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting report:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async updateReport(reportId: string, updateData: any): Promise<any> {
    try {
      const response = await axios.put(`${API_BASE_URL}/api/reports/${reportId}`, updateData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error updating report:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async deleteReport(reportId: string): Promise<any> {
    try {
      const response = await axios.delete(`${API_BASE_URL}/api/reports/${reportId}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error deleting report:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getReportEnums(): Promise<any> {
    try {
      const [statusResponse, inquiryTypesResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/reports/enums/status`, {
          headers: this.getAuthHeaders()
        }),
        axios.get(`${API_BASE_URL}/api/reports/enums/inquiry-types`, {
          headers: this.getAuthHeaders()
        })
      ]);
      return {
        success: true,
        statuses: statusResponse.data.statuses,
        inquiryTypes: inquiryTypesResponse.data.inquiry_types
      };
    } catch (error) {
      console.error('❌ API Service: Error getting report enums:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async extractCreditLimitInfo(extractionData: {
    inquiryDescription: string;
    currentCreditLimit: number;
  }): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/reports/extract-credit-limit`, extractionData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error extracting credit limit info:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async generateReportRecommendation(reportData: {
    customerId: number;
    customerData: any;
    aiSummary: string;
    inquiryType: string;
    inquiryDescription: string;
    extractedCreditData?: {
      currentCreditLimit: number;
      requestedCreditLimit: number;
      creditLimitIncrease: number;
      extractionMethod: string;
    };
  }): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/reports/generate-recommendation`, reportData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error generating report recommendation:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async generateInvestigationPlan(planData: {
    customerId: number;
    customerName: string;
    customerData: any;
    reportId: string | null;
    currentSteps?: any[];  // New parameter for personalization
  }): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/reports/generate-investigation-plan`, planData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error generating investigation plan:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  // Investigation Execution Methods
  async executeInvestigation(request: {
    customerId: number;
    customerName: string;
    reportId?: string;
    selectedSteps: any[];
    executionMode: 'batch' | 'sequential';
  }): Promise<any> {
    try {
      console.log('🔍 API Service: Sending request to backend:', request);
      const response = await axios.post(`${API_BASE_URL}/api/investigations/execute`, request, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      console.error('❌ API Service: Error executing investigation:', error);
      if (error.response) {
        console.error('❌ Response data:', error.response.data);
        console.error('❌ Response status:', error.response.status);
      }
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }



  async getInvestigationExecution(executionId: string): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/investigations/executions/${executionId}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting investigation execution:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getAllInvestigationExecutions(): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/investigations/executions`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting all investigation executions:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getDataSources(): Promise<any[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/investigations/data-sources`, {
        headers: this.getAuthHeaders()
      });
      
      console.log('🔍 Data sources response:', response.data);
      
      // Handle different response formats
      if (Array.isArray(response.data)) {
        return response.data;
      } else if (response.data && response.data.success && Array.isArray(response.data.data_sources)) {
        return response.data.data_sources;
      } else if (response.data && Array.isArray(response.data.data_sources)) {
        return response.data.data_sources;
      } else if (response.data && Array.isArray(response.data.data)) {
        return response.data.data;
      } else if (response.data && response.data.success && Array.isArray(response.data.data)) {
        return response.data.data;
      } else {
        console.warn('Unexpected data sources response format:', response.data);
        return [];
      }
    } catch (error) {
      console.error('❌ API Service: Error getting data sources:', error);
      return [];
    }
  }

  // Strategy Management Methods
  async createStrategy(strategyData: {
    name: string;
    description?: string;
    strategy_focus: string;
    risk_profile: string;
    steps: any[];
    is_template?: boolean;
    tags?: string[];
  }): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/strategies`, strategyData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error creating strategy:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getStrategies(params?: {
    focus?: string;
    risk_profile?: string;
    search?: string;
    templates_only?: boolean;
  }): Promise<any> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.focus) queryParams.append('focus', params.focus);
      if (params?.risk_profile) queryParams.append('risk_profile', params.risk_profile);
      if (params?.search) queryParams.append('search', params.search);
      if (params?.templates_only) queryParams.append('templates_only', 'true');

      const response = await axios.get(`${API_BASE_URL}/api/strategies?${queryParams}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting strategies:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getStrategy(strategyId: string): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/strategies/${strategyId}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting strategy:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async updateStrategy(strategyId: string, updateData: {
    name?: string;
    description?: string;
    tags?: string[];
    is_template?: boolean;
  }): Promise<any> {
    try {
      const response = await axios.put(`${API_BASE_URL}/api/strategies/${strategyId}`, updateData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error updating strategy:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async deleteStrategy(strategyId: string): Promise<any> {
    try {
      const response = await axios.delete(`${API_BASE_URL}/api/strategies/${strategyId}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error deleting strategy:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  // Chat with Investigations Methods
  async sendChatMessage(request: any): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat/send`, request, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error sending chat message:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  async sendEmail(emailData: any): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/email/send`, emailData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error sending email:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  async generateDecisionDocumentation(docData: any): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/decision-documentation/generate`, docData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error generating decision documentation:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  async getChatHistory(sessionId: string): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/chat/history/${sessionId}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting chat history:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getChatSessions(): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/chat/sessions`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting chat sessions:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async getSessionData(sessionId: string): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/session/${sessionId}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error getting session data:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }

  async saveSessionsToCosmos(): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/investigations/save-to-cosmos`, {}, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('❌ API Service: Error saving sessions to CosmosDB:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
  }
}

export default ApiService.getInstance();
