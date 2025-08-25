import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Drawer,
  Collapse,
  Fade,
  Slide,
  Avatar,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Autocomplete,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Storage as DataSourcesIcon,
  Settings as DataProcessingIcon,
  Analytics as DataSimulationIcon,
  Description as DocumentationIcon,
  Search as SearchIcon,
  ArrowForward as ArrowIcon,
  Menu as MenuIcon,
  Close as CloseIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  CheckCircle as CheckCircleIcon,
  Visibility as ViewResultsIcon,
  Refresh as RestartIcon,
  PlayArrow as RegenerateIcon,
  History as HistoryIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import ThemeSwitcher from './ThemeSwitcher';
import DataLayer from './DataLayer';
import CustomerSearch from './CustomerSearch';
import { ApiService } from '../services/api';

interface DashboardTile {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  isExpanded: boolean;
}

interface WorkflowConnection {
  from: string;
  to: string;
  isActive: boolean;
}

interface DashboardProps {
  onLogout: () => void;
  user: any;
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout, user }) => {
  const apiService = new ApiService();
  const [selectedTile, setSelectedTile] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [workflowConnections, setWorkflowConnections] = useState<WorkflowConnection[]>([
    { from: 'data-sources', to: 'data-processing', isActive: true },
    { from: 'data-processing', to: 'data-simulation', isActive: true },
    { from: 'data-simulation', to: 'documentation', isActive: true }
  ]);
  const [verifiedCustomer, setVerifiedCustomer] = useState<any>(null);
  const [lastExecutionResults, setLastExecutionResults] = useState<{ [key: string]: any }>({});
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [dialogTitle, setDialogTitle] = useState('');
  const [dialogContent, setDialogContent] = useState('');
  
  // Session management state
  const [previousSessions, setPreviousSessions] = useState<any[]>([]);
  const [selectedSession, setSelectedSession] = useState<any>(null);
  const [sessionSearchValue, setSessionSearchValue] = useState('');
  const [sessionMenuAnchor, setSessionMenuAnchor] = useState<null | HTMLElement>(null);
  const [sessionMenuOpen, setSessionMenuOpen] = useState(false);
  const [sessionResultsDialogOpen, setSessionResultsDialogOpen] = useState(false);
  const [currentSessionResults, setCurrentSessionResults] = useState<any>(null);
  
  const { theme } = useTheme();

  const tiles: DashboardTile[] = [
    {
      id: 'customer-search',
      title: 'Customer Search',
      description: 'Search and verify customer identity',
      icon: <SearchIcon sx={{ fontSize: 40 }} />,
      color: '#f59e0b',
      isExpanded: selectedTile === 'customer-search'
    },
    {
      id: 'data-sources',
      title: 'Data Sources',
      description: 'Select and configure data sources for analysis',
      icon: <DataSourcesIcon sx={{ fontSize: 40 }} />,
      color: '#6366f1',
      isExpanded: selectedTile === 'data-sources'
    },
    {
      id: 'data-processing',
      title: 'Data Processing',
      description: 'Transform and prepare data for analysis',
      icon: <DataProcessingIcon sx={{ fontSize: 40 }} />,
      color: '#8b5cf6',
      isExpanded: selectedTile === 'data-processing'
    },
    {
      id: 'data-simulation',
      title: 'Data Simulation & Visualization Studio',
      description: 'Run simulations and create visualizations',
      icon: <DataSimulationIcon sx={{ fontSize: 40 }} />,
      color: '#06b6d4',
      isExpanded: selectedTile === 'data-simulation'
    },
    {
      id: 'documentation',
      title: 'Decision Documentation',
      description: 'Document and communicate decisions',
      icon: <DocumentationIcon sx={{ fontSize: 40 }} />,
      color: '#10b981',
      isExpanded: selectedTile === 'documentation'
    }
  ];

  const handleTileClick = (tileId: string) => {
    // Special handling for Decision Documentation when session data is loaded
    if (tileId === 'documentation' && selectedSession && lastExecutionResults['documentation']) {
      // Navigate to the Decision Documentation page
      const sessionId = selectedSession.id || selectedSession.execution_id;
      window.open(`/decision-documentation?sessionId=${sessionId}`, '_blank');
      return;
    }
    
    setSelectedTile(selectedTile === tileId ? null : tileId);
    setSidebarOpen(false);
  };

  const handleSidebarItemClick = (tileId: string) => {
    if (tileId === 'home') {
      setSelectedTile(null);
    } else {
      setSelectedTile(tileId);
    }
    setSidebarOpen(false);
  };

  const handleWorkflowConnectionToggle = (from: string, to: string) => {
    setWorkflowConnections(prev => 
      prev.map(conn => 
        conn.from === from && conn.to === to 
          ? { ...conn, isActive: !conn.isActive }
          : conn
      )
    );
  };

  const handleCustomerVerified = (customer: any) => {
    setVerifiedCustomer(customer);
  };

  const handleViewResults = (moduleId: string) => {
    const execution = lastExecutionResults[moduleId];
    
    // Special handling for Decision Documentation module
    if (moduleId === 'documentation' && selectedSession) {
      // Show decision data in a modal instead of navigating
      setSelectedTile(moduleId);
      setIsDialogOpen(true);
      setDialogTitle(`Decision Documentation - ${selectedSession.customerName}`);
      
      // Format decision data for display
      let formattedContent = '';
      
      if (selectedSession.results && Object.keys(selectedSession.results).length > 0) {
        formattedContent += `📊 Decision Summary\n`;
        formattedContent += `==================\n`;
        formattedContent += `Customer: ${selectedSession.customerName}\n`;
        formattedContent += `Status: ${selectedSession.status}\n`;
        formattedContent += `Started: ${new Date(selectedSession.startedAt).toLocaleString()}\n`;
        if (selectedSession.completedAt) {
          formattedContent += `Completed: ${new Date(selectedSession.completedAt).toLocaleString()}\n`;
        }
        formattedContent += `Progress: ${selectedSession.progress}%\n`;
        formattedContent += `\n`;
        
        // Look for decision data in results
        const decisionData = selectedSession.results.decision || selectedSession.results.step_004;
        if (decisionData) {
          formattedContent += `🎯 Decision Details:\n`;
          formattedContent += `Decision: ${decisionData.decision || 'Pending'}\n`;
          if (decisionData.approved_amount) {
            formattedContent += `Approved Amount: $${decisionData.approved_amount.toLocaleString()}\n`;
          }
          if (decisionData.current_credit_limit) {
            formattedContent += `Current Credit Limit: $${decisionData.current_credit_limit.toLocaleString()}\n`;
          }
          if (decisionData.reason) {
            formattedContent += `Reason: ${decisionData.reason}\n`;
          }
          if (decisionData.decision_date) {
            formattedContent += `Decision Date: ${new Date(decisionData.decision_date).toLocaleString()}\n`;
          }
          formattedContent += `\n`;
        }
        
        // Show all step results
        formattedContent += `📋 Execution Steps:\n`;
        Object.entries(selectedSession.results).forEach(([stepId, result]: [string, any]) => {
          if (stepId !== 'decision' && typeof result === 'object') {
            formattedContent += `\n${stepId}: ${result.step_title || 'Unknown Step'}\n`;
            formattedContent += `Status: ${result.status || 'Unknown'}\n`;
            if (result.execution_time) {
              formattedContent += `Duration: ${result.execution_time}s\n`;
            }
            
            if (result.insights && result.insights.length > 0) {
              formattedContent += `Insights:\n`;
              result.insights.forEach((insight: string) => {
                formattedContent += `• ${insight}\n`;
              });
            }
            
            if (result.recommendations && result.recommendations.length > 0) {
              formattedContent += `Recommendations:\n`;
              result.recommendations.forEach((rec: string) => {
                formattedContent += `• ${rec}\n`;
              });
            }
          }
        });
      } else {
        formattedContent = 'No decision data available for this session.';
      }
      
      setDialogContent(formattedContent);
      return;
    }

    // For other modules, require execution results
    if (!execution) return;

    setSelectedTile(moduleId);
    setIsDialogOpen(true);
    setDialogTitle(`${moduleId.replace('-', ' ').replace('&', ' & ').replace(/\b\w/g, l => l.toUpperCase())} - Last Results`);
    
    // Format the results in a more readable way
    let formattedContent = '';
    
    if (execution.results && execution.results.length > 0) {
      formattedContent += `📊 Execution Summary\n`;
      formattedContent += `==================\n`;
      formattedContent += `Status: ${execution.status}\n`;
      formattedContent += `Started: ${new Date(execution.start_time).toLocaleString()}\n`;
      if (execution.end_time) {
        formattedContent += `Completed: ${new Date(execution.end_time).toLocaleString()}\n`;
      }
      formattedContent += `\n`;
      
      execution.results.forEach((result: any, index: number) => {
        formattedContent += `📋 Step ${index + 1}: ${result.step_title || 'Unknown Step'}\n`;
        formattedContent += `Status: ${result.status}\n`;
        if (result.execution_time) {
          formattedContent += `Duration: ${result.execution_time}ms\n`;
        }
        formattedContent += `\n`;
        
        if (result.insights && result.insights.length > 0) {
          formattedContent += `💡 Insights:\n`;
          result.insights.forEach((insight: string) => {
            formattedContent += `• ${insight}\n`;
          });
          formattedContent += `\n`;
        }
        
        if (result.recommendations && result.recommendations.length > 0) {
          formattedContent += `🎯 Recommendations:\n`;
          result.recommendations.forEach((rec: string) => {
            formattedContent += `• ${rec}\n`;
          });
          formattedContent += `\n`;
        }
      });
    } else {
      formattedContent = 'No results available for this module.';
    }
    
    setDialogContent(formattedContent);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    setDialogTitle('');
    setDialogContent('');
  };

  // Session management functions
  const fetchPreviousSessions = async () => {
    try {
      const apiService = ApiService.getInstance();
      console.log('🔍 Fetching previous sessions...');

      const response = await apiService.getAllInvestigationExecutions();
      console.log('🔍 API Response:', response);
      
      if (response.success && response.executions) {
        // Format sessions for display
        const formattedSessions = response.executions.map((execution: any) => ({
          id: execution.execution_id || execution.executionId,
          customerName: execution.customer_name || execution.customerName,
          customerId: execution.customer_id || execution.customerId,
          status: execution.status,
          startedAt: execution.started_at || execution.startedAt,
          completedAt: execution.completed_at || execution.completedAt,
          steps: execution.selectedSteps || [],
          results: execution.results || [],
          progress: execution.progress || 0
        }));
        console.log('🔍 Formatted sessions:', formattedSessions);
        setPreviousSessions(formattedSessions);
      } else {
        console.log('🔍 No executions found or API error:', response);
        setPreviousSessions([]);
      }
    } catch (error) {
      console.error('Failed to fetch previous sessions:', error);
      setPreviousSessions([]);
    }
  };

  const handleSessionSelect = (session: any) => {
    setSelectedSession(session);
    setSessionSearchValue(`${session.customerName} (${session.status})`);
    setSessionMenuOpen(false);
    
    // Load session data and make it available to workflow modules
    loadSessionData(session);
  };

  const loadSessionData = (session: any) => {
    console.log('📂 Loading session data for:', session);
    
    // Convert session results to the format expected by workflow modules
    const sessionResults: { [key: string]: any } = {};
    
    if (session.results && session.results.length > 0) {
      // Map session results to module types
      session.results.forEach((result: any) => {
        const moduleType = determineModuleType(result);
        if (moduleType) {
          if (!sessionResults[moduleType]) {
            sessionResults[moduleType] = {
              status: session.status,
              start_time: session.startedAt,
              end_time: session.completedAt,
              results: []
            };
          }
          sessionResults[moduleType].results.push(result);
        }
      });
    }
    
    // Handle decision data specifically
    if (session.results && session.results.decision) {
      sessionResults['documentation'] = {
        status: session.status,
        start_time: session.startedAt,
        end_time: session.completedAt,
        results: [{
          step_title: 'Decision Documentation',
          step_id: 'decision_documentation',
          status: 'completed',
          data: session.results.decision,
          insights: [`Decision: ${session.results.decision.decision}`],
          recommendations: [`Approved Amount: $${session.results.decision.approved_amount}`]
        }]
      };
    }
    
    // Update the last execution results with session data
    setLastExecutionResults(sessionResults);
    
    // Set verified customer if available
    if (session.customerName && session.customerId) {
      setVerifiedCustomer({
        name: session.customerName,
        id: session.customerId,
        email: session.customerEmail || `${session.customerName.toLowerCase().replace(' ', '.')}@example.com`
      });
    }
    
    console.log('✅ Session data loaded:', sessionResults);
  };

  const handleViewSessionResults = (session: any) => {
    setCurrentSessionResults(session);
    setSessionResultsDialogOpen(true);
  };

  const handleRestartSession = (session: any) => {
    // Load the session data and navigate to the appropriate module
    setSelectedSession(session);
    // Determine which module to open based on session progress
    if (session.progress < 0.25) {
      setSelectedTile('customer-search');
    } else if (session.progress < 0.5) {
      setSelectedTile('data-sources');
    } else if (session.progress < 0.75) {
      setSelectedTile('data-processing');
    } else if (session.progress < 1) {
      setSelectedTile('data-simulation');
    } else {
      setSelectedTile('documentation');
    }
    setSessionMenuOpen(false);
  };

  const handleRegenerateSession = async (session: any) => {
    try {
      const apiService = ApiService.getInstance();
      // Create a new execution with the same parameters
      const newExecution = await apiService.executeInvestigation({
        customerId: session.customerId,
        customerName: session.customerName,
        selectedSteps: session.steps,
        executionMode: 'batch'
      });
      
      if (newExecution.success) {
        alert('Session regenerated successfully!');
        fetchPreviousSessions(); // Refresh the sessions list
      } else {
        alert('Failed to regenerate session: ' + newExecution.error);
      }
    } catch (error) {
      console.error('Error regenerating session:', error);
      alert('Error regenerating session');
    }
    setSessionMenuOpen(false);
  };

  const formatSessionDisplay = (session: any) => {
    const date = new Date(session.startedAt).toLocaleDateString();
    const time = new Date(session.startedAt).toLocaleTimeString();
            // Progress is already a percentage (0-100), no need to multiply by 100
        const progress = Math.round(session.progress);
    return `${session.customerName} - ${date} ${time} (${progress}% complete)`;
  };

  const getSessionStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return '#10b981';
      case 'running': return '#f59e0b';
      case 'failed': return '#ef4444';
      default: return '#6b7280';
    }
  };

  useEffect(() => {
    fetchPreviousSessions();
    const interval = setInterval(fetchPreviousSessions, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, []);

  // Add a manual refresh function for debugging
  const handleRefreshSessions = () => {
    console.log('🔄 Manually refreshing sessions...');
    fetchPreviousSessions();
  };

  const handleSaveToCosmos = async () => {
    try {
      console.log('💾 Saving sessions to CosmosDB...');
      const response = await apiService.saveSessionsToCosmos();
      if (response.success) {
        console.log('✅ Sessions saved to CosmosDB:', response.message);
        // Refresh the sessions list after saving
        await fetchPreviousSessions();
      } else {
        console.error('❌ Failed to save sessions:', response.error);
      }
    } catch (error) {
      console.error('❌ Error saving sessions to CosmosDB:', error);
    }
  };

  const determineModuleType = (result: any): string | null => {
    // Determine which module this result belongs to based on step title or step ID
    const stepTitle = result.step_title || result.step_id || '';
    const stepId = result.step_id || '';
    
    if (stepTitle.toLowerCase().includes('customer') || stepId.toLowerCase().includes('customer')) {
      return 'customer-search';
    } else if (stepTitle.toLowerCase().includes('data source') || stepId.toLowerCase().includes('data_source')) {
      return 'data-sources';
    } else if (stepTitle.toLowerCase().includes('processing') || stepId.toLowerCase().includes('processing')) {
      return 'data-processing';
    } else if (stepTitle.toLowerCase().includes('simulation') || 
               stepTitle.toLowerCase().includes('visualization') ||
               stepId.toLowerCase().includes('simulation')) {
      return 'data-simulation';
    } else if (stepTitle.toLowerCase().includes('documentation') || 
               stepTitle.toLowerCase().includes('decision') ||
               stepId.toLowerCase().includes('documentation')) {
      return 'documentation';
    }
    
    // Default mapping based on step order or other criteria
    return null;
  };

  const renderTile = (tile: DashboardTile, index: number) => (
    <Box key={tile.id} sx={{ position: 'relative' }}>
      <Paper
        onClick={() => handleTileClick(tile.id)}
        sx={{
          p: 3,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          backgroundColor: verifiedCustomer && tile.id === 'customer-search' 
            ? 'rgba(76, 175, 80, 0.1)' 
            : lastExecutionResults[tile.id]
            ? 'rgba(16, 185, 129, 0.1)'
            : 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          border: `1px solid ${verifiedCustomer && tile.id === 'customer-search' 
            ? 'rgba(76, 175, 80, 0.3)' 
            : lastExecutionResults[tile.id]
            ? 'rgba(16, 185, 129, 0.3)'
            : 'rgba(255, 255, 255, 0.2)'}`,
          borderRadius: 3,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
            backgroundColor: verifiedCustomer && tile.id === 'customer-search'
              ? 'rgba(76, 175, 80, 0.15)'
              : lastExecutionResults[tile.id]
              ? 'rgba(16, 185, 129, 0.15)'
              : 'rgba(255, 255, 255, 0.15)'
          },
          position: 'relative',
          overflow: 'hidden',
          height: verifiedCustomer && tile.id === 'customer-search' ? 250 : 200, // Increased height for customer info
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          width: 400 // Fixed width for consistent layout
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            backgroundColor: tile.color,
            opacity: 0.8
          }}
        />
        
        <Box>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Box
              sx={{
                color: tile.color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              {tile.icon}
            </Box>
            <Box>
              <Typography variant="h5" sx={{ 
                color: theme.colors.text,
                fontWeight: 700,
                mb: 0.5
              }}>
                {tile.title}
              </Typography>
              <Typography variant="body2" sx={{ 
                color: theme.colors.textSecondary,
                maxWidth: 300
              }}>
                {tile.description}
              </Typography>
            </Box>
          </Box>
        </Box>
        
        <Box display="flex" alignItems="center" justifyContent="space-between">
          {verifiedCustomer && tile.id === 'customer-search' ? (
            <Box sx={{ width: '100%' }}>
              <Box sx={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.1)', 
                p: 2, 
                borderRadius: 2,
                mb: 1
              }}>
                <Typography variant="body2" sx={{ 
                  color: theme.colors.textSecondary,
                  fontSize: '0.7rem',
                  mb: 0.5
                }}>
                  Verified Customer
                </Typography>
                <Typography variant="body1" sx={{ 
                  color: theme.colors.text,
                  fontWeight: 600,
                  fontSize: '0.9rem'
                }}>
                  {verifiedCustomer.first_name} {verifiedCustomer.last_name}
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: theme.colors.textSecondary,
                  fontSize: '0.8rem',
                  fontFamily: 'monospace'
                }}>
                  Account: {verifiedCustomer.customer_id}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Typography variant="body2" sx={{ 
                  color: theme.colors.textSecondary,
                  fontSize: '0.7rem'
                }}>
                  Click to view details
                </Typography>
                {lastExecutionResults[tile.id] && (
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewResults(tile.id);
                    }}
                    sx={{
                      color: theme.colors.primary,
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.1)'
                      }
                    }}
                  >
                    <ViewResultsIcon sx={{ fontSize: 16 }} />
                  </IconButton>
                )}
              </Box>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', width: '100%' }}>
              <Typography variant="body2" sx={{ 
                color: theme.colors.textSecondary,
                fontSize: '0.8rem'
              }}>
                {lastExecutionResults[tile.id] ? 
                  (selectedSession ? 'Session Data Available' : 'Completed') : 
                  (tile.id === 'documentation' && selectedSession ? 'Session Data Available' : 'Click to expand')
                }
              </Typography>
              {(lastExecutionResults[tile.id] || (tile.id === 'documentation' && selectedSession)) && (
                <>
                  <CheckCircleIcon sx={{ 
                    fontSize: 16, 
                    color: '#10b981' 
                  }} />
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewResults(tile.id);
                    }}
                    sx={{
                      color: theme.colors.primary,
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.1)'
                      }
                    }}
                  >
                    <ViewResultsIcon sx={{ fontSize: 16 }} />
                  </IconButton>
                </>
              )}
            </Box>
          )}
        </Box>
      </Paper>
      
      {/* L-shaped workflow arrows between tiles */}
      {index < tiles.length - 1 && (() => {
        const connection = workflowConnections.find(
          conn => conn.from === tile.id && conn.to === tiles[index + 1].id
        );
        const isNextTileRight = index % 2 === 0; // Even indices go right, odd go left
        
        return (
          <Box
            onClick={() => handleWorkflowConnectionToggle(tile.id, tiles[index + 1].id)}
            sx={{
              position: 'absolute',
              top: '50%',
              left: isNextTileRight ? '100%' : 'auto',
              right: isNextTileRight ? 'auto' : '100%',
              transform: 'translateY(-50%)',
              zIndex: 10,
              display: { xs: 'none', md: 'flex' },
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-50%) scale(1.05)'
              }
            }}
          >
            {/* L-shaped arrow */}
            <Box sx={{ position: 'relative' }}>
              {/* Horizontal line */}
              <Box
                sx={{
                  width: isNextTileRight ? 120 : 120,
                  height: 3,
                  backgroundColor: connection?.isActive 
                    ? 'rgba(255, 255, 255, 0.6)' 
                    : 'rgba(255, 255, 255, 0.2)',
                  borderRadius: 2,
                  transition: 'all 0.3s ease'
                }}
              />
              
              {/* Vertical line with integrated arrowhead */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: isNextTileRight ? '100%' : 'auto',
                  right: isNextTileRight ? 'auto' : '100%',
                  width: 3,
                  height: 92, // Extended to include arrowhead
                  backgroundColor: connection?.isActive 
                    ? 'rgba(255, 255, 255, 0.6)' 
                    : 'rgba(255, 255, 255, 0.2)',
                  borderRadius: 2,
                  transition: 'all 0.3s ease',
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    bottom: -12,
                    left: -6.5, // Center the arrowhead on the 3px line
                    width: 0,
                    height: 0,
                    borderLeft: '8px solid transparent',
                    borderRight: '8px solid transparent',
                    borderTop: '12px solid',
                    borderTopColor: connection?.isActive 
                      ? 'rgba(255, 255, 255, 0.6)' 
                      : 'rgba(255, 255, 255, 0.2)',
                    transition: 'all 0.3s ease'
                  }
                }}
              />
            </Box>
            
            {/* Connection status indicator */}
            <Box
              sx={{
                position: 'absolute',
                top: -8,
                left: isNextTileRight ? 60 : 'auto',
                right: isNextTileRight ? 'auto' : 60,
                width: 16,
                height: 16,
                borderRadius: '50%',
                backgroundColor: connection?.isActive 
                  ? 'rgba(76, 175, 80, 0.8)' 
                  : 'rgba(244, 67, 54, 0.8)',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: 'white',
                  fontSize: '0.6rem',
                  fontWeight: 'bold'
                }}
              >
                {connection?.isActive ? '✓' : '✗'}
              </Typography>
            </Box>
          </Box>
        );
      })()}
    </Box>
  );

  const renderExpandedContent = () => {
    switch (selectedTile) {
      case 'customer-search':
        return <CustomerSearch 
          onCustomerVerified={handleCustomerVerified} 
          onNavigateToDataSources={() => setSelectedTile('data-sources')}
        />;
      case 'data-sources':
        return <DataLayer selectedCustomer={verifiedCustomer} />;
      case 'data-processing':
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ color: theme.colors.text, mb: 2 }}>
              Data Processing
            </Typography>
            <Typography variant="body1" sx={{ color: theme.colors.textSecondary }}>
              Data processing functionality coming soon...
            </Typography>
          </Box>
        );
      case 'data-simulation':
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ color: theme.colors.text, mb: 2 }}>
              Data Simulation & Visualization Studio
            </Typography>
            <Typography variant="body1" sx={{ color: theme.colors.textSecondary }}>
              Simulation and visualization functionality coming soon...
            </Typography>
          </Box>
        );
      case 'documentation':
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ color: theme.colors.text, mb: 2 }}>
              Decision Documentation
            </Typography>
            <Typography variant="body1" sx={{ color: theme.colors.textSecondary }}>
              Documentation functionality coming soon...
            </Typography>
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Sidebar */}
      <Drawer
        variant="temporary"
        anchor="left"
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        PaperProps={{
          sx: {
            width: 280,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            border: 'none'
          }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6" sx={{ color: theme.colors.text, fontWeight: 600 }}>
              Navigation
            </Typography>
            <IconButton onClick={() => setSidebarOpen(false)}>
              <CloseIcon sx={{ color: theme.colors.text }} />
            </IconButton>
          </Box>
          
          <Box>
            {/* Home/Dashboard Option */}
            <Box
              onClick={() => handleSidebarItemClick('home')}
              sx={{
                display: 'flex',
                alignItems: 'center',
                p: 2,
                borderRadius: 2,
                mb: 1,
                backgroundColor: selectedTile === null ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              <Box sx={{ color: '#6366f1', mr: 2, fontSize: 24 }}>
                🏠
              </Box>
              <Typography
                sx={{ 
                  color: theme.colors.text,
                  fontWeight: selectedTile === null ? 600 : 400
                }}
              >
                Home
              </Typography>
            </Box>
            
            {/* Divider */}
            <Box sx={{ 
              height: 1, 
              backgroundColor: 'rgba(255, 255, 255, 0.1)', 
              my: 2 
            }} />
            
            {tiles.map((tile) => (
              <Box
                key={tile.id}
                onClick={() => handleSidebarItemClick(tile.id)}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  p: 2,
                  borderRadius: 2,
                  mb: 1,
                  backgroundColor: selectedTile === tile.id ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)'
                  }
                }}
              >
                <Box sx={{ color: tile.color, mr: 2 }}>
                  {tile.icon}
                </Box>
                <Typography
                  sx={{ 
                    color: theme.colors.text,
                    fontWeight: selectedTile === tile.id ? 600 : 400
                  }}
                >
                  {tile.title}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      </Drawer>

      {/* Header */}
      <Box sx={{ 
        p: 3, 
        borderBottom: `1px solid ${theme.colors.border}`,
        backgroundColor: theme.colors.surface,
        position: 'sticky',
        top: 0,
        zIndex: 1000
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box display="flex" alignItems="center" gap={2}>
            <IconButton
              onClick={() => setSidebarOpen(true)}
              sx={{ 
                color: theme.colors.text,
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)'
                }
              }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h5" sx={{ 
              color: theme.colors.text,
              fontWeight: 700
            }}>
              Banking Agent
            </Typography>
          </Box>
          
          <Box display="flex" alignItems="center" gap={2}>
            {/* Session Search */}
            <Box display="flex" alignItems="center" gap={1}>
              <HistoryIcon sx={{ color: theme.colors.textSecondary, fontSize: 16 }} />
              <Autocomplete
                value={selectedSession}
                onChange={(_, newValue) => {
                  if (newValue) {
                    handleSessionSelect(newValue);
                  }
                }}
                inputValue={sessionSearchValue}
                onInputChange={(_, newInputValue) => {
                  setSessionSearchValue(newInputValue);
                }}
                options={previousSessions}
                getOptionLabel={(option) => formatSessionDisplay(option)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    placeholder="Search sessions..."
                    variant="outlined"
                    size="small"
                    sx={{
                      width: '200px',
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        color: theme.colors.text,
                        fontSize: '0.8rem',
                        '&:hover': {
                          borderColor: 'rgba(255, 255, 255, 0.3)'
                        },
                        '&.Mui-focused': {
                          borderColor: theme.colors.primary
                        }
                      },
                      '& .MuiInputLabel-root': {
                        color: theme.colors.textSecondary,
                        fontSize: '0.8rem'
                      },
                      '& .MuiInputBase-input': {
                        color: theme.colors.text,
                        fontSize: '0.8rem',
                        padding: '8px 12px'
                      }
                    }}
                  />
                )}
                renderOption={(props, option) => (
                  <Box component="li" {...props} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        backgroundColor: getSessionStatusColor(option.status)
                      }}
                    />
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ color: theme.colors.text, fontWeight: 600 }}>
                        {option.customerName}
                      </Typography>
                      <Typography variant="caption" sx={{ color: theme.colors.textSecondary }}>
                        {new Date(option.startedAt).toLocaleDateString()} - {Math.round(option.progress)}% complete
                      </Typography>
                    </Box>
                  </Box>
                )}
                noOptionsText="No previous sessions found"
              />
              
              {/* Session Action Buttons */}
                          <IconButton
              onClick={handleRefreshSessions}
              size="small"
              sx={{
                color: theme.colors.textSecondary,
                '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' }
              }}
              title="Refresh Sessions"
            >
              <RestartIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton
              onClick={handleSaveToCosmos}
              size="small"
              sx={{
                color: theme.colors.textSecondary,
                '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' }
              }}
              title="Save Sessions to Database"
            >
              <SaveIcon sx={{ fontSize: 18 }} />
            </IconButton>
              
              {selectedSession && (
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  <IconButton
                    onClick={() => handleViewSessionResults(selectedSession)}
                    size="small"
                    sx={{
                      color: theme.colors.primary,
                      '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' }
                    }}
                    title="View Results"
                  >
                    <ViewResultsIcon sx={{ fontSize: 18 }} />
                  </IconButton>
                  <IconButton
                    onClick={() => handleRestartSession(selectedSession)}
                    size="small"
                    sx={{
                      color: '#f59e0b',
                      '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' }
                    }}
                    title="Restart Session"
                  >
                    <RestartIcon sx={{ fontSize: 18 }} />
                  </IconButton>
                  <IconButton
                    onClick={() => handleRegenerateSession(selectedSession)}
                    size="small"
                    sx={{
                      color: '#10b981',
                      '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' }
                    }}
                    title="Regenerate Session"
                  >
                    <RegenerateIcon sx={{ fontSize: 18 }} />
                  </IconButton>
                </Box>
              )}
            </Box>

            {/* User Info */}
            <Box display="flex" alignItems="center" gap={1}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: '#6366f1' }}>
                <PersonIcon />
              </Avatar>
              <Box>
                <Typography variant="body2" sx={{ 
                  color: theme.colors.text,
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  {user?.first_name} {user?.last_name}
                </Typography>
                <Chip 
                  label={user?.role || 'User'} 
                  size="small" 
                  sx={{ 
                    height: 20, 
                    fontSize: '0.7rem',
                    backgroundColor: user?.role === 'admin' ? '#ef4444' : 
                                   user?.role === 'manager' ? '#f59e0b' : '#10b981'
                  }} 
                />
              </Box>
            </Box>
            
            <ThemeSwitcher />
            
            <Button
              onClick={onLogout}
              startIcon={<LogoutIcon />}
              variant="outlined"
              size="small"
              sx={{
                color: theme.colors.text,
                borderColor: 'rgba(255, 255, 255, 0.3)',
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              Logout
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Content Area */}
        <Box sx={{ flex: 1, p: 3 }}>
          {selectedTile ? (
            // Expanded view
            <Slide direction="up" in={true} mountOnEnter unmountOnExit>
              <Box>
                <IconButton
                  onClick={() => setSelectedTile(null)}
                  sx={{ 
                    mb: 2,
                    color: theme.colors.textSecondary,
                    '&:hover': { color: theme.colors.text }
                  }}
                >
                  <ArrowIcon sx={{ transform: 'rotate(180deg)' }} />
                  Back to Dashboard
                </IconButton>
                {renderExpandedContent()}
              </Box>
            </Slide>
          ) : (
            // Dashboard tiles view
            <Fade in={true}>
              <Box>
                <Typography variant="h3" sx={{ 
                  color: theme.colors.text,
                  fontWeight: 700,
                  mb: 1,
                  textAlign: 'center'
                }}>
                  Welcome to Credit Increase Agent
                </Typography>
                <Typography variant="h6" sx={{ 
                  color: theme.colors.textSecondary,
                  mb: 4,
                  textAlign: 'center'
                }}>
                  Select a module to get started
                </Typography>
                
                <Box sx={{ 
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 6,
                  alignItems: 'center'
                }}>
                  {tiles.map((tile, index) => (
                    <Box key={tile.id} sx={{ 
                      position: 'relative',
                      transform: index % 2 === 1 ? 'translateX(200px)' : 'translateX(0)',
                      transition: 'transform 0.3s ease'
                    }}>
                      {renderTile(tile, index)}
                    </Box>
                  ))}
                </Box>
              </Box>
            </Fade>
          )}
        </Box>
      </Box>

      {/* Results Dialog */}
      <Dialog
        open={isDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: theme.colors.background,
            backdropFilter: 'blur(10px)',
            border: `1px solid ${theme.colors.border}`,
            borderRadius: 3,
            boxShadow: '0 16px 48px rgba(0, 0, 0, 0.3)'
          }
        }}
      >
        <DialogTitle sx={{ 
          color: theme.colors.text,
          fontWeight: 700,
          textAlign: 'center',
          borderBottom: `1px solid ${theme.colors.border}`,
          backgroundColor: theme.colors.background
        }}>
          {dialogTitle}
        </DialogTitle>
        <DialogContent sx={{ 
          color: theme.colors.text,
          fontSize: '0.9rem',
          p: 3,
          maxHeight: '70vh',
          overflowY: 'auto',
          backgroundColor: theme.colors.background
        }}>
          <pre style={{ 
            whiteSpace: 'pre-wrap', 
            wordBreak: 'break-all',
            color: theme.colors.text,
            fontFamily: 'monospace',
            fontSize: '0.85rem',
            lineHeight: 1.5
          }}>{dialogContent}</pre>
        </DialogContent>
        <DialogActions sx={{ 
          borderTop: `1px solid ${theme.colors.border}`,
          p: 2,
          justifyContent: 'center',
          backgroundColor: theme.colors.background
        }}>
          <Button
            onClick={handleCloseDialog}
            variant="outlined"
            sx={{
              color: theme.colors.text,
              borderColor: theme.colors.border,
              '&:hover': {
                borderColor: theme.colors.primary,
                backgroundColor: theme.colors.primary + '20'
              }
            }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Session Results Dialog */}
      <Dialog
        open={sessionResultsDialogOpen}
        onClose={() => setSessionResultsDialogOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: theme.colors.background,
            backdropFilter: 'blur(10px)',
            border: `1px solid ${theme.colors.border}`,
            borderRadius: 3,
            boxShadow: '0 16px 48px rgba(0, 0, 0, 0.3)'
          }
        }}
      >
        <DialogTitle sx={{ 
          color: theme.colors.text,
          fontWeight: 700,
          borderBottom: `1px solid ${theme.colors.border}`,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          backgroundColor: theme.colors.background
        }}>
          <HistoryIcon />
          Session Results: {currentSessionResults?.customerName}
        </DialogTitle>
        <DialogContent sx={{ 
          color: theme.colors.text,
          p: 3,
          maxHeight: '80vh',
          overflowY: 'auto',
          backgroundColor: theme.colors.background
        }}>
          {currentSessionResults && (
            <Box>
              {/* Session Summary */}
              <Box sx={{ 
                backgroundColor: theme.colors.background,
                border: `1px solid ${theme.colors.border}`,
                p: 3, 
                borderRadius: 2, 
                mb: 3 
              }}>
                <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                  📊 Session Summary
                </Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                      Customer
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text, fontWeight: 600 }}>
                      {currentSessionResults.customerName}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                      Status
                    </Typography>
                    <Chip 
                      label={currentSessionResults.status} 
                      size="small"
                      sx={{ 
                        backgroundColor: getSessionStatusColor(currentSessionResults.status),
                        color: 'white',
                        fontWeight: 600
                      }}
                    />
                  </Box>
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                      Progress
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text, fontWeight: 600 }}>
                                              {Math.round(currentSessionResults.progress)}%
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                      Started
                    </Typography>
                    <Typography variant="body1" sx={{ color: theme.colors.text }}>
                      {new Date(currentSessionResults.startedAt).toLocaleString()}
                    </Typography>
                  </Box>
                  {currentSessionResults.completedAt && (
                    <Box>
                      <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
                        Completed
                      </Typography>
                      <Typography variant="body1" sx={{ color: theme.colors.text }}>
                        {new Date(currentSessionResults.completedAt).toLocaleString()}
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Box>

              {/* Results */}
              {currentSessionResults.results && currentSessionResults.results.length > 0 ? (
                <Box>
                  <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                    📋 Investigation Results
                  </Typography>
                  {currentSessionResults.results.map((result: any, index: number) => (
                    <Box key={index} sx={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.03)', 
                      p: 2, 
                      borderRadius: 2, 
                      mb: 2 
                    }}>
                      <Typography variant="subtitle1" sx={{ color: theme.colors.text, fontWeight: 600, mb: 1 }}>
                        {index + 1}. {result.step_title || 'Unknown Step'}
                      </Typography>
                      
                      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 1, mb: 2 }}>
                        <Box>
                          <Typography variant="caption" sx={{ color: theme.colors.textSecondary }}>
                            Status
                          </Typography>
                          <Typography variant="body2" sx={{ color: theme.colors.text }}>
                            {result.status}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" sx={{ color: theme.colors.textSecondary }}>
                            Duration
                          </Typography>
                          <Typography variant="body2" sx={{ color: theme.colors.text }}>
                            {result.execution_time?.toFixed(2) || 'N/A'} seconds
                          </Typography>
                        </Box>
                      </Box>

                      {result.insights && result.insights.length > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 1 }}>
                            Key Insights:
                          </Typography>
                          <Box component="ul" sx={{ pl: 2, m: 0 }}>
                            {result.insights.map((insight: string, i: number) => (
                              <Typography key={i} component="li" variant="body2" sx={{ color: theme.colors.text }}>
                                {insight}
                              </Typography>
                            ))}
                          </Box>
                        </Box>
                      )}

                      {result.recommendations && result.recommendations.length > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 1 }}>
                            Recommendations:
                          </Typography>
                          <Box component="ul" sx={{ pl: 2, m: 0 }}>
                            {result.recommendations.map((rec: string, i: number) => (
                              <Typography key={i} component="li" variant="body2" sx={{ color: theme.colors.text }}>
                                {rec}
                              </Typography>
                            ))}
                          </Box>
                        </Box>
                      )}

                      {result.data && Object.keys(result.data).length > 0 && (
                        <Box>
                          <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 1 }}>
                            Data Summary:
                          </Typography>
                          <Box sx={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.1)', 
                            p: 2, 
                            borderRadius: 1,
                            fontFamily: 'monospace',
                            fontSize: '0.8rem',
                            border: '1px solid rgba(255, 255, 255, 0.2)'
                          }}>
                            <pre style={{ 
                              margin: 0, 
                              whiteSpace: 'pre-wrap',
                              color: theme.colors.text,
                              lineHeight: 1.4
                            }}>
                              {JSON.stringify(result.data, null, 2)}
                            </pre>
                          </Box>
                        </Box>
                      )}
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography variant="body1" sx={{ color: theme.colors.textSecondary, textAlign: 'center', py: 4 }}>
                  No detailed results available for this session.
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ 
          borderTop: '1px solid rgba(255, 255, 255, 0.2)',
          p: 2,
          justifyContent: 'space-between'
        }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              onClick={() => currentSessionResults && handleRestartSession(currentSessionResults)}
              variant="outlined"
              startIcon={<RestartIcon />}
              sx={{
                color: '#f59e0b',
                borderColor: '#f59e0b',
                '&:hover': {
                  borderColor: '#d97706',
                  backgroundColor: 'rgba(245, 158, 11, 0.1)'
                }
              }}
            >
              Restart Session
            </Button>
            <Button
              onClick={() => currentSessionResults && handleRegenerateSession(currentSessionResults)}
              variant="outlined"
              startIcon={<RegenerateIcon />}
              sx={{
                color: '#10b981',
                borderColor: '#10b981',
                '&:hover': {
                  borderColor: '#059669',
                  backgroundColor: 'rgba(16, 185, 129, 0.1)'
                }
              }}
            >
              Regenerate Session
            </Button>
          </Box>
          <Button
            onClick={() => setSessionResultsDialogOpen(false)}
            variant="outlined"
            sx={{
              color: theme.colors.text,
              borderColor: 'rgba(255, 255, 255, 0.3)',
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.5)',
                backgroundColor: 'rgba(255, 255, 255, 0.05)'
              }
            }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard;
