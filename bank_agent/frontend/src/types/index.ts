export interface DataSource {
  id: string;
  name: string;
  description: string;
  category: 'demographics' | 'banking' | 'credit_bureau' | 'income' | 'open_banking' | 'fraud' | 'economic';
  isEnabled: boolean;
  tableName: string;
  fields: string[];
  sampleQuery?: string;
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
