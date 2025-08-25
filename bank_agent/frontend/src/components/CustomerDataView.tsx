import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent,
  Button
} from '@mui/material';
import {
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  TableChart as TableIcon,
  Description as SummaryIcon,
  Save as SaveIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import apiService from '../services/api';
import ReactMarkdown from 'react-markdown';
import ReportManager from './ReportManager';

interface CustomerDataViewProps {
  customerId: number;
  customerName?: string;
  onClose?: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`customer-data-tabpanel-${index}`}
      aria-labelledby={`customer-data-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const CustomerDataView: React.FC<CustomerDataViewProps> = ({ 
  customerId, 
  customerName = `Customer ${customerId}`,
  onClose 
}) => {
  const [tabValue, setTabValue] = useState(0);
  const [customerData, setCustomerData] = useState<any>(null);
  const [summary, setSummary] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [savedReportId, setSavedReportId] = useState<string>('');
  const { theme } = useTheme();

  useEffect(() => {
    const fetchCustomerData = async () => {
      try {
        console.log('🔍 Starting to fetch customer data for ID:', customerId);
        setIsLoading(true);
        setError('');
        
        console.log('🔍 Calling apiService.getCustomerData...');
        const result = await apiService.getCustomerData(customerId, true);
        console.log('🔍 API response:', result);
        
        if (result.success) {
          console.log('✅ Customer data fetched successfully');
          setCustomerData(result.data);
          setSummary(result.summary || 'No summary available');
        } else {
          console.error('❌ API returned error:', result.error);
          
          // Handle specific error messages
          let errorMessage = result.error || 'Failed to fetch customer data';
          
          if (errorMessage.includes('500') || errorMessage.includes('Internal server error')) {
            errorMessage = 'AI Summary generation is in progress. Please wait a moment and try again.';
          } else if (errorMessage.includes('APIM')) {
            errorMessage = 'AI service is temporarily unavailable. Please try again in a few moments.';
          }
          
          setError(errorMessage);
        }
      } catch (err) {
        console.error('❌ Exception during customer data fetch:', err);
        setError('Network error. Please check your connection.');
        console.error('Error fetching customer data:', err);
      } finally {
        console.log('🔍 Setting loading to false');
        setIsLoading(false);
      }
    };

    if (customerId) {
      console.log('🔍 Customer ID provided, starting fetch...');
      fetchCustomerData();
    } else {
      console.log('❌ No customer ID provided');
    }
  }, [customerId]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleRetrySummary = async () => {
    if (!customerId) return;
    
    console.log('🔄 Retrying AI summary generation...');
    try {
      setIsLoading(true);
      setError('');
      
      const result = await apiService.getCustomerData(customerId, true);
      
      if (result.success) {
        setCustomerData(result.data);
        setSummary(result.summary || 'No summary available');
      } else {
        let errorMessage = result.error || 'Failed to fetch customer data';
        
        if (errorMessage.includes('500') || errorMessage.includes('Internal server error')) {
          errorMessage = 'AI Summary generation is in progress. Please wait a moment and try again.';
        } else if (errorMessage.includes('APIM')) {
          errorMessage = 'AI service is temporarily unavailable. Please try again in a few moments.';
        }
        
        setError(errorMessage);
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderDataTable = () => {
    if (!customerData) return null;

    const allData: Array<{ source: string; field: string; value: any }> = [];
    
    Object.entries(customerData).forEach(([sourceId, sourceInfo]: [string, any]) => {
      const sourceName = sourceInfo.source_name;
      const data = sourceInfo.data;
      
      Object.entries(data).forEach(([field, value]) => {
        allData.push({
          source: sourceName,
          field: field,
          value: value
        });
      });
    });

    return (
      <TableContainer component={Paper} sx={{ 
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: `1px solid rgba(255, 255, 255, 0.1)`
      }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: theme.colors.text, fontWeight: 600 }}>Data Source</TableCell>
              <TableCell sx={{ color: theme.colors.text, fontWeight: 600 }}>Field</TableCell>
              <TableCell sx={{ color: theme.colors.text, fontWeight: 600 }}>Value</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {allData.map((row, index) => (
              <TableRow key={index} sx={{ '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.05)' } }}>
                <TableCell sx={{ color: theme.colors.text }}>
                  <Chip 
                    label={row.source} 
                    size="small" 
                    sx={{ 
                      backgroundColor: theme.colors.primary,
                      color: 'white',
                      fontSize: '0.7rem'
                    }} 
                  />
                </TableCell>
                <TableCell sx={{ color: theme.colors.text, fontWeight: 500 }}>
                  {row.field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </TableCell>
                <TableCell sx={{ color: theme.colors.textSecondary }}>
                  {typeof row.value === 'boolean' 
                    ? (row.value ? 'Yes' : 'No')
                    : typeof row.value === 'number' && row.value > 1000
                    ? row.value.toLocaleString()
                    : String(row.value)
                  }
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderSummary = () => {
    if (isLoading) {
      return (
        <Card sx={{ 
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: `1px solid rgba(255, 255, 255, 0.1)`
        }}>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <CircularProgress sx={{ color: theme.colors.primary, mb: 2 }} />
            <Typography variant="body1" sx={{ color: theme.colors.textSecondary, mb: 1 }}>
              Generating AI Summary...
            </Typography>
            <Typography variant="caption" sx={{ color: theme.colors.textSecondary, opacity: 0.7 }}>
              This may take a few moments while we analyze the customer data
            </Typography>
          </CardContent>
        </Card>
      );
    }

    if (!summary) {
      return (
        <Card sx={{ 
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: `1px solid rgba(255, 255, 255, 0.1)`
        }}>
          <CardContent sx={{ textAlign: 'center', py: 3 }}>
            <InfoIcon sx={{ color: theme.colors.textSecondary, fontSize: 40, mb: 2 }} />
            <Typography variant="body1" sx={{ color: theme.colors.textSecondary, mb: 2 }}>
              No AI Summary Available
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.textSecondary, opacity: 0.7, mb: 2 }}>
              The AI summary could not be generated. This might be due to insufficient data or a temporary service issue.
            </Typography>
            <Button
              variant="outlined"
              onClick={handleRetrySummary}
              sx={{
                borderColor: theme.colors.primary,
                color: theme.colors.primary,
                '&:hover': {
                  borderColor: theme.colors.primaryDark,
                  backgroundColor: 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              Retry Summary Generation
            </Button>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card sx={{ 
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: `1px solid rgba(255, 255, 255, 0.1)`
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ color: theme.colors.text, display: 'flex', alignItems: 'center', gap: 1 }}>
              <AssessmentIcon sx={{ color: theme.colors.primary }} />
              AI-Generated Summary
            </Typography>
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              onClick={() => setTabValue(3)}
              sx={{
                borderColor: theme.colors.primary,
                color: theme.colors.primary,
                '&:hover': {
                  borderColor: theme.colors.primaryDark,
                  backgroundColor: 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              Save Report
            </Button>
          </Box>
          <Box sx={{ 
            color: theme.colors.textSecondary,
            lineHeight: 1.6,
            '& h2': {
              color: theme.colors.text,
              fontSize: '1.5rem',
              fontWeight: 600,
              marginTop: 2,
              marginBottom: 1,
              borderBottom: `2px solid ${theme.colors.primary}`,
              paddingBottom: 0.5,
              display: 'flex',
              alignItems: 'center',
              gap: 1
            },
            '& h3': {
              color: theme.colors.primary,
              fontSize: '1.2rem',
              fontWeight: 500,
              marginTop: 1.5,
              marginBottom: 0.5
            },
            '& strong': {
              color: theme.colors.text,
              fontWeight: 600
            },
            '& ul': {
              marginLeft: 2,
              marginTop: 0.5,
              marginBottom: 0.5
            },
            '& li': {
              marginBottom: 0.5,
              paddingLeft: 0.5
            },
            '& hr': {
              borderColor: theme.colors.primary,
              marginTop: 1.5,
              marginBottom: 1.5,
              opacity: 0.6
            },
            '& p': {
              marginBottom: 0.5
            }
          }}>
            <ReactMarkdown>{summary}</ReactMarkdown>
          </Box>
        </CardContent>
      </Card>
    );
  };

  const renderSourceBreakdown = () => {
    if (!customerData) return null;

    return (
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2 }}>
        {Object.entries(customerData).map(([sourceId, sourceInfo]: [string, any]) => (
          <Card key={sourceId} sx={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: `1px solid rgba(255, 255, 255, 0.1)`
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2 }}>
                {sourceInfo.source_name}
              </Typography>
              <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mb: 2 }}>
                {sourceInfo.source_description}
              </Typography>
              <Chip 
                label={sourceInfo.category} 
                size="small" 
                sx={{ 
                  backgroundColor: theme.colors.primary,
                  color: 'white'
                }} 
              />
              <Typography variant="body2" sx={{ color: theme.colors.textSecondary, mt: 1 }}>
                {Object.keys(sourceInfo.data).length} data points available
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  };

  if (isLoading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px',
        flexDirection: 'column',
        gap: 2
      }}>
        <CircularProgress sx={{ color: theme.colors.primary }} />
        <Typography variant="h6" sx={{ color: theme.colors.text }}>
          Loading customer data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 2, 
        mb: 3,
        p: 2,
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 2,
        border: `1px solid rgba(255, 255, 255, 0.1)`
      }}>
        <PersonIcon sx={{ fontSize: 32, color: theme.colors.primary }} />
        <Box>
          <Typography variant="h4" sx={{ color: theme.colors.text, fontWeight: 600 }}>
            {customerName}
          </Typography>
          <Typography variant="body2" sx={{ color: theme.colors.textSecondary }}>
            Customer ID: {customerId} • {Object.keys(customerData || {}).length} data sources
          </Typography>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'rgba(255, 255, 255, 0.2)' }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          sx={{
            '& .MuiTab-root': {
              color: theme.colors.textSecondary,
              '&.Mui-selected': {
                color: theme.colors.primary
              }
            },
            '& .MuiTabs-indicator': {
              backgroundColor: theme.colors.primary
            }
          }}
        >
          <Tab 
            icon={<TableIcon />} 
            label="Data Table" 
            iconPosition="start"
          />
          <Tab 
            icon={<SummaryIcon />} 
            label="AI Summary" 
            iconPosition="start"
          />
          <Tab 
            icon={<AssessmentIcon />} 
            label="Source Breakdown" 
            iconPosition="start"
          />
          <Tab 
            icon={<PersonIcon />} 
            label="Reports" 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        {renderDataTable()}
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        {renderSummary()}
      </TabPanel>
      
              <TabPanel value={tabValue} index={2}>
          {renderSourceBreakdown()}
        </TabPanel>
        <TabPanel value={tabValue} index={3}>
          {customerData && summary && (
            <ReportManager
              customerId={customerId}
              customerName={customerName}
              customerData={customerData}
              aiSummary={summary}
              onReportSaved={(reportId: string) => setSavedReportId(reportId)}
            />
          )}
        </TabPanel>
      </Box>
    );
  };

export default CustomerDataView;
