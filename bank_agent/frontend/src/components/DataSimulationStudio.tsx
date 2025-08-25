import React, { useState, useEffect } from 'react';
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
  Tooltip
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
  RadioButtonUnchecked as RadioButtonUncheckedIcon
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
  const [execution, setExecution] = useState<InvestigationExecution | null>(null);
  const [results, setResults] = useState<InvestigationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [executionMode, setExecutionMode] = useState<'batch' | 'sequential'>('batch');
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

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
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
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
                    tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                    tooltip.style.color = 'white';
                    tooltip.style.padding = '8px 12px';
                    tooltip.style.borderRadius = '4px';
                    tooltip.style.fontSize = '12px';
                    tooltip.style.zIndex = '1000';
                    tooltip.style.pointerEvents = 'none';
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
                    tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                    tooltip.style.color = 'white';
                    tooltip.style.padding = '8px 12px';
                    tooltip.style.borderRadius = '4px';
                    tooltip.style.fontSize = '12px';
                    tooltip.style.zIndex = '1000';
                    tooltip.style.pointerEvents = 'none';
                    tooltip.innerHTML = `
                      <div><strong>Requested Credit Limit</strong></div>
                      <div>Amount: $${viz.data.requested.toLocaleString()}</div>
                      <div>Increase: $${viz.data.increase.toLocaleString()}</div>
                      <div>Percentage: ${viz.data.percentage_increase.toFixed(1)}%</div>
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
            <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Increase:</strong> ${viz.data.increase.toLocaleString()} ({viz.data.percentage_increase.toFixed(1)}%)
              </Typography>
            </Box>
          </Box>
        );

      case 'line_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
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
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
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
                          tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
                          tooltip.style.color = 'white';
                          tooltip.style.padding = '10px 12px';
                          tooltip.style.borderRadius = '6px';
                          tooltip.style.fontSize = '12px';
                          tooltip.style.zIndex = '1000';
                          tooltip.style.pointerEvents = 'none';
                          tooltip.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
                          tooltip.innerHTML = `
                            <div style="font-weight: bold; margin-bottom: 4px;">${label}</div>
                            <div>Credit Utilization: <strong>${viz.data.values[index].toFixed(1)}%</strong></div>
                            <div style="font-size: 10px; margin-top: 4px; opacity: 0.8;">
                              ${viz.data.values[index] < viz.data.threshold ? '✅ Below recommended threshold' : '⚠️ Above recommended threshold'}
                            </div>
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
                      {/* Visible data point with glow effect */}
                      <circle
                        cx={(index / (viz.data.labels.length - 1)) * 100}
                        cy={200 - (viz.data.values[index] / 30) * 200}
                        r="5"
                        fill={theme.colors.primary}
                        stroke="white"
                        strokeWidth="2"
                        style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }}
                      />
                    </g>
                  ))}
                </svg>
              </Box>
            </Box>
            
            {/* X-axis labels */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1, ml: 5 }}>
              {viz.data.labels.map((label: string, index: number) => (
                <Typography 
                  key={index} 
                  variant="caption" 
                  sx={{ 
                    color: theme.colors.textSecondary,
                    fontSize: '11px',
                    fontWeight: 'medium'
                  }}
                >
                  {label}
                </Typography>
              ))}
            </Box>
            
            {/* Summary stats */}
            <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Average Utilization:</strong> {(viz.data.values.reduce((a: number, b: number) => a + b, 0) / viz.data.values.length).toFixed(1)}%
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Peak Utilization:</strong> {Math.max(...viz.data.values).toFixed(1)}% ({viz.data.labels[viz.data.values.indexOf(Math.max(...viz.data.values))]})
              </Typography>
              <Typography variant="body2" sx={{ color: '#4CAF50' }}>
                ✅ All months below {viz.data.threshold}% threshold
              </Typography>
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
            <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: theme.colors.text }}>
                <strong>Overall Risk:</strong> {viz.data.overall_risk} (Score: {viz.data.risk_score})
              </Typography>
            </Box>
          </Box>
        );

      case 'impact_chart':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
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
            <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(76, 175, 80, 0.1)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: '#4CAF50', textAlign: 'center' }}>
                <strong>Improvement:</strong> {viz.data.improvement.toFixed(1)}% reduction in utilization
              </Typography>
            </Box>
          </Box>
        );

      case 'credit_profile_dashboard':
        return (
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
              {viz.title}
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 3 }}>
              {viz.subtitle}
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
              {/* FICO Score */}
              <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                  {viz.data.fico_score}
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  FICO Score
                </Typography>
              </Box>
              
              {/* Credit Limit */}
              <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#2196F3', fontWeight: 'bold' }}>
                  ${(viz.data.credit_limit / 1000).toFixed(0)}k
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Current Credit Limit
                </Typography>
              </Box>
              
              {/* Utilization */}
              <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#FF9800', fontWeight: 'bold' }}>
                  {viz.data.utilization.toFixed(1)}%
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Credit Utilization
                </Typography>
              </Box>
              
              {/* Payment History */}
              <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                  {viz.data.payment_percentage.toFixed(0)}%
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  On-time Payments
                </Typography>
              </Box>
              
              {/* DTI Ratio */}
              <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#9C27B0', fontWeight: 'bold' }}>
                  {viz.data.dti_ratio.toFixed(1)}%
                </Typography>
                <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                  Debt-to-Income Ratio
                </Typography>
              </Box>
              
              {/* Account Age */}
              <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1, textAlign: 'center' }}>
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
          <Box sx={{ mt: 2, p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
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
                      backgroundColor: risk_level === 'Low' ? 'rgba(76, 175, 80, 0.1)' :
                                     risk_level === 'Medium' ? 'rgba(255, 152, 0, 0.1)' :
                                     'rgba(244, 67, 54, 0.1)',
                      borderRadius: 2,
                      border: `1px solid ${
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
                      tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
                      tooltip.style.color = 'white';
                      tooltip.style.padding = '10px 12px';
                      tooltip.style.borderRadius = '6px';
                      tooltip.style.fontSize = '12px';
                      tooltip.style.zIndex = '1000';
                      tooltip.style.pointerEvents = 'none';
                      tooltip.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
                      tooltip.style.maxWidth = '250px';
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
            <Box sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: theme.colors.text, textAlign: 'center' }}>
                <strong>Overall Risk Level:</strong> {viz.data.risk_level} (Score: {viz.data.overall_risk_score})
              </Typography>
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
                            tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.95)';
                            tooltip.style.color = 'white';
                            tooltip.style.padding = '12px 16px';
                            tooltip.style.borderRadius = '8px';
                            tooltip.style.fontSize = '13px';
                            tooltip.style.zIndex = '9999';
                            tooltip.style.pointerEvents = 'none';
                            tooltip.style.boxShadow = '0 6px 16px rgba(0,0,0,0.4)';
                            tooltip.style.border = '1px solid rgba(255,255,255,0.1)';
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

        {/* Selected Investigation Steps as Rectangular Blocks */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
            Selected Investigation Steps
          </Typography>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
            gap: 2 
          }}>
            {selectedSteps.map((step, index) => (
              <Card 
                key={step.id} 
                sx={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: 2,
                  p: 2,
                  minHeight: 120,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}
              >
                <Box>
                  <Typography variant="h6" sx={{ color: theme.colors.text, mb: 1 }}>
                    {step.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 2 }}>
                    {step.description}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Chip 
                    label={step.category?.toUpperCase() || 'ANALYSIS'} 
                    size="small" 
                    color="primary" 
                    variant="outlined"
                  />
                  <Chip 
                    label={step.priority?.toUpperCase() || 'MEDIUM'} 
                    size="small" 
                    color={step.priority === 'high' ? 'error' : step.priority === 'medium' ? 'warning' : 'success'}
                    variant="outlined"
                  />
                </Box>
              </Card>
            ))}
          </Box>
        </Box>

        {/* Execution Controls */}
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 3 }}>
          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={handleExecuteInvestigation}
            disabled={loading || execution?.status === 'running'}
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
            disabled={execution?.status === 'running'}
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
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: 1,
            border: '1px solid rgba(255, 255, 255, 0.1)'
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
      </Box>

      {/* Content */}
      <Box sx={{ p: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}



        {/* Execution Status */}
        {execution && (
          <Card sx={{ mb: 3, backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                {getStatusIcon(execution.status)}
                <Typography variant="h6" sx={{ color: theme.colors.text }}>
                  Execution Status: {execution.status.toUpperCase()}
                </Typography>
                <Chip
                  label={`${execution.progress.toFixed(1)}%`}
                  color={getStatusColor(execution.status) as any}
                />
              </Box>
              
              {execution.status === 'running' && (
                <Box sx={{ mb: 2 }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={execution.progress}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                  {execution.currentStep && (
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mt: 1 }}>
                      Current Step: {execution.currentStep}
                    </Typography>
                  )}
                </Box>
              )}

              {execution.errors.length > 0 && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  <Typography variant="body2">Errors:</Typography>
                  {execution.errors.map((error, index) => (
                    <Typography key={index} variant="body2">• {error}</Typography>
                  ))}
                </Alert>
              )}
            </CardContent>
          </Card>
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
                label="Summary" 
                sx={{ color: theme.colors.text }}
              />
              <Tab 
                label="Data Sources" 
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
                          {step.title}
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
                  Execution Summary
                </Typography>
                <Box sx={{ display: 'flex', gap: 3 }}>
                  <Box sx={{ flex: 1 }}>
                    <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                          Execution Details
                        </Typography>
                        <List dense>
                          <ListItem>
                            <ListItemText
                              primary="Total Steps"
                              secondary={results.length}
                              sx={{ color: theme.colors.text }}
                            />
                          </ListItem>
                          <ListItem>
                            <ListItemText
                              primary="Completed Steps"
                              secondary={results.filter(r => r.status === 'completed').length}
                              sx={{ color: theme.colors.text }}
                            />
                          </ListItem>
                          <ListItem>
                            <ListItemText
                              primary="Total Execution Time"
                              secondary={`${results.reduce((sum, r) => sum + r.execution_time, 0).toFixed(2)}s`}
                              sx={{ color: theme.colors.text }}
                            />
                          </ListItem>
                        </List>
                      </CardContent>
                    </Card>
                  </Box>
                  
                  <Box sx={{ flex: 1 }}>
                    <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                          Key Insights
                        </Typography>
                        <List dense>
                          {results.flatMap(r => r.insights).slice(0, 5).map((insight, index) => (
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
                      </CardContent>
                    </Card>
                  </Box>
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
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default DataSimulationStudio;
