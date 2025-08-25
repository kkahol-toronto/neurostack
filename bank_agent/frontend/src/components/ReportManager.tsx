import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Card,
  CardContent,
  IconButton,
  Alert,
  CircularProgress,
  Divider,
  List
} from '@mui/material';
import {
  Save as SaveIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  Description as ReportIcon,
  Assessment as AssessmentIcon,
  CreditCard as CreditCardIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import apiService from '../services/api';
import ReactMarkdown from 'react-markdown';
import DataProcessingStage from './DataProcessingStage';

interface ReportManagerProps {
  customerId: number;
  customerName: string;
  customerData: any;
  aiSummary: string;
  onReportSaved?: (reportId: string) => void;
}

interface Report {
  report_id: string;
  customer_id: number;
  customer_name: string;
  report_date: string;
  inquiry_type: string;
  inquiry_description: string;
  ai_summary: string;
  ai_recommendation: string;
  suggested_decision: string;
  current_credit_limit?: number;
  requested_credit_limit?: number;
  credit_limit_increase?: number;
  agent_notes?: string;
  status: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
  customer_data: any;
  credit_recommendation?: string;
  final_decision?: string;
  decision_date?: string;
  decision_by?: string;
}

const ReportManager: React.FC<ReportManagerProps> = ({
  customerId,
  customerName,
  customerData,
  aiSummary,
  onReportSaved
}) => {
  const { theme } = useTheme();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  
  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [amountDialogOpen, setAmountDialogOpen] = useState(false);
  const [extractedAmount, setExtractedAmount] = useState<number | null>(null);
  
  // Form states
  const [inquiryType, setInquiryType] = useState('');
  const [inquiryDescription, setInquiryDescription] = useState('');
  const [aiRecommendation, setAiRecommendation] = useState('');
  const [suggestedDecision, setSuggestedDecision] = useState('');
  const [currentCreditLimit, setCurrentCreditLimit] = useState<number | null>(null);
  const [requestedCreditLimit, setRequestedCreditLimit] = useState<number | null>(null);
  const [creditLimitIncrease, setCreditLimitIncrease] = useState<number | null>(null);
  const [agentNotes, setAgentNotes] = useState('');
  const [status, setStatus] = useState('');
  const [creditRecommendation, setCreditRecommendation] = useState('');
  const [finalDecision, setFinalDecision] = useState('');
  
  // Enums
  const [inquiryTypes, setInquiryTypes] = useState<string[]>([]);
  const [statuses, setStatuses] = useState<string[]>([]);
  
  // Plan for Investigation Stage
  const [dataProcessingOpen, setDataProcessingOpen] = useState(false);
  const [lastCreatedReportId, setLastCreatedReportId] = useState<string | null>(null);
  const [selectedReportForDataProcessing, setSelectedReportForDataProcessing] = useState<Report | null>(null);

  const loadReports = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiService.getReports(customerId);
      if (response.success) {
        const reports = response.reports || response.data || [];
        // Sort reports by creation date (newest first)
        const sortedReports = reports.sort((a: any, b: any) => {
          const dateA = new Date(a.created_at || a.report_date || 0);
          const dateB = new Date(b.created_at || b.report_date || 0);
          return dateB.getTime() - dateA.getTime();
        });
        setReports(sortedReports);
      } else {
        setError(response.error || 'Failed to load reports');
      }
    } catch (err) {
      setError('Failed to load reports');
      console.error('Error loading reports:', err);
    } finally {
      setLoading(false);
    }
  }, [customerId]);

  useEffect(() => {
    loadReports();
    loadEnums();
  }, [loadReports]);

  // Auto-populate current credit limit from customer data when component loads
  useEffect(() => {
    console.log('🔍 ReportManager component loaded');
    console.log('🔍 Customer ID:', customerId);
    console.log('🔍 Customer Name:', customerName);
    console.log('🔍 Customer Data:', customerData);
    console.log('🔍 Customer Data Type:', typeof customerData);
    console.log('🔍 Customer Data Keys:', customerData ? Object.keys(customerData) : 'No data');
    
    if (customerData) {
      console.log('🔍 Customer data available, attempting to populate current credit limit...');
      console.log('🔍 Customer data structure:', JSON.stringify(customerData, null, 2));
      populateCurrentCreditLimitFromData();
    } else {
      console.log('❌ No customer data provided to ReportManager');
    }
  }, [customerData, customerId, customerName]);

  // Also populate when create dialog opens
  useEffect(() => {
    if (createDialogOpen && customerData) {
      console.log('🔍 Create dialog opened, re-populating credit limit...');
      populateCurrentCreditLimitFromData();
    }
  }, [createDialogOpen, customerData]);

  // Auto-populate current credit limit from customer data
  const populateCurrentCreditLimitFromData = () => {
    if (!customerData) {
      console.log('❌ No customer data available');
      return;
    }
    
    console.log('🔍 Searching for credit limit in customer data...');
    console.log('🔍 Customer data keys:', Object.keys(customerData));
    console.log('🔍 Full customer data structure:', JSON.stringify(customerData, null, 2));
    
    // Look for current credit limit in customer data
    const creditLimitKeys = ['current_credit_limit', 'credit_limit', 'current_credit', 'credit_limit_current'];
    for (const key of creditLimitKeys) {
      if (customerData[key]) {
        const currentLimit = parseFloat(customerData[key]);
        setCurrentCreditLimit(currentLimit);
        console.log(`✅ Auto-populated current credit limit from customer data (${key}):`, currentLimit);
        return;
      }
    }
    
    // Check for credit limit in internal_banking_data structure
    if (customerData.internal_banking_data && customerData.internal_banking_data.data) {
      const bankingData = customerData.internal_banking_data.data;
      console.log('🔍 Found internal_banking_data:', bankingData);
      console.log('🔍 internal_banking_data keys:', Object.keys(bankingData));
      
      if (bankingData.current_credit_limit) {
        const currentLimit = parseFloat(bankingData.current_credit_limit);
        setCurrentCreditLimit(currentLimit);
        console.log(`✅ Auto-populated current credit limit from internal_banking_data:`, currentLimit);
        return;
      }
    }
    
    // Check if customerData is an array and look in each item
    if (Array.isArray(customerData)) {
      console.log('🔍 Customer data is an array, searching through items...');
      customerData.forEach((item, index) => {
        console.log(`🔍 Checking item ${index}:`, item);
        if (item && typeof item === 'object') {
          // Check direct properties
          const creditLimitKeys = ['current_credit_limit', 'credit_limit', 'current_credit', 'credit_limit_current'];
          for (const key of creditLimitKeys) {
            if (item[key]) {
              const currentLimit = parseFloat(item[key]);
              setCurrentCreditLimit(currentLimit);
              console.log(`✅ Auto-populated current credit limit from array item ${index} (${key}):`, currentLimit);
              return;
            }
          }
          
          // Check nested data structures
          if (item.data) {
            console.log(`🔍 Checking nested data in item ${index}:`, item.data);
            Object.values(item.data).forEach((field: any) => {
              if (field && typeof field === 'object' && field.field_name && 
                  field.field_name.toLowerCase().includes('credit') && 
                  field.field_name.toLowerCase().includes('limit') &&
                  field.field_value) {
                const currentLimit = parseFloat(field.field_value);
                setCurrentCreditLimit(currentLimit);
                console.log(`✅ Auto-populated current credit limit from nested data in item ${index}:`, currentLimit);
              }
            });
          }
        }
      });
    } else {
      // Also check nested data structures for non-array data
      console.log('🔍 Checking nested data structures...');
      Object.values(customerData).forEach((sourceData: any) => {
        if (sourceData && typeof sourceData === 'object' && sourceData.data) {
          console.log('🔍 Found nested data:', sourceData.data);
          console.log('🔍 Nested data keys:', Object.keys(sourceData.data));
          
          Object.values(sourceData.data).forEach((field: any) => {
            console.log('🔍 Checking field:', field);
            if (field && typeof field === 'object' && field.field_name) {
              console.log(`🔍 Field name: "${field.field_name}", Field value: "${field.field_value}"`);
              
              // Check for credit limit in field name
              if (field.field_name.toLowerCase().includes('credit') && 
                  field.field_name.toLowerCase().includes('limit') &&
                  field.field_value) {
                const currentLimit = parseFloat(field.field_value);
                setCurrentCreditLimit(currentLimit);
                console.log(`✅ Auto-populated current credit limit from nested data:`, currentLimit);
              }
              
              // Also check for any numeric field that might be credit limit
              if (field.field_value && !isNaN(parseFloat(field.field_value))) {
                const numericValue = parseFloat(field.field_value);
                console.log(`🔍 Found numeric field: "${field.field_name}" = ${numericValue}`);
              }
            }
          });
        }
      });
    }
    
    console.log('❌ No credit limit found in customer data');
    
    // Last resort: search for any field containing 32000 or similar values
    console.log('🔍 Performing deep search for credit limit values...');
    const deepSearch = (obj: any, path: string = '') => {
      if (obj && typeof obj === 'object') {
        Object.entries(obj).forEach(([key, value]) => {
          const currentPath = path ? `${path}.${key}` : key;
          
          if (typeof value === 'string' && value.includes('32000')) {
            console.log(`🔍 Found 32000 in: ${currentPath} = "${value}"`);
          }
          
          if (typeof value === 'number' && value >= 30000 && value <= 35000) {
            console.log(`🔍 Found potential credit limit: ${currentPath} = ${value}`);
          }
          
          if (typeof value === 'object' && value !== null) {
            deepSearch(value, currentPath);
          }
        });
      }
    };
    
    deepSearch(customerData);
  };

  const loadEnums = async () => {
    try {
      console.log('🔍 Loading enums...');
      const response = await apiService.getReportEnums();
      console.log('🔍 Enums response:', response);
      if (response.success) {
        console.log('🔍 Setting inquiry types:', response.inquiryTypes);
        console.log('🔍 Setting statuses:', response.statuses);
        setInquiryTypes(response.inquiryTypes || []);
        setStatuses(response.statuses || []);
      } else {
        console.error('❌ Failed to load enums:', response.error);
        // Set default values if API fails
        setInquiryTypes(['credit_limit_increase', 'new_credit_product', 'loan_application', 'refinancing', 'general_inquiry']);
        setStatuses(['pending', 'approved', 'rejected', 'under_review']);
      }
    } catch (err) {
      console.error('❌ Error loading enums:', err);
      // Set default values if API fails
      setInquiryTypes(['credit_limit_increase', 'new_credit_product', 'loan_application', 'refinancing', 'general_inquiry']);
      setStatuses(['pending', 'approved', 'rejected', 'under_review']);
    }
  };

  // Function to extract amount from inquiry description
  const extractAmountFromDescription = (description: string): number | null => {
    const text = description.toLowerCase();
    console.log('🔍 Extracting amount from:', text);
    
    // Pattern for "increase by X" format (single number)
    const increaseByPattern = /increase\s+by\s+(\d{1,3}(?:,\d{3})*)/;
    const increaseByMatch = text.match(increaseByPattern);
    
    if (increaseByMatch) {
      const amount = parseFloat(increaseByMatch[1].replace(/[$,]/g, ''));
      console.log('✅ Extracted amount (increase by):', amount);
      return amount;
    }
    
    // Pattern for "increase of X" format
    const increaseOfPattern = /increase\s+of\s+\$?\s*(\d{1,3}(?:,\d{3})*)/;
    const increaseOfMatch = text.match(increaseOfPattern);
    
    if (increaseOfMatch) {
      const amount = parseFloat(increaseOfMatch[1].replace(/[$,]/g, ''));
      console.log('✅ Extracted amount (increase of):', amount);
      return amount;
    }
    
    // Pattern for just numbers (take the first one)
    const numberPattern = /\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)/g;
    const matches = text.match(numberPattern);
    if (matches && matches.length >= 1) {
      const amount = parseFloat(matches[0].replace(/[$,]/g, ''));
      console.log('✅ Extracted amount (single number):', amount);
      return amount;
    }
    
    console.log('❌ No amount found in description');
    return null;
  };

  const generateAiRecommendation = async () => {
    try {
      console.log('🔍 Starting AI recommendation generation...');
      console.log('🔍 Customer ID:', customerId);
      console.log('🔍 Inquiry Type:', inquiryType);
      console.log('🔍 Inquiry Description:', inquiryDescription);
      
      setLoading(true);
      setError('');
      
      // Step 1: Use LLM to extract credit limit information from description
      console.log('🔍 Step 1: Extracting credit limit information using LLM...');
      const extractionResponse = await apiService.extractCreditLimitInfo({
        inquiryDescription,
        currentCreditLimit: currentCreditLimit || 0
      });
      
      console.log('🔍 Extraction Response:', extractionResponse);
      
      if (!extractionResponse.success) {
        setError('Failed to extract credit limit information');
        setLoading(false);
        return;
      }
      
      const extractedData = extractionResponse.data;
      let creditLimitIncrease = 0;
      let requestedCreditLimit = 0;
      
      // Handle different extraction scenarios
      if (extractedData.increase_amount) {
        // Scenario 1: "increase by X"
        creditLimitIncrease = extractedData.increase_amount;
        requestedCreditLimit = (currentCreditLimit || 0) + creditLimitIncrease;
        console.log('✅ Scenario 1: Increase by amount:', {
          current: currentCreditLimit,
          increase: creditLimitIncrease,
          requested: requestedCreditLimit
        });
      } else if (extractedData.requested_total_limit) {
        // Scenario 2: "total credit limit to be X"
        requestedCreditLimit = extractedData.requested_total_limit;
        creditLimitIncrease = requestedCreditLimit - (currentCreditLimit || 0);
        console.log('✅ Scenario 2: Total limit requested:', {
          current: currentCreditLimit,
          requested: requestedCreditLimit,
          increase: creditLimitIncrease
        });
      } else {
        // No clear extraction, show dialog
        setExtractedAmount(null);
        setAmountDialogOpen(true);
        setLoading(false);
        return;
      }
      
      // Update UI with extracted values
      setRequestedCreditLimit(requestedCreditLimit);
      setCreditLimitIncrease(creditLimitIncrease);
      
      // Step 2: Generate AI recommendation with customer profile + extracted data
      console.log('🔍 Step 2: Generating AI recommendation with enhanced data...');
      const recommendationResponse = await apiService.generateReportRecommendation({
        customerId,
        customerData,
        aiSummary,
        inquiryType,
        inquiryDescription,
        extractedCreditData: {
          currentCreditLimit: currentCreditLimit || 0,
          requestedCreditLimit,
          creditLimitIncrease,
          extractionMethod: extractedData.increase_amount ? 'increase_by' : 'total_limit'
        }
      });
      
      console.log('🔍 Recommendation Response:', recommendationResponse);
      
      if (recommendationResponse.success) {
        setAiRecommendation(recommendationResponse.data.recommendation || '');
        setSuggestedDecision(recommendationResponse.data.suggested_decision || '');
      } else {
        setError(recommendationResponse.error || 'Failed to generate AI recommendation');
      }
    } catch (err) {
      setError('Failed to generate AI recommendation');
      console.error('Error generating AI recommendation:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReport = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess(''); // Clear any previous success messages
      
      console.log('🔍 Creating report with data:', {
        customer_id: customerId,
        customer_name: customerName,
        inquiry_type: inquiryType,
        inquiry_description: inquiryDescription,
        ai_summary: aiSummary,
        ai_recommendation: aiRecommendation,
        suggested_decision: suggestedDecision,
        current_credit_limit: currentCreditLimit || null,
        requested_credit_limit: requestedCreditLimit || null,
        credit_limit_increase: creditLimitIncrease || null,
        agent_notes: agentNotes,
        status: status || 'pending',
        customer_data: customerData
      });

      const reportData = {
        customer_id: customerId,
        customer_name: customerName,
        inquiry_type: inquiryType,
        inquiry_description: inquiryDescription,
        ai_summary: aiSummary,
        ai_recommendation: aiRecommendation,
        suggested_decision: suggestedDecision,
        current_credit_limit: currentCreditLimit || null,
        requested_credit_limit: requestedCreditLimit || null,
        credit_limit_increase: creditLimitIncrease || null,
        agent_notes: agentNotes,
        status: status || 'pending',
        customer_data: customerData
      };

      const response = await apiService.createReport(reportData);
      console.log('🔍 Report creation response:', response);
      
      if (response.success) {
        setSuccess('Report created successfully');
        setError(''); // Clear any previous errors
        setCreateDialogOpen(false);
        
        // Handle different response structures
        const reportId = response.report?.report_id || response.data?.report_id;
        if (reportId) {
          setLastCreatedReportId(reportId);
          if (onReportSaved) {
            onReportSaved(reportId);
          }
        }
        
        resetForm();
        loadReports();
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000);
        // Clear the last created report ID after 10 minutes
        setTimeout(() => clearLastCreatedReport(), 600000);
      } else {
        setError(response.error || 'Failed to create report');
        setSuccess(''); // Clear any previous success messages
      }
    } catch (err) {
      setError('Failed to create report');
      setSuccess(''); // Clear any previous success messages
      console.error('Error creating report:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateReport = async () => {
    if (!selectedReport) return;
    
    try {
      setSaving(true);
      setError('');
      setSuccess(''); // Clear any previous success messages
      
      const updateData = {
        status,
        agent_notes: agentNotes,
        credit_recommendation: creditRecommendation,
        final_decision: finalDecision,
        current_credit_limit: currentCreditLimit || null,
        requested_credit_limit: requestedCreditLimit || null,
        credit_limit_increase: creditLimitIncrease || null
      };

      const response = await apiService.updateReport(selectedReport.report_id, updateData);
      if (response.success) {
        setSuccess('Report updated successfully');
        setError(''); // Clear any previous errors
        setEditDialogOpen(false);
        loadReports();
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(response.error || 'Failed to update report');
        setSuccess(''); // Clear any previous success messages
      }
    } catch (err) {
      setError('Failed to update report');
      setSuccess(''); // Clear any previous success messages
      console.error('Error updating report:', err);
    } finally {
      setSaving(false);
    }
  };

  const openEditDialog = (report: Report) => {
    setSelectedReport(report);
    setStatus(report.status);
    setAgentNotes(report.agent_notes || '');
    setCreditRecommendation(report.credit_recommendation || '');
    setFinalDecision(report.final_decision || '');
    setCurrentCreditLimit(report.current_credit_limit || null);
    setRequestedCreditLimit(report.requested_credit_limit || null);
    setCreditLimitIncrease(report.credit_limit_increase || null);
    setEditDialogOpen(true);
  };

  const openViewDialog = (report: Report) => {
    setSelectedReport(report);
    setViewDialogOpen(true);
  };

  const openDataProcessing = (report: Report) => {
    setSelectedReportForDataProcessing(report);
    setDataProcessingOpen(true);
  };

  const resetForm = () => {
    setInquiryType('');
    setInquiryDescription('');
    setAiRecommendation('');
    setSuggestedDecision('');
    setCurrentCreditLimit(null);
    setRequestedCreditLimit(null);
    setCreditLimitIncrease(null);
    setAgentNotes('');
    setStatus('');
    setCreditRecommendation('');
    setFinalDecision('');
  };

  const clearLastCreatedReport = () => {
    setLastCreatedReportId(null);
  };

  const handleAmountDialogConfirm = async (amount: number) => {
    setAmountDialogOpen(false);
    
    // Calculate requested credit limit
    const currentLimit = currentCreditLimit || 0;
    const requestedLimit = currentLimit + amount;
    setRequestedCreditLimit(requestedLimit);
    setCreditLimitIncrease(amount);
    
    console.log('✅ User provided amount, calculated credit limits:', {
      current: currentLimit,
      requested: requestedLimit,
      increase: amount
    });
    
    // Continue with AI recommendation generation
    try {
      setLoading(true);
      console.log('🔍 Calling API service...');
      const response = await apiService.generateReportRecommendation({
        customerId,
        customerData,
        aiSummary,
        inquiryType,
        inquiryDescription
      });
      
      console.log('🔍 API Response:', response);
      
      if (response.success) {
        setAiRecommendation(response.data.recommendation || '');
        setSuggestedDecision(response.data.suggested_decision || '');
      } else {
        setError(response.error || 'Failed to generate AI recommendation');
      }
    } catch (err) {
      setError('Failed to generate AI recommendation');
      console.error('Error generating AI recommendation:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      case 'under_review': return 'info';
      default: return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 3 
      }}>
        <Typography variant="h5" sx={{ color: theme.colors.text }}>
          <ReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Customer Reports
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          sx={{ backgroundColor: theme.colors.primary }}
        >
          Create Report
        </Button>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
          {success}
        </Alert>
      )}
      
      {lastCreatedReportId && (
        <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant="contained"
            onClick={() => setDataProcessingOpen(true)}
            startIcon={<AssessmentIcon />}
            sx={{ 
              backgroundColor: theme.colors.primary,
              '&:hover': { backgroundColor: theme.colors.primaryDark }
            }}
                      >
              Go to Plan for Investigation
            </Button>
          <Button
            variant="outlined"
            size="small"
            onClick={clearLastCreatedReport}
            sx={{ color: theme.colors.textSecondary }}
          >
            Dismiss
          </Button>
        </Box>
      )}

      {/* Reports List */}
      {reports.length === 0 ? (
        <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <ReportIcon sx={{ fontSize: 48, color: theme.colors.textSecondary, mb: 2 }} />
            <Typography variant="h6" sx={{ color: theme.colors.textSecondary, mb: 1 }}>
              No Reports Yet
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
              Create your first report to get started
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <List>
          {reports.map((report) => (
            <Card key={report.report_id} sx={{ 
              mb: 2, 
              backgroundColor: 'rgba(255, 255, 255, 0.05)', 
              border: '1px solid rgba(255, 255, 255, 0.1)' 
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
                      {report.inquiry_type.replace(/_/g, ' ').toUpperCase()}
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 1 }}>
                      {report.inquiry_description}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                      <Chip
                        label={report.status.replace(/_/g, ' ').toUpperCase()}
                        color={getStatusColor(report.status) as any}
                        size="small"
                      />
                      <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                        {formatDate(report.created_at)}
                      </Typography>
                      {report.ai_recommendation && (
                        <Chip
                          label="AI Ready"
                          color="success"
                          size="small"
                          variant="outlined"
                          icon={<AssessmentIcon />}
                        />
                      )}
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => openDataProcessing(report)}
                      startIcon={<AssessmentIcon />}
                      sx={{ 
                        color: theme.colors.primary,
                        borderColor: theme.colors.primary,
                        '&:hover': { 
                          borderColor: theme.colors.primaryDark,
                          backgroundColor: 'rgba(255, 255, 255, 0.05)'
                        }
                      }}
                                          >
                        Plan for Investigation
                      </Button>
                    <IconButton
                      size="small"
                      onClick={() => openViewDialog(report)}
                      sx={{ color: theme.colors.primary }}
                    >
                      <ViewIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => openEditDialog(report)}
                      sx={{ color: theme.colors.primary }}
                    >
                      <EditIcon />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ))}
        </List>
      )}

      {/* Create Report Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle sx={{ color: theme.colors.text }}>
          Create New Report - {customerName}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2, mt: 1 }}>
            <Box>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Inquiry Type</InputLabel>
                <Select
                  value={inquiryType}
                  onChange={(e) => setInquiryType(e.target.value)}
                  label="Inquiry Type"
                >
                  {inquiryTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type.replace(/_/g, ' ').toUpperCase()}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <TextField
                fullWidth
                label="Inquiry Description"
                value={inquiryDescription}
                onChange={(e) => setInquiryDescription(e.target.value)}
                multiline
                rows={3}
                placeholder="Describe the customer inquiry..."
                sx={{ mb: 2 }}
              />

              <Button
                variant="outlined"
                onClick={generateAiRecommendation}
                disabled={!inquiryType || !inquiryDescription || loading}
                startIcon={loading ? <CircularProgress size={20} /> : <AssessmentIcon />}
                sx={{ mb: 2 }}
              >
                {loading ? 'Generating...' : 'Generate AI Recommendation'}
              </Button>
            </Box>

            <Box>
              <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                AI Recommendation
              </Typography>
              <TextField
                fullWidth
                label="Neurostack Agent Recommendation"
                value={aiRecommendation}
                onChange={(e) => setAiRecommendation(e.target.value)}
                multiline
                rows={8}
                placeholder="AI recommendation will be generated..."
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="Suggested Decision"
                value={suggestedDecision}
                onChange={(e) => setSuggestedDecision(e.target.value)}
                multiline
                rows={2}
                placeholder="Suggested decision based on AI analysis..."
                sx={{ mb: 2 }}
              />
            </Box>
          </Box>

          {/* Credit Limit Information */}
          <Divider sx={{ my: 3 }} />
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text }}>
              <CreditCardIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Credit Limit Information
            </Typography>
            <Button
              size="small"
              variant="outlined"
              onClick={() => {
                console.log('🔍 Manual credit limit population triggered');
                setCurrentCreditLimit(32000);
                console.log('✅ Manually set current credit limit to 32000');
              }}
              sx={{ fontSize: '0.75rem', mr: 1 }}
            >
              Set 32,000 (Debug)
            </Button>
            <Button
              size="small"
              variant="outlined"
              onClick={() => {
                console.log('🔄 Refreshing credit limit from customer data...');
                populateCurrentCreditLimitFromData();
              }}
              sx={{ fontSize: '0.75rem' }}
            >
              Refresh from Data
            </Button>
          </Box>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
            <TextField
              fullWidth
              label="Current Credit Limit"
              type="number"
              value={currentCreditLimit || ''}
              onChange={(e) => setCurrentCreditLimit(e.target.value ? Number(e.target.value) : null)}
              placeholder="Current credit limit amount"
              InputProps={{
                startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>
              }}
            />
            <TextField
              fullWidth
              label="Requested Credit Limit"
              type="number"
              value={requestedCreditLimit || ''}
              onChange={(e) => setRequestedCreditLimit(e.target.value ? Number(e.target.value) : null)}
              placeholder="Requested credit limit amount"
              InputProps={{
                startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>
              }}
            />
            <TextField
              fullWidth
              label="Credit Limit Increase"
              type="number"
              value={creditLimitIncrease || ''}
              onChange={(e) => setCreditLimitIncrease(e.target.value ? Number(e.target.value) : null)}
              placeholder="Increase amount"
              InputProps={{
                startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>
              }}
            />
          </Box>

          <TextField
            fullWidth
            label="Agent Notes"
            value={agentNotes}
            onChange={(e) => setAgentNotes(e.target.value)}
            multiline
            rows={3}
            placeholder="Add your notes, observations, or recommendations..."
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateReport}
            disabled={saving || !inquiryType || !inquiryDescription}
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            variant="contained"
          >
            {saving ? 'Creating...' : 'Create Report'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Report Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle sx={{ color: theme.colors.text }}>
          View Report - {selectedReport?.customer_name}
        </DialogTitle>
        <DialogContent>
          {selectedReport && (
            <Box sx={{ mt: 1 }}>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 3 }}>
                <Box>
                  <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                    Report Details
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                      <strong>Inquiry Type:</strong> {selectedReport.inquiry_type.replace(/_/g, ' ').toUpperCase()}
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                      <strong>Status:</strong> 
                      <Chip
                        label={selectedReport.status.replace(/_/g, ' ').toUpperCase()}
                        color={getStatusColor(selectedReport.status) as any}
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                      <strong>Created:</strong> {formatDate(selectedReport.created_at)}
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                      <strong>By:</strong> {selectedReport.created_by}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body1" sx={{ color: theme.colors.text, mb: 1 }}>
                    <strong>Inquiry Description:</strong>
                  </Typography>
                  <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 2 }}>
                    {selectedReport.inquiry_description}
                  </Typography>

                  {/* Credit Limit Information */}
                  {(selectedReport.current_credit_limit || selectedReport.requested_credit_limit) && (
                    <>
                      <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                        <CreditCardIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Credit Limit Information
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        {selectedReport.current_credit_limit && (
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                            <strong>Current Credit Limit:</strong> ${selectedReport.current_credit_limit.toLocaleString()}
                          </Typography>
                        )}
                        {selectedReport.requested_credit_limit && (
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                            <strong>Requested Credit Limit:</strong> ${selectedReport.requested_credit_limit.toLocaleString()}
                          </Typography>
                        )}
                        {selectedReport.credit_limit_increase && (
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                            <strong>Credit Limit Increase:</strong> ${selectedReport.credit_limit_increase.toLocaleString()}
                          </Typography>
                        )}
                      </Box>
                    </>
                  )}

                  {selectedReport.agent_notes && (
                    <>
                      <Typography variant="body1" sx={{ color: theme.colors.text, mb: 1 }}>
                        <strong>Agent Notes:</strong>
                      </Typography>
                      <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 2 }}>
                        {selectedReport.agent_notes}
                      </Typography>
                    </>
                  )}

                  {selectedReport.credit_recommendation && (
                    <>
                      <Typography variant="body1" sx={{ color: theme.colors.text, mb: 1 }}>
                        <strong>Credit Recommendation:</strong>
                      </Typography>
                      <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 2 }}>
                        {selectedReport.credit_recommendation}
                      </Typography>
                    </>
                  )}

                  {selectedReport.final_decision && (
                    <>
                      <Typography variant="body1" sx={{ color: theme.colors.text, mb: 1 }}>
                        <strong>Final Decision:</strong>
                      </Typography>
                      <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 2 }}>
                        {selectedReport.final_decision}
                      </Typography>
                    </>
                  )}
                </Box>
                
                <Box>
                  <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                    AI Analysis
                  </Typography>
                  
                  {selectedReport.ai_recommendation && (
                    <>
                      <Typography variant="body1" sx={{ color: theme.colors.text, mb: 1 }}>
                        <strong>Neurostack Agent Recommendation:</strong>
                      </Typography>
                      <Box sx={{ 
                        p: 2, 
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: 1,
                        mb: 2
                      }}>
                        <ReactMarkdown>{selectedReport.ai_recommendation}</ReactMarkdown>
                      </Box>
                    </>
                  )}

                  {selectedReport.suggested_decision && (
                    <>
                      <Typography variant="body1" sx={{ color: theme.colors.text, mb: 1 }}>
                        <strong>Suggested Decision:</strong>
                      </Typography>
                      <Box sx={{ 
                        p: 2, 
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: 1,
                        mb: 2
                      }}>
                        <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                          {selectedReport.suggested_decision}
                        </Typography>
                      </Box>
                    </>
                  )}

                  <Typography variant="body1" sx={{ color: theme.colors.text, mb: 1 }}>
                    <strong>AI Summary:</strong>
                  </Typography>
                  <Box sx={{ 
                    p: 2, 
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: 1,
                    maxHeight: 300,
                    overflow: 'auto'
                  }}>
                    <ReactMarkdown>{selectedReport.ai_summary}</ReactMarkdown>
                  </Box>
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
          {selectedReport && (
            <Button
              onClick={() => {
                setViewDialogOpen(false);
                openEditDialog(selectedReport);
              }}
              startIcon={<EditIcon />}
              variant="contained"
            >
              Edit Report
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Edit Report Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ color: theme.colors.text }}>
          Edit Report - {selectedReport?.customer_name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                label="Status"
              >
                {statuses.map((s) => (
                  <MenuItem key={s} value={s}>
                    {s.replace(/_/g, ' ').toUpperCase()}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Box sx={{ gridColumn: '1 / -1' }}>
              <TextField
                fullWidth
                label="Agent Notes"
                value={agentNotes}
                onChange={(e) => setAgentNotes(e.target.value)}
                multiline
                rows={4}
                placeholder="Add your notes, observations, or recommendations..."
              />
            </Box>
            
            <Box sx={{ gridColumn: '1 / -1' }}>
              <TextField
                fullWidth
                label="Credit Recommendation"
                value={creditRecommendation}
                onChange={(e) => setCreditRecommendation(e.target.value)}
                multiline
                rows={3}
                placeholder="Provide credit recommendation based on analysis..."
              />
            </Box>
            
            <Box sx={{ gridColumn: '1 / -1' }}>
              <TextField
                fullWidth
                label="Final Decision"
                value={finalDecision}
                onChange={(e) => setFinalDecision(e.target.value)}
                multiline
                rows={2}
                placeholder="Final decision on the customer's request..."
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleUpdateReport}
            disabled={saving}
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            variant="contained"
          >
            {saving ? 'Saving...' : 'Update Report'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Amount Dialog */}
      <Dialog
        open={amountDialogOpen}
        onClose={() => setAmountDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ color: theme.colors.text }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarningIcon sx={{ color: 'warning.main' }} />
            Amount Not Found
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>
            We couldn't automatically extract the credit limit increase amount from your description. 
            Please specify the amount the customer is requesting:
          </Typography>
          <TextField
            fullWidth
            label="Credit Limit Increase Amount"
            type="number"
            placeholder="Enter amount (e.g., 8000)"
            InputProps={{
              startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>
            }}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                const amount = parseFloat((e.target as HTMLInputElement).value);
                if (amount && amount > 0) {
                  handleAmountDialogConfirm(amount);
                }
              }
            }}
            autoFocus
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAmountDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={() => {
              const input = document.querySelector('input[type="number"]') as HTMLInputElement;
              const amount = parseFloat(input?.value || '0');
              if (amount && amount > 0) {
                handleAmountDialogConfirm(amount);
              }
            }}
            variant="contained"
          >
            Confirm & Generate AI Recommendation
          </Button>
        </DialogActions>
      </Dialog>

      {/* Plan for Investigation Dialog */}
      <Dialog
        open={dataProcessingOpen}
        onClose={() => setDataProcessingOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle sx={{ color: theme.colors.text }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AssessmentIcon />
            Plan for Investigation - Analysis Strategy
          </Box>
        </DialogTitle>
        <DialogContent>
          <DataProcessingStage 
            customerId={customerId}
            customerName={customerName}
            customerData={customerData}
            reportId={selectedReportForDataProcessing?.report_id || lastCreatedReportId}
            reportData={selectedReportForDataProcessing}
            onClose={() => {
              setDataProcessingOpen(false);
              setSelectedReportForDataProcessing(null);
              clearLastCreatedReport();
            }}
          />
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default ReportManager;
