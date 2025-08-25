import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  TextField
} from '@mui/material';

import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  TableChart as TableChartIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Send as SendIcon,
  Chat as ChatIcon
} from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import apiService from '../services/api';

interface InvestigationStep {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: string;
  estimatedTime: string;
}

interface InvestigationExecution {
  executionId: string;
  customerId: number;
  customerName: string;
  reportId?: string;
  selectedSteps: InvestigationStep[];
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: string;
  completedAt?: string;
  results: Record<string, any>;
  errors: string[];
  progress: number;
  currentStep?: string;
  stepStatus: Record<string, 'pending' | 'running' | 'completed' | 'failed'>;
}

interface InvestigationResult {
  step_id: string;
  step_title: string;
  execution_time: number;
  status: string;
  data: Record<string, any>;
  visualizations: Array<{
    type: string;
    title: string;
    data: any;
  }>;
  insights: string[];
  recommendations: string[];
  metadata: Record<string, any>;
}

interface ChatMessage {
  message_id: string;
  session_id: string;
  customer_id: number;
  customer_name: string;
  message_type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: any;
}

interface ChatSession {
  session_id: string;
  customer_id: number;
  customer_name: string;
  execution_id?: string;
  investigation_results?: any;
  created_at: string;
  updated_at?: string;
  message_count: number;
}

interface DataSimulationStudioProps {
  customerId: number;
  customerName: string;
  reportId?: string;
  selectedSteps: InvestigationStep[];
  onClose: () => void;
}

const DataSimulationStudio: React.FC<DataSimulationStudioProps> = ({
  customerId,
  customerName,
  reportId,
  selectedSteps,
  onClose
}) => {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const [execution, setExecution] = useState<InvestigationExecution | null>(null);
  const [results, setResults] = useState<InvestigationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [executionMode, setExecutionMode] = useState<'batch' | 'sequential'>('batch');
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatSession, setChatSession] = useState<ChatSession | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [sessionId] = useState(`session_${customerId}_${Date.now()}`);

  // Finalize Decision state
  const [decisionData, setDecisionData] = useState({
    decision: 'approved' as 'approved' | 'rejected',
    approvedAmount: 0,
    reason: '',
    customerEmail: '',
    emailSubject: '',
    emailBody: ''
  });
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailManuallyEdited, setEmailManuallyEdited] = useState(false);

  // Decision Documentation state
  const [showDecisionDoc, setShowDecisionDoc] = useState(false);
  const [decisionDocLoading, setDecisionDocLoading] = useState(false);
  const [decisionDocUrl, setDecisionDocUrl] = useState('');
  const [decisionDocSummary, setDecisionDocSummary] = useState(null);
  const [finalDecisionData, setFinalDecisionData] = useState<typeof decisionData | null>(null);
  const [emailSent, setEmailSent] = useState(false);

  // Pre-fill customer email when tab is opened
  useEffect(() => {
    if (activeTab === 4 && customerName && !emailManuallyEdited) {
      console.log('🔍 Tab 4 opened, attempting to populate customer email');
      console.log('🔍 Customer Name:', customerName);
      console.log('🔍 Results:', results);
      
      // Try to get customer email from profile data
      const customerProfile = results.find(r => r.data?.customer_profile);
      console.log('🔍 Customer Profile:', customerProfile);
      
      if (customerProfile?.data?.customer_profile?.email) {
        console.log('✅ Found email in customer profile:', customerProfile.data.customer_profile.email);
        setDecisionData(prev => ({
          ...prev,
          customerEmail: customerProfile.data.customer_profile.email
        }));
      } else {
        // Try to get email from customer demographics data
        const customerDemo = results.find(r => r.data?.customer_demographics);
        console.log('🔍 Customer Demographics:', customerDemo);
        
        if (customerDemo?.data?.customer_demographics?.email) {
          console.log('✅ Found email in customer demographics:', customerDemo.data.customer_demographics.email);
          setDecisionData(prev => ({
            ...prev,
            customerEmail: customerDemo.data.customer_demographics.email
          }));
        } else {
          // Fallback: use a default email based on customer name
          const defaultEmail = `${customerName.toLowerCase().replace(' ', '.')}@example.com`;
          console.log('⚠️ Using fallback email:', defaultEmail);
          setDecisionData(prev => ({
            ...prev,
            customerEmail: defaultEmail
          }));
        }
      }
    }
  }, [activeTab, customerName, results, emailManuallyEdited]);

  // Persist decision documentation state
  useEffect(() => {
    // If we have a decision doc URL, ensure the decision doc section stays visible
    if (decisionDocUrl && !showDecisionDoc) {
      console.log('🔒 Restoring decision documentation state');
      setShowDecisionDoc(true);
    }
  }, [decisionDocUrl, showDecisionDoc]);

  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const handleExecuteInvestigation = async () => {
    try {
      setLoading(true);
      setError('');

      // Debug: Log the request data
      const requestData = {
        customerId,
        customerName,
        reportId,
        selectedSteps,
        executionMode
      };
      console.log('🔍 Executing investigation with data:', requestData);

      const response = await apiService.executeInvestigation(requestData);

      if (response.success && response.execution) {
        console.log('🔍 Frontend received execution:', response.execution);
        setExecution(response.execution);
        
        // Start polling for updates
        const executionId = response.execution.executionId;
        console.log('🔍 Using execution ID for polling:', executionId);
        
        const interval = setInterval(async () => {
          await pollExecutionStatus(executionId);
        }, 2000);
        
        setPollingInterval(interval);
      } else {
        setError(response.error || 'Failed to start investigation execution');
      }
    } catch (err) {
      setError('Error starting investigation execution');
      console.error('Error executing investigation:', err);
    } finally {
      setLoading(false);
    }
  };

  const pollExecutionStatus = async (executionId: string) => {
    try {
      const response = await apiService.getInvestigationExecution(executionId);
      
      if (response.success && response.execution) {
        setExecution(response.execution);
        
        // Stop polling if execution is completed or failed
        if (['completed', 'failed', 'cancelled'].includes(response.execution.status)) {
          if (pollingInterval) {
            clearInterval(pollingInterval);
            setPollingInterval(null);
          }
          
          // Process results
          if (response.execution.status === 'completed') {
            await processResults(response.execution);
          }
        }
      }
    } catch (err) {
      console.error('Error polling execution status:', err);
    }
  };

  const processResults = async (execution: InvestigationExecution) => {
    try {
      const processedResults: InvestigationResult[] = [];
      
      for (const [stepId, resultData] of Object.entries(execution.results)) {
        if (resultData && typeof resultData === 'object') {
          processedResults.push({
            step_id: stepId,
            step_title: resultData.step_title || 'Unknown Step',
            execution_time: resultData.execution_time || 0,
            status: resultData.status || 'completed',
            data: resultData.data || {},
            visualizations: resultData.visualizations || [],
            insights: resultData.insights || [],
            recommendations: resultData.recommendations || [],
            metadata: resultData.metadata || {}
          });
        }
      }
      
      setResults(processedResults);
    } catch (err) {
      console.error('Error processing results:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'failed': return 'error';
      case 'cancelled': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon />;
      case 'running': return <CircularProgress size={20} />;
      case 'failed': return <ErrorIcon />;
      case 'cancelled': return <WarningIcon />;
      default: return <InfoIcon />;
    }
  };

  const renderVisualization = (viz: any) => {
    switch (viz.type) {
      case 'comparison_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'flex', gap: 3, alignItems: 'flex-end', height: 200 }}>
              <Box sx={{ textAlign: 'center', flex: 1 }}>
                <Box
                  sx={{
                    height: (viz.data.current / Math.max(viz.data.current, viz.data.requested)) * 150,
                    backgroundColor: '#2196F3',
                    borderRadius: '8px 8px 0 0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: '#1976D2',
                      transform: 'scale(1.02)'
                    }
                  }}
                  onMouseEnter={(e) => {
                    const tooltip = document.createElement('div');
                    tooltip.style.position = 'absolute';
                    tooltip.style.left = `${e.clientX + 10}px`;
                    tooltip.style.top = `${e.clientY - 10}px`;
                    tooltip.style.backgroundColor = theme.colors.surface;
                    tooltip.style.color = theme.colors.text;
                    tooltip.style.padding = '8px 12px';
                    tooltip.style.borderRadius = '4px';
                    tooltip.style.fontSize = '12px';
                    tooltip.style.zIndex = '1000';
                    tooltip.style.pointerEvents = 'none';
                    tooltip.style.border = `1px solid ${theme.colors.border}`;
                    tooltip.innerHTML = `
                      <div><strong>Current Credit Limit</strong></div>
                      <div>Amount: $${viz.data.current.toLocaleString()}</div>
                      <div>Status: Active</div>
                    `;
                    document.body.appendChild(tooltip);
                    (e.target as any).tooltip = tooltip;
                  }}
                  onMouseLeave={(e) => {
                    const tooltip = (e.target as any).tooltip;
                    if (tooltip) {
                      document.body.removeChild(tooltip);
                      (e.target as any).tooltip = null;
                    }
                  }}
                >
                  ${(viz.data.current / 1000).toFixed(0)}k
                </Box>
                <Typography variant="body2" sx={{ color: theme.colors.text, mt: 1 }}>
                  Current Limit
                </Typography>
              </Box>
              <Box sx={{ textAlign: 'center', flex: 1 }}>
                <Box
                  sx={{
                    height: (viz.data.requested / Math.max(viz.data.current, viz.data.requested)) * 150,
                    backgroundColor: '#4CAF50',
                    borderRadius: '8px 8px 0 0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: '#388E3C',
                      transform: 'scale(1.02)'
                    }
                  }}
                  onMouseEnter={(e) => {
                    const tooltip = document.createElement('div');
                    tooltip.style.position = 'absolute';
                    tooltip.style.left = `${e.clientX + 10}px`;
                    tooltip.style.top = `${e.clientY - 10}px`;
                    tooltip.style.backgroundColor = theme.colors.surface;
                    tooltip.style.color = theme.colors.text;
                    tooltip.style.padding = '8px 12px';
                    tooltip.style.borderRadius = '4px';
                    tooltip.style.fontSize = '12px';
                    tooltip.style.zIndex = '1000';
                    tooltip.style.pointerEvents = 'none';
                    tooltip.style.border = `1px solid ${theme.colors.border}`;
                    tooltip.innerHTML = `
                      <div><strong>Requested Credit Limit</strong></div>
                      <div>Amount: $${viz.data.requested.toLocaleString()}</div>
                      <div>Status: Pending</div>
                    `;
                    document.body.appendChild(tooltip);
                    (e.target as any).tooltip = tooltip;
                  }}
                  onMouseLeave={(e) => {
                    const tooltip = (e.target as any).tooltip;
                    if (tooltip) {
                      document.body.removeChild(tooltip);
                      (e.target as any).tooltip = null;
                    }
                  }}
                >
                  ${(viz.data.requested / 1000).toFixed(0)}k
                </Box>
                <Typography variant="body2" sx={{ color: theme.colors.text, mt: 1 }}>
                  Requested Limit
                </Typography>
              </Box>
            </Box>
            <Box sx={{ mt: 2, p: 2, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Increase:</strong> ${viz.data.increase.toLocaleString()} ({viz.data.percentage_increase.toFixed(1)}%)
              </Typography>
            </Box>
          </Box>
        );

      case 'line_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ position: 'relative', height: 200 }}>
              {/* Y-axis labels */}
              <Box sx={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 40, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary, fontSize: '10px' }}>30%</Typography>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary, fontSize: '10px' }}>20%</Typography>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary, fontSize: '10px' }}>10%</Typography>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary, fontSize: '10px' }}>0%</Typography>
              </Box>
              
              {/* Chart area with padding for y-axis */}
              <Box sx={{ position: 'absolute', left: 40, right: 0, top: 0, bottom: 0 }}>
                {/* Grid lines */}
                {[0, 10, 20, 30].map((value) => (
                  <Box
                    key={value}
                    sx={{
                      position: 'absolute',
                      left: 0,
                      right: 0,
                      top: (1 - value / 30) * 200,
                      height: 1,
                      backgroundColor: theme.colors.border,
                      zIndex: 0
                    }}
                  />
                ))}
                
                {/* Threshold line */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: (1 - viz.data.threshold / 30) * 200,
                    left: 0,
                    right: 0,
                    height: 2,
                    backgroundColor: '#FF9800',
                    zIndex: 1
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{
                    position: 'absolute',
                    top: (1 - viz.data.threshold / 30) * 200 - 20,
                    right: 0,
                    color: '#FF9800',
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }}
                >
                  {viz.data.threshold}% Threshold
                </Typography>
                
                {/* Interactive Line chart */}
                <svg width="100%" height="200" style={{ position: 'absolute', top: 0, left: 0 }}>
                  {/* Smooth line connecting all points */}
                  <polyline
                    fill="none"
                    stroke={theme.colors.primary}
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={viz.data.labels.map((label: string, index: number) => 
                      `${(index / (viz.data.labels.length - 1)) * 100},${200 - (viz.data.values[index] / 30) * 200}`
                    ).join(' ')}
                  />
                  
                  {/* Data points with hover effects */}
                  {viz.data.labels.map((label: string, index: number) => (
                    <g key={index}>
                      {/* Invisible larger circle for hover area */}
                      <circle
                        cx={(index / (viz.data.labels.length - 1)) * 100}
                        cy={200 - (viz.data.values[index] / 30) * 200}
                        r="10"
                        fill="transparent"
                        style={{ cursor: 'pointer' }}
                        onMouseEnter={(e) => {
                          const tooltip = document.createElement('div');
                          tooltip.style.position = 'absolute';
                          tooltip.style.left = `${e.clientX + 10}px`;
                          tooltip.style.top = `${e.clientY - 10}px`;
                          tooltip.style.backgroundColor = theme.colors.surface;
                          tooltip.style.color = theme.colors.text;
                          tooltip.style.padding = '8px 12px';
                          tooltip.style.borderRadius = '4px';
                          tooltip.style.fontSize = '12px';
                          tooltip.style.zIndex = '1000';
                          tooltip.style.pointerEvents = 'none';
                          tooltip.style.border = `1px solid ${theme.colors.border}`;
                          tooltip.innerHTML = `
                            <div><strong>${label}</strong></div>
                            <div>Utilization: ${viz.data.values[index]}%</div>
                          `;
                          document.body.appendChild(tooltip);
                          (e.target as any).tooltip = tooltip;
                        }}
                        onMouseLeave={(e) => {
                          const tooltip = (e.target as any).tooltip;
                          if (tooltip) {
                            document.body.removeChild(tooltip);
                            (e.target as any).tooltip = null;
                          }
                        }}
                      />
                      {/* Visible data point */}
                      <circle
                        cx={(index / (viz.data.labels.length - 1)) * 100}
                        cy={200 - (viz.data.values[index] / 30) * 200}
                        r="4"
                        fill={theme.colors.primary}
                        stroke="white"
                        strokeWidth="2"
                      />
                    </g>
                  ))}
                </svg>
              </Box>
            </Box>
          </Box>
        );

      case 'pie_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              <Box sx={{ flex: 1, textAlign: 'center' }}>
                <Box sx={{ width: 120, height: 120, margin: '0 auto', position: 'relative' }}>
                  <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle
                      cx="60"
                      cy="60"
                      r="50"
                      fill="none"
                      stroke="#4CAF50"
                      strokeWidth="20"
                      strokeDasharray={`${(viz.data.values[0] / (viz.data.values[0] + viz.data.values[1])) * 314} 314`}
                      transform="rotate(-90 60 60)"
                    />
                    <circle
                      cx="60"
                      cy="60"
                      r="50"
                      fill="none"
                      stroke="#F44336"
                      strokeWidth="20"
                      strokeDasharray={`${(viz.data.values[1] / (viz.data.values[0] + viz.data.values[1])) * 314} 314`}
                      strokeDashoffset={-(viz.data.values[0] / (viz.data.values[0] + viz.data.values[1])) * 314}
                      transform="rotate(-90 60 60)"
                    />
                  </svg>
                </Box>
              </Box>
              <Box sx={{ flex: 1 }}>
                {viz.data.labels.map((label: string, index: number) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        backgroundColor: viz.data.colors[index],
                        mr: 1
                      }}
                    />
                    <Typography variant="body2" sx={{ color: theme.colors.text }}>
                      {label}: {viz.data.values[index]}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          </Box>
        );

      case 'fico_comparison_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'flex', gap: 3, alignItems: 'center' }}>
              {/* Customer Score */}
              <Box sx={{ flex: 1, textAlign: 'center' }}>
                <Box sx={{ position: 'relative', width: 120, height: 60, margin: '0 auto' }}>
                  <svg width="120" height="60" viewBox="0 0 120 60">
                    <path
                      d="M 20 60 A 40 40 0 0 1 100 60"
                      fill="none"
                      stroke="#E0E0E0"
                      strokeWidth="6"
                    />
                    <path
                      d="M 20 60 A 40 40 0 0 1 100 60"
                      fill="none"
                      stroke="#4CAF50"
                      strokeWidth="6"
                      strokeDasharray={`${(viz.data.customer_score / viz.data.max_score) * 126} 126`}
                    />
                  </svg>
                  <Typography
                    variant="h5"
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      color: theme.colors.text,
                      fontWeight: 'bold'
                    }}
                  >
                    {viz.data.customer_score}
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: theme.colors.text, mt: 1, fontWeight: 'bold' }}>
                  Your Score
                </Typography>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary }}>
                  {viz.data.score_range}
                </Typography>
              </Box>
              
              {/* Comparison Arrow */}
              <Box sx={{ fontSize: '24px', color: theme.colors.textSecondary }}>
                vs
              </Box>
              
              {/* Similar Profile Average */}
              <Box sx={{ flex: 1, textAlign: 'center' }}>
                <Box sx={{ position: 'relative', width: 120, height: 60, margin: '0 auto' }}>
                  <svg width="120" height="60" viewBox="0 0 120 60">
                    <path
                      d="M 20 60 A 40 40 0 0 1 100 60"
                      fill="none"
                      stroke="#E0E0E0"
                      strokeWidth="6"
                    />
                    <path
                      d="M 20 60 A 40 40 0 0 1 100 60"
                      fill="none"
                      stroke="#2196F3"
                      strokeWidth="6"
                      strokeDasharray={`${(viz.data.similar_profile_avg / viz.data.max_score) * 126} 126`}
                    />
                  </svg>
                  <Typography
                    variant="h5"
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      color: theme.colors.text,
                      fontWeight: 'bold'
                    }}
                  >
                    {viz.data.similar_profile_avg}
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: theme.colors.text, mt: 1 }}>
                  Similar Profiles Avg
                </Typography>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary }}>
                  {viz.data.similar_profile_count.toLocaleString()} profiles
                </Typography>
              </Box>
            </Box>
            
            {/* Comparison Details */}
            <Box sx={{ mt: 3, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: theme.colors.text, mb: 1 }}>
                <strong>Profile Segment:</strong> {viz.data.profile_segment}
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Percentile:</strong> Top {100 - viz.data.percentile}% of similar profiles
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: viz.data.customer_score >= viz.data.similar_profile_avg ? '#4CAF50' : '#FF9800',
                  mt: 1,
                  fontWeight: 'bold'
                }}
              >
                {viz.data.customer_score >= viz.data.similar_profile_avg 
                  ? `✅ Your score is ${viz.data.customer_score - viz.data.similar_profile_avg} points above average`
                  : `⚠️ Your score is ${viz.data.similar_profile_avg - viz.data.customer_score} points below average`
                }
              </Typography>
            </Box>
          </Box>
        );

      case 'progress_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ position: 'relative', mb: 2 }}>
              <Box sx={{ height: 20, backgroundColor: '#E0E0E0', borderRadius: 10, position: 'relative' }}>
                <Box
                  sx={{
                    height: '100%',
                    width: `${Math.min(viz.data.current_dti, 100)}%`,
                    backgroundColor: viz.data.current_dti <= viz.data.excellent_threshold ? '#4CAF50' :
                                   viz.data.current_dti <= viz.data.good_threshold ? '#FF9800' : '#F44336',
                    borderRadius: 10,
                    transition: 'width 0.3s ease'
                  }}
                />
                <Typography
                  variant="body2"
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    color: 'white',
                    fontWeight: 'bold',
                    textShadow: '1px 1px 2px rgba(0,0,0,0.5)'
                  }}
                >
                  {viz.data.current_dti.toFixed(1)}%
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="caption" sx={{ color: '#4CAF50' }}>
                Excellent: ≤{viz.data.excellent_threshold}%
              </Typography>
              <Typography variant="caption" sx={{ color: '#FF9800' }}>
                Good: ≤{viz.data.good_threshold}%
              </Typography>
              <Typography variant="caption" sx={{ color: '#F44336' }}>
                Acceptable: ≤{viz.data.acceptable_threshold}%
              </Typography>
            </Box>
          </Box>
        );

      case 'radar_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ width: 200, height: 200, margin: '0 auto', position: 'relative' }}>
                <svg width="200" height="200" viewBox="0 0 200 200">
                  {/* Radar grid */}
                  {[20, 40, 60, 80, 100].map((value, index) => (
                    <circle
                      key={index}
                      cx="100"
                      cy="100"
                      r={value}
                      fill="none"
                      stroke="#E0E0E0"
                      strokeWidth="1"
                    />
                  ))}
                  
                  {/* Radar data */}
                  <polygon
                    points={viz.data.categories.map((category: string, index: number) => {
                      const angle = (index / viz.data.categories.length) * 2 * Math.PI - Math.PI / 2;
                      const radius = (viz.data.values[index] / viz.data.max_value) * 80;
                      return `${100 + radius * Math.cos(angle)},${100 + radius * Math.sin(angle)}`;
                    }).join(' ')}
                    fill="rgba(76, 175, 80, 0.3)"
                    stroke="#4CAF50"
                    strokeWidth="2"
                  />
                </svg>
              </Box>
              <Box sx={{ mt: 2 }}>
                {viz.data.categories.map((category: string, index: number) => (
                  <Typography key={index} variant="caption" sx={{ color: theme.colors.textSecondary, mr: 2 }}>
                    {category}: {viz.data.values[index]}
                  </Typography>
                ))}
              </Box>
            </Box>
          </Box>
        );

      case 'bubble_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              {viz.data.accounts.map((account: any, index: number) => (
                <Box
                  key={index}
                  sx={{
                    p: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: 2,
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    minWidth: 120,
                    textAlign: 'center'
                  }}
                >
                  <Typography variant="body2" sx={{ color: theme.colors.text, fontWeight: 'bold' }}>
                    {account.type}
                  </Typography>
                  <Typography variant="h6" sx={{ color: theme.colors.primary }}>
                    {account.count}
                  </Typography>
                  <Typography variant="caption" sx={{ color: theme.colors.textSecondary }}>
                    Age: {account.age}m
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>
        );

      case 'matrix_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              {Object.entries(viz.data.risk_levels).map(([level, factors]: [string, any]) => (
                <Box
                  key={level}
                  sx={{
                    flex: 1,
                    p: 2,
                    backgroundColor: level === 'Low Risk' ? 'rgba(76, 175, 80, 0.1)' :
                                   level === 'Medium Risk' ? 'rgba(255, 152, 0, 0.1)' :
                                   'rgba(244, 67, 54, 0.1)',
                    borderRadius: 2,
                    border: `1px solid ${
                      level === 'Low Risk' ? '#4CAF50' :
                      level === 'Medium Risk' ? '#FF9800' : '#F44336'
                    }`
                  }}
                >
                  <Typography variant="subtitle2" sx={{ color: theme.colors.text, mb: 1 }}>
                    {level}
                  </Typography>
                  {factors.map((factor: string, index: number) => (
                    <Typography key={index} variant="caption" sx={{ color: theme.colors.textSecondary, display: 'block' }}>
                      • {factor}
                    </Typography>
                  ))}
                </Box>
              ))}
            </Box>
            <Box sx={{ mt: 2, p: 2, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Overall Risk:</strong> {viz.data.overall_risk} (Score: {viz.data.risk_score})
              </Typography>
            </Box>
          </Box>
        );

      case 'impact_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'flex', gap: 3, alignItems: 'center' }}>
              <Box sx={{ flex: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#2196F3' }}>
                  {viz.data.current_utilization.toFixed(1)}%
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Current Utilization
                </Typography>
              </Box>
              <Box sx={{ fontSize: '24px', color: theme.colors.textSecondary }}>
                →
              </Box>
              <Box sx={{ flex: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#4CAF50' }}>
                  {viz.data.projected_utilization.toFixed(1)}%
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Projected Utilization
                </Typography>
              </Box>
            </Box>
            <Box sx={{ mt: 2, p: 2, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: '#4CAF50', textAlign: 'center' }}>
                <strong>Improvement:</strong> {viz.data.improvement.toFixed(1)}% reduction in utilization
              </Typography>
            </Box>
          </Box>
        );

      case 'credit_profile_dashboard':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
              {/* FICO Score */}
              <Box sx={{ p: 2, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                  {viz.data.fico_score}
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  FICO Score
                </Typography>
              </Box>
              
              {/* Credit Limit */}
              <Box sx={{ p: 2, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#2196F3', fontWeight: 'bold' }}>
                  ${(viz.data.credit_limit / 1000).toFixed(0)}k
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Current Credit Limit
                </Typography>
              </Box>
              
              {/* Utilization */}
              <Box sx={{ p: 2, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#FF9800', fontWeight: 'bold' }}>
                  {viz.data.utilization.toFixed(1)}%
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Credit Utilization
                </Typography>
              </Box>
              
              {/* Payment History */}
              <Box sx={{ p: 2, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                  {viz.data.payment_percentage.toFixed(0)}%
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  On-time Payments
                </Typography>
              </Box>
              
              {/* DTI Ratio */}
              <Box sx={{ p: 2, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#9C27B0', fontWeight: 'bold' }}>
                  {viz.data.dti_ratio.toFixed(1)}%
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Debt-to-Income Ratio
                </Typography>
              </Box>
              
              {/* Account Age */}
              <Box sx={{ p: 2, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#607D8B', fontWeight: 'bold' }}>
                  {viz.data.account_age}m
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Oldest Account Age
                </Typography>
              </Box>
            </Box>
          </Box>
        );

      case 'risk_assessment_matrix':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: theme.colors.surface, border: `1px solid ${theme.colors.border}`, borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mb: 3 }}>
              {Object.entries(viz.data.risk_factors).map(([risk_type, risk_level]: [string, any]) => {
                const riskDescriptions = {
                  "payment_risk": "Measures payment history reliability. Low risk = no late payments, High risk = multiple late payments.",
                  "utilization_risk": "Measures credit card usage. Low risk = <30% utilization, High risk = >50% utilization.",
                  "dti_risk": "Debt-to-Income ratio. Low risk = <36% of income goes to debt, High risk = >43% of income goes to debt.",
                  "fico_risk": "Credit score assessment. Low risk = FICO ≥700, High risk = FICO <650."
                };
                
                return (
                  <Box
                    key={risk_type}
                    sx={{
                      p: 2,
                      backgroundColor: risk_level === 'Low' ? theme.colors.surface :
                                     risk_level === 'Medium' ? theme.colors.surface :
                                     theme.colors.surface,
                      borderRadius: 2,
                      border: `2px solid ${
                        risk_level === 'Low' ? '#4CAF50' :
                        risk_level === 'Medium' ? '#FF9800' : '#F44336'
                      }`,
                      textAlign: 'center',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        transform: 'scale(1.02)',
                        boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
                      }
                    }}
                    onMouseEnter={(e) => {
                      const tooltip = document.createElement('div');
                      tooltip.style.position = 'absolute';
                      tooltip.style.left = `${e.clientX + 10}px`;
                      tooltip.style.top = `${e.clientY - 10}px`;
                      tooltip.style.backgroundColor = theme.colors.surface;
                      tooltip.style.color = theme.colors.text;
                      tooltip.style.padding = '10px 12px';
                      tooltip.style.borderRadius = '6px';
                      tooltip.style.fontSize = '12px';
                      tooltip.style.zIndex = '1000';
                      tooltip.style.pointerEvents = 'none';
                      tooltip.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
                      tooltip.style.maxWidth = '250px';
                      tooltip.style.border = `1px solid ${theme.colors.border}`;
                      tooltip.innerHTML = `
                        <div style="font-weight: bold; margin-bottom: 4px;">${risk_type.replace('_', ' ').toUpperCase()}</div>
                        <div style="margin-bottom: 4px;"><strong>Risk Level:</strong> ${risk_level}</div>
                        <div style="font-size: 11px; opacity: 0.9;">${riskDescriptions[risk_type as keyof typeof riskDescriptions] || 'Risk assessment based on credit profile analysis.'}</div>
                      `;
                      document.body.appendChild(tooltip);
                      (e.target as any).tooltip = tooltip;
                    }}
                    onMouseLeave={(e) => {
                      const tooltip = (e.target as any).tooltip;
                      if (tooltip) {
                        document.body.removeChild(tooltip);
                        (e.target as any).tooltip = null;
                      }
                    }}
                  >
                    <Typography variant="subtitle2" sx={{ color: theme.colors.text, mb: 1, textTransform: 'capitalize' }}>
                      {risk_type.replace('_', ' ')}
                    </Typography>
                    <Typography variant="h6" sx={{ 
                      color: risk_level === 'Low' ? '#4CAF50' :
                             risk_level === 'Medium' ? '#FF9800' : '#F44336',
                      fontWeight: 'bold'
                    }}>
                      {risk_level}
                    </Typography>
                  </Box>
                );
              })}
            </Box>
          </Box>
        );

      case 'utilization_trend_enhanced':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ position: 'relative', height: 300, minWidth: '100%', overflow: 'visible' }}>
              {/* Y-axis labels */}
              <Box sx={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 50, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary, fontSize: '11px' }}>30%</Typography>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary, fontSize: '11px' }}>20%</Typography>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary, fontSize: '11px' }}>10%</Typography>
                <Typography variant="caption" sx={{ color: theme.colors.textSecondary, fontSize: '11px' }}>0%</Typography>
              </Box>
              
              {/* Chart area with padding for y-axis */}
              <Box sx={{ position: 'absolute', left: 50, right: 20, top: 0, bottom: 0, minWidth: 'calc(100% - 70px)' }}>
                {/* Grid lines */}
                {[0, 10, 20, 30].map((value) => (
                  <Box
                    key={value}
                    sx={{
                      position: 'absolute',
                      left: 0,
                      right: 0,
                      top: (1 - value / 30) * 300,
                      height: 1,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      zIndex: 0
                    }}
                  />
                ))}
                
                {/* Threshold line */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: (1 - viz.data.threshold / 30) * 300,
                    left: 0,
                    right: 0,
                    height: 2,
                    backgroundColor: '#FF9800',
                    zIndex: 1
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{
                    position: 'absolute',
                    top: (1 - viz.data.threshold / 30) * 300 - 20,
                    right: 0,
                    color: '#FF9800',
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }}
                >
                  {viz.data.threshold}% Threshold
                </Typography>
                
                {/* Interactive Bar Chart */}
                <svg width="100%" height="300" style={{ position: 'absolute', top: 0, left: 0, minWidth: '100%' }}>
                  {viz.data.monthly_data.map((item: any, index: number) => {
                    const totalWidth = 100;
                    const barWidth = totalWidth / viz.data.monthly_data.length * 0.8; // 80% of available space per bar
                    const barSpacing = totalWidth / viz.data.monthly_data.length * 0.2; // 20% spacing
                    const xPos = (index / viz.data.monthly_data.length) * totalWidth + barSpacing / 2;
                    const barHeight = (item.utilization / 30) * 300;
                    const yPos = 300 - barHeight;
                    
                    // Determine bar color based on utilization vs threshold
                    const barColor = item.utilization < viz.data.threshold ? '#4CAF50' : '#FF9800';
                    
                    return (
                      <g key={index}>
                        {/* Bar with hover effects */}
                        <rect
                          x={`${xPos}%`}
                          y={yPos}
                          width={`${barWidth}%`}
                          height={barHeight}
                          fill={barColor}
                          stroke="white"
                          strokeWidth="1"
                          style={{ 
                            cursor: 'pointer',
                            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))',
                            transition: 'all 0.2s ease'
                          }}
                          onMouseEnter={(e) => {
                            // Add hover effect
                            (e.target as any).style.filter = 'drop-shadow(0 4px 8px rgba(0,0,0,0.5)) brightness(1.1)';
                            
                            // Create tooltip
                            const tooltip = document.createElement('div');
                            tooltip.style.position = 'fixed';
                            tooltip.style.left = `${e.clientX + 15}px`;
                            tooltip.style.top = `${e.clientY - 15}px`;
                            tooltip.style.backgroundColor = theme.colors.surface;
                            tooltip.style.color = theme.colors.text;
                            tooltip.style.padding = '12px 16px';
                            tooltip.style.borderRadius = '8px';
                            tooltip.style.fontSize = '13px';
                            tooltip.style.zIndex = '9999';
                            tooltip.style.pointerEvents = 'none';
                            tooltip.style.boxShadow = '0 6px 16px rgba(0,0,0,0.4)';
                            tooltip.style.border = `1px solid ${theme.colors.border}`;
                            tooltip.style.minWidth = '180px';
                            tooltip.innerHTML = `
                              <div style="font-weight: bold; margin-bottom: 6px; color: #4CAF50; font-size: 14px;">${item.month}</div>
                              <div style="margin-bottom: 4px; font-size: 15px;">
                                <strong>Credit Utilization:</strong> <span style="color: #FFD700; font-weight: bold;">${item.utilization.toFixed(1)}%</span>
                              </div>
                              <div style="font-size: 11px; margin-top: 6px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2);">
                                ${item.utilization < viz.data.threshold ? 
                                  '✅ Below recommended threshold' : 
                                  '⚠️ Above recommended threshold'
                                }
                              </div>
                            `;
                            document.body.appendChild(tooltip);
                            (e.target as any).tooltip = tooltip;
                          }}
                          onMouseLeave={(e) => {
                            // Remove hover effect
                            (e.target as any).style.filter = 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))';
                            
                            // Remove tooltip
                            const tooltip = (e.target as any).tooltip;
                            if (tooltip) {
                              document.body.removeChild(tooltip);
                              (e.target as any).tooltip = null;
                            }
                          }}
                        />
                        
                        {/* Value label on top of bar */}
                        <text
                          x={`${xPos + barWidth / 2}%`}
                          y={yPos - 8}
                          textAnchor="middle"
                          fill="white"
                          fontSize="11"
                          fontWeight="bold"
                          style={{ filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.8))' }}
                        >
                          {item.utilization.toFixed(1)}%
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </Box>
            </Box>
            
            {/* X-axis labels */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1, ml: 6, mr: 2, position: 'relative' }}>
              {viz.data.monthly_data.map((item: any, index: number) => {
                const totalWidth = 100;
                const barWidth = totalWidth / viz.data.monthly_data.length * 0.8;
                const barSpacing = totalWidth / viz.data.monthly_data.length * 0.2;
                const xPos = (index / viz.data.monthly_data.length) * totalWidth + barSpacing / 2 + barWidth / 2;
                
                return (
                  <Typography 
                    key={index} 
                    variant="caption" 
                    sx={{ 
                      color: theme.colors.textSecondary,
                      fontSize: '12px',
                      fontWeight: 'medium',
                      position: 'absolute',
                      left: `${xPos}%`,
                      transform: 'translateX(-50%)',
                      textAlign: 'center'
                    }}
                  >
                    {item.month}
                  </Typography>
                );
              })}
            </Box>
            
            {/* Enhanced Summary stats */}
            <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Average Utilization:</strong> {viz.data.average_utilization.toFixed(1)}%
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Peak Utilization:</strong> {viz.data.peak_utilization.toFixed(1)}% ({viz.data.peak_month})
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Trend Direction:</strong> {viz.data.trend_direction.charAt(0).toUpperCase() + viz.data.trend_direction.slice(1)}
              </Typography>
              <Typography variant="body2" sx={{ color: '#4CAF50' }}>
                ✅ All months below {viz.data.threshold}% threshold
              </Typography>
            </Box>
          </Box>
        );

      case 'recommendation_confidence':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ mb: 3 }}>
              {Object.entries(viz.data.factors).map(([factor_name, score]: [string, any]) => (
                <Box key={factor_name} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ color: theme.colors.text, textTransform: 'capitalize' }}>
                      {factor_name.replace(/_/g, ' ').replace('score', '')}
                    </Typography>
                  </Box>
                  <Box sx={{ flex: 1, mx: 2 }}>
                    <Box sx={{ height: 8, backgroundColor: '#E0E0E0', borderRadius: 4 }}>
                      <Box
                        sx={{
                          height: '100%',
                          width: `${score}%`,
                          backgroundColor: score >= 80 ? '#4CAF50' :
                                         score >= 60 ? '#FF9800' : '#F44336',
                          borderRadius: 4
                        }}
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" sx={{ color: theme.colors.text, minWidth: 40 }}>
                    {score}
                  </Typography>
                </Box>
              ))}
            </Box>
            <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1 }}>
              <Typography variant="h6" sx={{ color: theme.colors.text, textAlign: 'center' }}>
                Overall Confidence: {viz.data.overall_confidence.toFixed(1)}%
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.textSecondary, textAlign: 'center' }}>
                Recommendation: <strong style={{ color: '#4CAF50' }}>{viz.data.recommendation}</strong>
              </Typography>
            </Box>
          </Box>
        );

      case 'credit_limit_impact':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 3, mb: 3 }}>
              {/* Current State */}
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#2196F3' }}>
                  ${(viz.data.current_limit / 1000).toFixed(0)}k
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Current Credit Limit
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Utilization: {viz.data.current_utilization.toFixed(1)}%
                </Typography>
              </Box>
              
              {/* Arrow */}
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography variant="h4" sx={{ color: theme.colors.textSecondary }}>
                  →
                </Typography>
              </Box>
              
              {/* Requested State */}
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#4CAF50' }}>
                  ${(viz.data.requested_limit / 1000).toFixed(0)}k
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Requested Credit Limit
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Utilization: {viz.data.projected_utilization.toFixed(1)}%
                </Typography>
              </Box>
            </Box>
            
            {/* Impact Summary */}
            <Box sx={{ p: 2, backgroundColor: 'rgba(76, 175, 80, 0.1)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: '#4CAF50', textAlign: 'center', fontWeight: 'bold' }}>
                ✅ Credit Limit Increase: ${viz.data.increase_amount.toLocaleString()} ({viz.data.increase_percentage.toFixed(1)}%)
              </Typography>
              <Typography variant="body2" sx={{ color: '#4CAF50', textAlign: 'center' }}>
                📉 Utilization Improvement: {viz.data.utilization_improvement.toFixed(1)}% reduction
              </Typography>
            </Box>
          </Box>
        );

      case 'confidence_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ mb: 3 }}>
              {viz.data.factors.map((factor: any, index: number) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ color: theme.colors.text }}>
                      {factor.factor}
                    </Typography>
                  </Box>
                  <Box sx={{ flex: 1, mx: 2 }}>
                    <Box sx={{ height: 8, backgroundColor: '#E0E0E0', borderRadius: 4 }}>
                      <Box
                        sx={{
                          height: '100%',
                          width: `${factor.score}%`,
                          backgroundColor: factor.score >= 80 ? '#4CAF50' :
                                         factor.score >= 60 ? '#FF9800' : '#F44336',
                          borderRadius: 4
                        }}
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" sx={{ color: theme.colors.text, minWidth: 40 }}>
                    {factor.score}
                  </Typography>
                </Box>
              ))}
            </Box>
            <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1 }}>
              <Typography variant="h6" sx={{ color: theme.colors.text, textAlign: 'center' }}>
                Overall Confidence: {viz.data.overall_confidence.toFixed(1)}%
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.textSecondary, textAlign: 'center' }}>
                Recommendation: <strong style={{ color: '#4CAF50' }}>{viz.data.recommendation}</strong>
              </Typography>
            </Box>
          </Box>
        );

      case 'table':
        return (
          <TableContainer component={Paper} sx={{ mt: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {viz.columns?.map((col: string, index: number) => (
                    <TableCell key={index}>{col}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(viz.data || {}).map(([key, value], index) => (
                  <TableRow key={index}>
                    <TableCell>{key}</TableCell>
                    <TableCell>{String(value)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        );
      
      default:
        return (
          <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
            <Typography variant="body2" sx={{ color: theme.colors.text }}>
              {viz.content || JSON.stringify(viz.data, null, 2)}
            </Typography>
          </Box>
        );
    }
  };

  const renderStepResult = (result: InvestigationResult) => (
    <Accordion key={result.step_id} sx={{ mb: 2, backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: theme.colors.text }} />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
          {getStatusIcon(result.status)}
          <Typography variant="h6" sx={{ color: theme.colors.text, flexGrow: 1 }}>
            {result.step_title}
          </Typography>
          <Chip
            label={`${result.execution_time.toFixed(2)}s`}
            size="small"
            variant="outlined"
            sx={{ color: theme.colors.textSecondary }}
          />
          <Chip
            label={result.status.toUpperCase()}
            color={getStatusColor(result.status) as any}
            size="small"
          />
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Box sx={{ display: 'flex', gap: 3 }}>
            {/* Insights */}
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                Insights
              </Typography>
              <List dense>
                {result.insights.map((insight, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <InfoIcon sx={{ color: theme.colors.primary }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={insight}
                      sx={{ color: theme.colors.text }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>

            {/* Recommendations */}
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                Recommendations
              </Typography>
              <List dense>
                {result.recommendations.map((recommendation, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <AssessmentIcon sx={{ color: theme.colors.success }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={recommendation}
                      sx={{ color: theme.colors.text }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          </Box>

          {/* Visualizations */}
          <Box>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
              Visualizations
            </Typography>
            {result.visualizations.map((viz, index) => (
              <Box key={index} sx={{ mb: 3 }}>
                {renderVisualization(viz)}
              </Box>
            ))}
          </Box>
        </Box>
      </AccordionDetails>
    </Accordion>
  );

  // Chat functions
  const handleSendMessage = async () => {
    if (!chatInput.trim() || chatLoading) return;
    
    const message = chatInput.trim();
    setChatInput('');
    setChatLoading(true);
    
    // Add user message to chat immediately
    const userMessage: ChatMessage = {
      message_id: `user_${Date.now()}`,
      session_id: sessionId,
      customer_id: customerId,
      customer_name: customerName,
      message_type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    
    try {
      const response = await apiService.sendChatMessage({
        session_id: sessionId,
        customer_id: customerId,
        customer_name: customerName,
        content: message,
        execution_id: execution?.executionId,
        investigation_results: {
          results: results,
          cumulative_data: results.length > 0 ? results[0].data : {}
        }
      });
      
      if (response.success && response.message) {
        setChatMessages(prev => [...prev, response.message]);
        if (response.session) {
          setChatSession(response.session);
        }
      } else {
        // Add error message to chat
        setChatMessages(prev => [...prev, {
          message_id: `error_${Date.now()}`,
          session_id: sessionId,
          customer_id: customerId,
          customer_name: customerName,
          message_type: 'assistant',
          content: `Error: ${response.error || 'Failed to get response'}`,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setChatMessages(prev => [...prev, {
        message_id: `error_${Date.now()}`,
        session_id: sessionId,
        customer_id: customerId,
        customer_name: customerName,
        message_type: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const renderScenarioAnalysis = (scenarioData: any) => {
    return (
      <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
        <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
          {scenarioData.title}
        </Typography>
        <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
          {scenarioData.subtitle}
        </Typography>
        
        {/* Scenarios Table */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 2 }}>
            Credit Limit Variations
          </Typography>
          <TableContainer component={Paper} sx={{ backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: theme.colors.text, fontWeight: 'bold' }}>Variation</TableCell>
                  <TableCell sx={{ color: theme.colors.text, fontWeight: 'bold' }}>Increase</TableCell>
                  <TableCell sx={{ color: theme.colors.text, fontWeight: 'bold' }}>New Limit</TableCell>
                  <TableCell sx={{ color: theme.colors.text, fontWeight: 'bold' }}>Utilization</TableCell>
                  <TableCell sx={{ color: theme.colors.text, fontWeight: 'bold' }}>Risk</TableCell>
                  <TableCell sx={{ color: theme.colors.text, fontWeight: 'bold' }}>Recommendation</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {scenarioData.scenarios.map((scenario: any, index: number) => (
                  <TableRow key={index}>
                    <TableCell sx={{ color: theme.colors.text }}>
                      {scenario.variation_percentage}%
                    </TableCell>
                    <TableCell sx={{ color: theme.colors.text }}>
                      ${scenario.increase_amount.toLocaleString()}
                    </TableCell>
                    <TableCell sx={{ color: theme.colors.text }}>
                      ${scenario.new_credit_limit.toLocaleString()}
                    </TableCell>
                    <TableCell sx={{ color: theme.colors.text }}>
                      {scenario.projected_utilization.toFixed(1)}%
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={scenario.risk_level}
                        size="small"
                        color={scenario.risk_level === 'Low' ? 'success' : scenario.risk_level === 'Medium' ? 'warning' : 'error'}
                      />
                    </TableCell>
                    <TableCell sx={{ color: theme.colors.text }}>
                      {scenario.recommendation}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
        
        {/* Spending Trends */}
        <Box>
          <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 2 }}>
            Spending Pattern Analysis
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
            <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.03)' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: theme.colors.primary }}>
                  ${scenarioData.spending_trends.monthly_average.toLocaleString()}
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Monthly Average
                </Typography>
              </CardContent>
            </Card>
            <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.03)' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#4CAF50' }}>
                  {scenarioData.spending_trends.trend_direction}
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Trend Direction
                </Typography>
              </CardContent>
            </Card>
            <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.03)' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#FF9800' }}>
                  ${scenarioData.spending_trends.projected_spending.toLocaleString()}
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Projected Spending
                </Typography>
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Box>
    );
  };

  // Email generation and sending functions
  const generateEmailContent = () => {
    const subject = decisionData.emailSubject || `Credit Limit Decision - ${customerName}`;
    
    let body = '';
    if (decisionData.decision === 'approved') {
      body = `Dear ${customerName},

Thank you for your credit limit increase request. After careful review of your application and credit profile, I am pleased to inform you that your request has been **APPROVED**.

**Decision Details:**
- Approved Amount: $${decisionData.approvedAmount.toLocaleString()}
- Decision Date: ${new Date().toLocaleDateString()}

**Reason for Approval:**
${decisionData.reason}

Your new credit limit will be effective immediately. You can view your updated credit limit in your online banking portal or mobile app.

If you have any questions about this decision, please don't hesitate to contact our customer service team.

Best regards,
Banking Team`;
    } else {
      body = `Dear ${customerName},

Thank you for your credit limit increase request. After careful review of your application and credit profile, I regret to inform you that your request has been **DECLINED**.

**Decision Details:**
- Decision: Declined
- Decision Date: ${new Date().toLocaleDateString()}

**Reason for Decline:**
${decisionData.reason}

We understand this may be disappointing, and we encourage you to continue building your credit profile. You may be eligible for a credit limit increase in the future as your financial situation improves.

If you have any questions about this decision or would like to discuss ways to improve your credit profile, please don't hesitate to contact our customer service team.

Best regards,
Banking Team`;
    }
    
    setDecisionData(prev => ({
      ...prev,
      emailSubject: subject,
      emailBody: body
    }));
  };

  const sendEmail = async () => {
    if (!decisionData.customerEmail || !decisionData.reason) {
      alert('Please fill in all required fields');
      return;
    }

    setEmailLoading(true);
    try {
      const emailData = {
        to: decisionData.customerEmail,
        subject: decisionData.emailSubject,
        body: decisionData.emailBody,
        decision: decisionData.decision,
        approvedAmount: decisionData.approvedAmount,
        reason: decisionData.reason,
        customerName,
        customerId,
        sessionId: execution?.executionId || `session_${customerId}_${Date.now()}`
      };

      // Send email via API
      const response = await apiService.sendEmail(emailData);
      
      if (response.success) {
        alert('Email sent successfully!');
        // Show decision documentation option
        setShowDecisionDoc(true);
        setEmailSent(true);
        
        // Store the decision data for PDF generation
        setFinalDecisionData({ ...decisionData });
        
        // Reset form
        setDecisionData({
          decision: 'approved',
          approvedAmount: 0,
          reason: '',
          customerEmail: '',
          emailSubject: '',
          emailBody: ''
        });
      } else {
        alert(`Error sending email: ${response.error || 'Unknown error'}`);
      }
      
    } catch (error) {
      console.error('Error sending email:', error);
      alert('Error sending email. Please try again.');
    } finally {
      setEmailLoading(false);
    }
  };

  const generateDecisionDocumentation = async () => {
    setDecisionDocLoading(true);
    try {
      // Use finalDecisionData if available, otherwise use current decisionData
      const decisionDataToUse = finalDecisionData || decisionData;
      
      const docData = {
        customerId,
        customerName,
        decision: decisionDataToUse.decision,
        approvedAmount: decisionDataToUse.approvedAmount,
        reason: decisionDataToUse.reason,
        emailData: {
          to: decisionDataToUse.customerEmail,
          subject: decisionDataToUse.emailSubject,
          body: decisionDataToUse.emailBody
        },
        investigationResults: results,
        chatHistory: chatMessages,
        execution: execution,
        timestamp: new Date().toISOString()
      };

      console.log('📄 Generating decision documentation with data:', docData);

      const response = await apiService.generateDecisionDocumentation(docData);
      
      console.log('📄 PDF generation response:', response);
      
      if (response.success) {
        setDecisionDocUrl(response.pdf_url);
        setDecisionDocSummary(response.summary);
        console.log('✅ PDF generated successfully, URL:', response.pdf_url);
        alert('Decision documentation generated successfully!');
        
        // Ensure we stay on the Finalize Decision tab
        console.log('🔒 Keeping activeTab at 4 (Finalize Decision)');
      } else {
        console.error('❌ PDF generation failed:', response.error);
        alert(`Error generating documentation: ${response.error || 'Unknown error'}`);
      }
      
    } catch (error) {
      console.error('❌ Error generating decision documentation:', error);
      alert('Error generating decision documentation. Please try again.');
    } finally {
      setDecisionDocLoading(false);
    }
  };

  return (
    <Box sx={{ 
      position: 'fixed', 
      top: 0, 
      left: 0, 
      right: 0, 
      bottom: 0, 
      backgroundColor: theme.colors.background,
      zIndex: 1300,
      overflow: 'auto'
    }}>
      {/* Header */}
      <Box sx={{ 
        p: 3, 
        borderBottom: `1px solid ${theme.colors.border}`,
        backgroundColor: theme.colors.surface
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" sx={{ color: theme.colors.text }}>
            Data Simulation & Visualization Studio
          </Typography>
          <Button
            variant="outlined"
            onClick={onClose}
            sx={{ color: theme.colors.text, borderColor: theme.colors.border }}
          >
            Close
          </Button>
        </Box>
        
        <Typography variant="body1" sx={{ color: theme.colors.textSecondary, mb: 2 }}>
          Customer: {customerName} (ID: {customerId}) | Selected Steps: {selectedSteps.length}
        </Typography>

        {/* Planning Interface - Only show when no execution is running */}
        {!execution && (
          <>
            {/* Selected Investigation Steps as Rectangular Blocks */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6"
                sx={{ color: theme.colors.text, mb: 2 }}>
                Selected Investigation Steps:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {selectedSteps.map((step, index) => (
                  <Box
                    key={index}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      backgroundColor: theme.colors.surface,
                      border: `1px solid ${theme.colors.border}`,
                      color: theme.colors.text,
                      fontSize: '0.9rem',
                      fontWeight: 500
                    }}
                  >
                    {step.title || step.id}
                  </Box>
                ))}
              </Box>
            </Box>

            {/* Execution Controls */}
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 3 }}>
              <Button
                variant="contained"
                startIcon={<PlayIcon />}
                onClick={handleExecuteInvestigation}
                disabled={loading}
                sx={{ 
                  backgroundColor: theme.colors.primary,
                  minWidth: 200,
                  height: 48
                }}
              >
                {loading ? 'Starting...' : 'Execute Investigation'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={() => setExecutionMode(executionMode === 'batch' ? 'sequential' : 'batch')}
                sx={{ 
                  color: theme.colors.text, 
                  borderColor: theme.colors.border,
                  minWidth: 150,
                  height: 48
                }}
              >
                Mode: {executionMode === 'batch' ? 'Batch' : 'Sequential'}
              </Button>

              {/* Execution Mode Info */}
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1,
                p: 1.5,
                backgroundColor: theme.colors.surface,
                borderRadius: 1,
                border: `1px solid ${theme.colors.border}`
              }}>
                <InfoIcon sx={{ color: theme.colors.textSecondary, fontSize: 20 }} />
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  {executionMode === 'batch' 
                    ? 'Batch mode: Execute all steps in parallel' 
                    : 'Sequential mode: Execute steps one by one'
                  }
                </Typography>
              </Box>
            </Box>
          </>
        )}

        {/* Execution Status - Show when investigation is running or completed */}
        {execution && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
              Investigation Status: {execution.status.toUpperCase()}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              {getStatusIcon(execution.status)}
              <Typography variant="body1" sx={{ color: theme.colors.textSecondary }}>
                Progress: {execution.progress.toFixed(1)}%
              </Typography>
              {execution.status === 'running' && execution.currentStep && (
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Current Step: {execution.currentStep}
                </Typography>
              )}
            </Box>
            {execution.status === 'running' && (
              <LinearProgress 
                variant="determinate" 
                value={execution.progress}
                sx={{ height: 6, borderRadius: 3 }}
              />
            )}
            {execution.errors.length > 0 && (
              <Alert severity="error" sx={{ mt: 2 }}>
                <Typography variant="body2">Errors:</Typography>
                {execution.errors.map((error, index) => (
                  <Typography key={index} variant="body2">• {error}</Typography>
                ))}
              </Alert>
            )}
          </Box>
        )}
      </Box>

      {/* Content */}
      <Box sx={{ p: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Results Tabs */}
        {results.length > 0 && (
          <Box sx={{ width: '100%' }}>
            <Tabs 
              value={activeTab} 
              onChange={(_, newValue) => setActiveTab(newValue)}
              sx={{ 
                borderBottom: `1px solid ${theme.colors.border}`,
                mb: 3
              }}
            >
              <Tab 
                label="Step Results" 
                sx={{ color: theme.colors.text }}
              />
              <Tab 
                label="Visualizations" 
                sx={{ color: theme.colors.text }}
              />
              <Tab 
                label="Chat with Investigations" 
                sx={{ color: theme.colors.text }}
              />
              <Tab 
                label="Data Sources" 
                sx={{ color: theme.colors.text }}
              />
              <Tab 
                label="Finalize Decision" 
                sx={{ color: theme.colors.text }}
              />
            </Tabs>

            {/* Tab Content */}
            {activeTab === 0 && (
              <Box>
                <Typography variant="h5" sx={{ color: theme.colors.text, mb: 3 }}>
                  Investigation Results
                </Typography>
                {execution && execution.selectedSteps.map((step: any, index: number) => {
                  const stepStatus = execution.stepStatus?.[step.id] || 'pending';
                  const result = results?.find((r: any) => r.step_id === step.id);
                  
                  // Debug logging
                  console.log(`Step ${step.id}: ${stepStatus}, Result:`, result);
                  
                  const getStepStatusIcon = (status: string) => {
                    switch (status) {
                      case 'completed':
                        return <CheckCircleIcon sx={{ color: '#4CAF50', fontSize: 20 }} />;
                      case 'running':
                        return <CircularProgress size={20} sx={{ color: '#FF9800' }} />;
                      case 'failed':
                        return <ErrorIcon sx={{ color: '#F44336', fontSize: 20 }} />;
                      default:
                        return <RadioButtonUncheckedIcon sx={{ color: theme.colors.textSecondary, fontSize: 20 }} />;
                    }
                  };
                  
                  const getStepStatusColor = (status: string) => {
                    switch (status) {
                      case 'completed':
                        return { bg: 'rgba(76, 175, 80, 0.2)', color: '#4CAF50' };
                      case 'running':
                        return { bg: 'rgba(255, 152, 0, 0.2)', color: '#FF9800' };
                      case 'failed':
                        return { bg: 'rgba(244, 67, 54, 0.2)', color: '#F44336' };
                      default:
                        return { bg: 'rgba(255, 255, 255, 0.1)', color: theme.colors.textSecondary };
                    }
                  };
                  
                  return (
                    <Box
                      key={index}
                      sx={{
                        p: 2,
                        mb: 2,
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: 2,
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        transition: 'all 0.3s ease',
                        ...(stepStatus === 'running' && {
                          borderColor: '#FF9800',
                          backgroundColor: 'rgba(255, 152, 0, 0.05)'
                        })
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {getStepStatusIcon(stepStatus)}
                        <Typography variant="body1" sx={{ color: theme.colors.text }}>
                          {step.title || step.id}
                        </Typography>
                        {stepStatus === 'running' && (
                          <Typography variant="caption" sx={{ color: '#FF9800', fontStyle: 'italic' }}>
                            Processing...
                          </Typography>
                        )}
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {result && (
                          <Chip
                            label={`${result.execution_time}s`}
                            size="small"
                            sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)', color: theme.colors.textSecondary }}
                          />
                        )}
                        <Chip
                          label={stepStatus.toUpperCase()}
                          size="small"
                          sx={{
                            backgroundColor: getStepStatusColor(stepStatus).bg,
                            color: getStepStatusColor(stepStatus).color,
                            fontWeight: 'bold'
                          }}
                        />
                        {result && (
                          <ExpandMoreIcon sx={{ color: theme.colors.textSecondary, cursor: 'pointer' }} />
                        )}
                      </Box>
                    </Box>
                  );
                })}
              </Box>
            )}

            {activeTab === 1 && (
              <Box>
                <Typography variant="h5" sx={{ color: theme.colors.text, mb: 3 }}>
                  Comprehensive Visualizations
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
                  Interactive charts and analysis based on all investigation steps
                </Typography>
                
                {/* Cumulative Visualizations */}
                {results && results.length > 0 && results[0].visualizations && results[0].visualizations.map((viz: any, index: number) => (
                  <Box key={index} sx={{ mb: 3 }}>
                    {renderVisualization(viz)}
                  </Box>
                ))}
              </Box>
            )}

            {activeTab === 2 && (
              <Box>
                <Typography variant="h5" sx={{ color: theme.colors.text, mb: 3 }}>
                  Chat with Investigations
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
                  Ask questions about the investigation results and get AI-powered insights. Use /scenario to analyze credit limit variations.
                </Typography>
                
                {/* Chat Messages */}
                <Box sx={{ 
                  height: 400, 
                  overflowY: 'auto', 
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: 2,
                  p: 2,
                  mb: 2,
                  backgroundColor: 'rgba(255, 255, 255, 0.02)'
                }}>
                  {chatMessages.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <ChatIcon sx={{ fontSize: 48, color: theme.colors.textSecondary, mb: 2 }} />
                      <Typography variant="body1" sx={{ color: theme.colors.textSecondary, mb: 1 }}>
                        Start a conversation about the investigation results
                      </Typography>
                      <Typography variant="body2" sx={{ color: theme.colors.textSecondary, opacity: 0.7 }}>
                        Try asking: "What are the key risk factors?" or "/scenario 8000" for credit limit analysis
                      </Typography>
                    </Box>
                  ) : (
                    chatMessages.map((message, index) => (
                      <Box
                        key={index}
                        sx={{
                          display: 'flex',
                          justifyContent: message.message_type === 'user' ? 'flex-end' : 'flex-start',
                          mb: 2
                        }}
                      >
                        <Box
                          sx={{
                            maxWidth: '70%',
                            p: 2,
                            borderRadius: 2,
                            backgroundColor: message.message_type === 'user' 
                              ? theme.colors.primary 
                              : 'rgba(255, 255, 255, 0.05)',
                            border: `1px solid ${message.message_type === 'user' 
                              ? theme.colors.primary 
                              : theme.colors.border}`,
                            color: message.message_type === 'user' ? 'white' : theme.colors.text
                          }}
                        >
                          <Box
                            sx={{
                              color: 'inherit',
                              '& > *:first-of-type': { mt: 0 },
                              '& > *:last-of-type': { mb: 0 }
                            }}
                          >
                            <ReactMarkdown
                              components={{
                                // Style the markdown elements
                                p: ({ children }) => (
                                  <Typography variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 } }}>
                                    {children}
                                  </Typography>
                                ),
                                h1: ({ children }) => (
                                  <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold' }}>
                                    {children}
                                  </Typography>
                                ),
                                h2: ({ children }) => (
                                  <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
                                    {children}
                                  </Typography>
                                ),
                                h3: ({ children }) => (
                                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                                    {children}
                                  </Typography>
                                ),
                                strong: ({ children }) => (
                                  <Box component="span" sx={{ fontWeight: 'bold' }}>
                                    {children}
                                  </Box>
                                ),
                                em: ({ children }) => (
                                  <Box component="span" sx={{ fontStyle: 'italic' }}>
                                    {children}
                                  </Box>
                                ),
                                ul: ({ children }) => (
                                  <Box component="ul" sx={{ pl: 2, mb: 1 }}>
                                    {children}
                                  </Box>
                                ),
                                ol: ({ children }) => (
                                  <Box component="ol" sx={{ pl: 2, mb: 1 }}>
                                    {children}
                                  </Box>
                                ),
                                li: ({ children }) => (
                                  <Typography variant="body2" component="li" sx={{ mb: 0.5 }}>
                                    {children}
                                  </Typography>
                                ),
                                code: ({ children }) => (
                                  <Box
                                    component="code"
                                    sx={{
                                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                      padding: '2px 4px',
                                      borderRadius: 1,
                                      fontSize: '0.875em',
                                      fontFamily: 'monospace'
                                    }}
                                  >
                                    {children}
                                  </Box>
                                ),
                                pre: ({ children }) => (
                                  <Box
                                    component="pre"
                                    sx={{
                                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                                      padding: 1,
                                      borderRadius: 1,
                                      overflow: 'auto',
                                      mb: 1
                                    }}
                                  >
                                    {children}
                                  </Box>
                                ),
                                blockquote: ({ children }) => (
                                  <Box
                                    component="blockquote"
                                    sx={{
                                      borderLeft: `3px solid ${theme.colors.primary}`,
                                      pl: 2,
                                      ml: 0,
                                      mb: 1,
                                      fontStyle: 'italic'
                                    }}
                                  >
                                    {children}
                                  </Box>
                                )
                              }}
                            >
                              {message.content}
                            </ReactMarkdown>
                          </Box>
                          
                          {/* Render scenario analysis if present */}
                          {message.metadata?.scenario_analysis && (
                            <Box sx={{ mt: 2 }}>
                              {renderScenarioAnalysis(message.metadata.scenario_analysis)}
                            </Box>
                          )}
                          
                          <Typography variant="caption" sx={{ 
                            display: 'block', 
                            mt: 1, 
                            opacity: 0.7,
                            color: message.message_type === 'user' ? 'rgba(255,255,255,0.7)' : theme.colors.textSecondary
                          }}>
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Box>
                      </Box>
                    ))
                  )}
                  
                  {chatLoading && (
                    <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                      <Box sx={{ p: 2, borderRadius: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CircularProgress size={16} />
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                            Analyzing...
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  )}
                </Box>
                
                {/* Chat Input */}
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Box
                    component="input"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask about the investigation results... (use /scenario for credit limit analysis)"
                    sx={{
                      flex: 1,
                      p: 2,
                      border: `1px solid ${theme.colors.border}`,
                      borderRadius: 2,
                      backgroundColor: 'rgba(255, 255, 255, 0.02)',
                      color: theme.colors.text,
                      fontSize: '14px',
                      '&::placeholder': {
                        color: theme.colors.textSecondary,
                        opacity: 0.7
                      },
                      '&:focus': {
                        outline: 'none',
                        borderColor: theme.colors.primary
                      }
                    }}
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!chatInput.trim() || chatLoading}
                    variant="contained"
                    sx={{
                      backgroundColor: theme.colors.primary,
                      color: 'white',
                      '&:hover': {
                        backgroundColor: theme.colors.primary,
                        opacity: 0.9
                      }
                    }}
                  >
                    <SendIcon />
                  </Button>
                </Box>
              </Box>
            )}

            {activeTab === 3 && (
              <Box>
                <Typography variant="h5" sx={{ color: theme.colors.text, mb: 3 }}>
                  Data Sources Used
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {results.map(result => (
                    <Box key={result.step_id}>
                      <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                        <CardContent>
                          <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                            {result.step_title}
                          </Typography>
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                            Data Sources: {Object.keys(result.data).join(', ')}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Box>
                  ))}
                </Box>
              </Box>
            )}

            {activeTab === 4 && (
              <Box>
                <Typography variant="h5" sx={{ color: theme.colors.text, mb: 3 }}>
                  Finalize Credit Decision
                </Typography>
                
                {/* Decision Form */}
                <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ color: theme.colors.text, mb: 3 }}>
                      Decision Details
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      {/* Decision Type */}
                      <Box>
                        <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 1 }}>
                          Decision *
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                          <Button
                            variant={decisionData.decision === 'approved' ? 'contained' : 'outlined'}
                            onClick={() => setDecisionData(prev => ({ ...prev, decision: 'approved' }))}
                            sx={{
                              backgroundColor: decisionData.decision === 'approved' ? '#4CAF50' : 'transparent',
                              color: decisionData.decision === 'approved' ? 'white' : theme.colors.text,
                              borderColor: '#4CAF50',
                              '&:hover': {
                                backgroundColor: decisionData.decision === 'approved' ? '#45a049' : 'rgba(76, 175, 80, 0.1)'
                              }
                            }}
                          >
                            Approve
                          </Button>
                          <Button
                            variant={decisionData.decision === 'rejected' ? 'contained' : 'outlined'}
                            onClick={() => setDecisionData(prev => ({ ...prev, decision: 'rejected' }))}
                            sx={{
                              backgroundColor: decisionData.decision === 'rejected' ? '#F44336' : 'transparent',
                              color: decisionData.decision === 'rejected' ? 'white' : theme.colors.text,
                              borderColor: '#F44336',
                              '&:hover': {
                                backgroundColor: decisionData.decision === 'rejected' ? '#d32f2f' : 'rgba(244, 67, 54, 0.1)'
                              }
                            }}
                          >
                            Reject
                          </Button>
                        </Box>
                      </Box>

                      {/* Approved Amount (only show if approved) */}
                      {decisionData.decision === 'approved' && (
                        <Box>
                          <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 1 }}>
                            Approved Amount *
                          </Typography>
                          <Box
                            component="input"
                            type="number"
                            value={decisionData.approvedAmount}
                            onChange={(e) => setDecisionData(prev => ({ ...prev, approvedAmount: parseFloat(e.target.value) || 0 }))}
                            placeholder="Enter approved amount"
                            sx={{
                              width: '100%',
                              p: 2,
                              border: `1px solid ${theme.colors.border}`,
                              borderRadius: 1,
                              backgroundColor: 'rgba(255, 255, 255, 0.02)',
                              color: theme.colors.text,
                              fontSize: '16px',
                              '&:focus': {
                                outline: 'none',
                                borderColor: theme.colors.primary
                              }
                            }}
                          />
                        </Box>
                      )}

                      {/* Reason */}
                      <Box>
                        <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 1 }}>
                          Decision Reason *
                        </Typography>
                        <Box
                          component="textarea"
                          value={decisionData.reason}
                          onChange={(e) => setDecisionData(prev => ({ ...prev, reason: e.target.value }))}
                          placeholder="Provide detailed reason for approval or rejection..."
                          rows={4}
                          sx={{
                            width: '100%',
                            p: 2,
                            border: `1px solid ${theme.colors.border}`,
                            borderRadius: 1,
                            backgroundColor: 'rgba(255, 255, 255, 0.02)',
                            color: theme.colors.text,
                            fontSize: '14px',
                            fontFamily: 'inherit',
                            resize: 'vertical',
                            '&:focus': {
                              outline: 'none',
                              borderColor: theme.colors.primary
                            }
                          }}
                        />
                      </Box>

                      {/* Customer Email */}
                      <Box>
                        <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 1 }}>
                          Customer Email *
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <TextField
                            type="email"
                            value={decisionData.customerEmail}
                            onChange={(e) => {
                              setDecisionData(prev => ({ ...prev, customerEmail: e.target.value }));
                              setEmailManuallyEdited(true);
                            }}
                            placeholder="customer@example.com"
                            fullWidth
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                color: theme.colors.text,
                                backgroundColor: theme.colors.surface,
                                borderColor: theme.colors.border,
                                '& fieldset': {
                                  borderColor: theme.colors.border,
                                },
                                '&:hover fieldset': {
                                  borderColor: theme.colors.primary,
                                },
                                '&.Mui-focused fieldset': {
                                  borderColor: theme.colors.primary,
                                },
                              },
                              '& .MuiInputLabel-root': {
                                color: theme.colors.textSecondary,
                              },
                            }}
                          />
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => {
                              const defaultEmail = `${customerName.toLowerCase().replace(' ', '.')}@example.com`;
                              setDecisionData(prev => ({ ...prev, customerEmail: defaultEmail }));
                              setEmailManuallyEdited(false);
                            }}
                            sx={{
                              borderColor: theme.colors.primary,
                              color: theme.colors.primary,
                              minWidth: 'auto',
                              px: 2
                            }}
                          >
                            Auto-fill
                          </Button>
                        </Box>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>

                {/* Email Preview */}
                <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ color: theme.colors.text, mb: 3 }}>
                      Email Communication
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      {/* Email Subject */}
                      <Box>
                        <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 1 }}>
                          Email Subject
                        </Typography>
                        <TextField
                          value={decisionData.emailSubject}
                          onChange={(e) => setDecisionData(prev => ({ ...prev, emailSubject: e.target.value }))}
                          placeholder="Credit Limit Decision - [Customer Name]"
                          fullWidth
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              color: theme.colors.text,
                              backgroundColor: theme.colors.surface,
                              borderColor: theme.colors.border,
                              '& fieldset': {
                                borderColor: theme.colors.border,
                              },
                              '&:hover fieldset': {
                                borderColor: theme.colors.primary,
                              },
                              '&.Mui-focused fieldset': {
                                borderColor: theme.colors.primary,
                              },
                            },
                            '& .MuiInputLabel-root': {
                              color: theme.colors.textSecondary,
                            },
                          }}
                        />
                      </Box>

                      {/* Email Body */}
                      <Box>
                        <Typography variant="subtitle1" sx={{ color: theme.colors.text, mb: 1 }}>
                          Email Body
                        </Typography>
                        <TextField
                          value={decisionData.emailBody}
                          onChange={(e) => setDecisionData(prev => ({ ...prev, emailBody: e.target.value }))}
                          placeholder="Email content will be generated automatically..."
                          multiline
                          rows={8}
                          fullWidth
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              color: theme.colors.text,
                              backgroundColor: theme.colors.surface,
                              borderColor: theme.colors.border,
                              '& fieldset': {
                                borderColor: theme.colors.border,
                              },
                              '&:hover fieldset': {
                                borderColor: theme.colors.primary,
                              },
                              '&.Mui-focused fieldset': {
                                borderColor: theme.colors.primary,
                              },
                            },
                            '& .MuiInputLabel-root': {
                              color: theme.colors.textSecondary,
                            },
                          }}
                        />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button
                    variant="outlined"
                    onClick={() => generateEmailContent()}
                    sx={{
                      borderColor: theme.colors.primary,
                      color: theme.colors.primary,
                      '&:hover': {
                        borderColor: theme.colors.primary,
                        backgroundColor: 'rgba(255, 255, 255, 0.05)'
                      }
                    }}
                  >
                    Generate Email
                  </Button>
                  <Button
                    variant="contained"
                    onClick={() => sendEmail()}
                    disabled={emailLoading || !decisionData.customerEmail || !decisionData.reason}
                    sx={{
                      backgroundColor: theme.colors.primary,
                      color: 'white',
                      '&:hover': {
                        backgroundColor: theme.colors.primary,
                        opacity: 0.9
                      }
                    }}
                  >
                    {emailLoading ? <CircularProgress size={20} color="inherit" /> : 'Send Email'}
                  </Button>
                </Box>

                {/* Proceed to Decision Documentation Button - Shows after email is sent */}
                {emailSent && (
                  <Box sx={{ mt: 3, p: 3, backgroundColor: 'rgba(76, 175, 80, 0.1)', borderRadius: 2, border: '1px solid rgba(76, 175, 80, 0.3)' }}>
                    <Typography variant="h6" sx={{ color: '#4CAF50', mb: 2, display: 'flex', alignItems: 'center' }}>
                      <CheckCircleIcon sx={{ mr: 1 }} />
                      Email Sent Successfully!
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
                      The decision email has been sent to the customer. You can now proceed to generate and view the complete decision documentation.
                    </Typography>
                    <Button
                      variant="contained"
                      size="large"
                      onClick={() => {
                        // Extract session ID from the execution or create one
                        const sessionId = execution?.executionId || `decision_doc_${customerId}_${Date.now()}`;
                        navigate(`/decision-documentation?sessionId=${sessionId}`);
                      }}
                      sx={{
                        backgroundColor: '#9C27B0',
                        color: 'white',
                        fontSize: '1.1rem',
                        fontWeight: 600,
                        py: 1.5,
                        px: 3,
                        '&:hover': {
                          backgroundColor: '#7B1FA2',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 6px 20px rgba(0, 0, 0, 0.2)'
                        }
                      }}
                    >
                      Proceed to Decision Documentation
                    </Button>
                  </Box>
                )}

                {/* Decision Documentation Section */}
                {showDecisionDoc && (
                  <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', mt: 3 }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ color: theme.colors.text, mb: 3 }}>
                        Decision Documentation
                      </Typography>
                      
                      {!decisionDocUrl ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                            Generate a comprehensive PDF report documenting all investigation steps, AI analysis, visualizations, chat history, and final decision.
                          </Typography>
                          <Button
                            variant="contained"
                            onClick={generateDecisionDocumentation}
                            disabled={decisionDocLoading}
                            sx={{
                              backgroundColor: '#9C27B0',
                              color: 'white',
                              '&:hover': {
                                backgroundColor: '#7B1FA2',
                                opacity: 0.9
                              }
                            }}
                          >
                            {decisionDocLoading ? (
                              <CircularProgress size={20} color="inherit" />
                            ) : (
                              'Generate Decision Documentation'
                            )}
                          </Button>
                        </Box>
                      ) : (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                            Decision documentation has been generated successfully!
                          </Typography>
                          
                          <Button
                            variant="contained"
                            onClick={() => {
                              // Extract session ID from the PDF URL
                              const sessionId = decisionDocUrl.split('/').pop()?.replace('.pdf', '') || 'decision_doc_5_20250825_034258';
                              navigate(`/decision-documentation?sessionId=${sessionId}`);
                            }}
                            sx={{
                              backgroundColor: '#4CAF50',
                              color: 'white',
                              '&:hover': {
                                backgroundColor: '#45a049',
                                opacity: 0.9
                              }
                            }}
                          >
                            View Documentation
                          </Button>
                          
                          {decisionDocSummary && (
                            <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
                              <Typography variant="subtitle2" sx={{ color: theme.colors.text, mb: 1 }}>
                                Report Summary:
                              </Typography>
                              <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                                {decisionDocSummary}
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                )}
              </Box>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default DataSimulationStudio;
