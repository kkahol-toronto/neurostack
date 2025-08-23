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
  CardContent
} from '@mui/material';
import {
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  TableChart as TableIcon,
  Description as SummaryIcon
} from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import apiService from '../services/api';

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
  const { theme } = useTheme();

  useEffect(() => {
    const fetchCustomerData = async () => {
      try {
        setIsLoading(true);
        setError('');
        
        const result = await apiService.getCustomerData(customerId, true);
        
        if (result.success) {
          setCustomerData(result.data);
          setSummary(result.summary || 'No summary available');
        } else {
          setError(result.error || 'Failed to fetch customer data');
        }
      } catch (err) {
        setError('Network error. Please check your connection.');
        console.error('Error fetching customer data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (customerId) {
      fetchCustomerData();
    }
  }, [customerId]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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
    if (!summary) {
      return (
        <Alert severity="info" sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
          No summary available for this customer.
        </Alert>
      );
    }

    return (
      <Card sx={{ 
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: `1px solid rgba(255, 255, 255, 0.1)`
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: theme.colors.text, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <AssessmentIcon sx={{ color: theme.colors.primary }} />
            AI-Generated Summary
          </Typography>
          <Typography 
            variant="body1" 
            sx={{ 
              color: theme.colors.textSecondary,
              lineHeight: 1.6,
              whiteSpace: 'pre-line'
            }}
          >
            {summary}
          </Typography>
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
    </Box>
  );
};

export default CustomerDataView;
