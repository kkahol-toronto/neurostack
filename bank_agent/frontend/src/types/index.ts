export interface TableInfo {
  tableName: string;
  fields: string[];
  sampleData?: any[];
}

export interface DataSource {
  id: string;
  name: string;
  description: string;
  category: 'demographics' | 'banking' | 'credit_bureau' | 'income' | 'open_banking' | 'fraud' | 'economic';
  is_enabled: boolean;
  table_name: string;
  fields: string[];
  sample_query?: string;
}

export interface MultiTableQueryRequest {
  naturalLanguageQuery: string;
  tables: TableInfo[];
}

export interface QueryResult {
  success: boolean;
  data?: any[];
  error?: string;
  sql?: string;
  executionTime?: number;
}

export interface NeuroStackLayer {
  id: string;
  name: string;
  description: string;
  components: any[];
  isActive: boolean;
}

export interface CreditDecision {
  customerId: number;
  decision: 'Increase' | 'Decrease' | 'Maintain';
  confidence: number;
  factors: string[];
  riskScore: number;
}

export interface Tool {
  id: string;
  name: string;
  description: string;
  category: 'analysis' | 'prediction' | 'validation' | 'reporting';
  icon: string;
  isDraggable: boolean;
}
