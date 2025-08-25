import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Button,
  Alert,
  Collapse
} from '@mui/material';
import {
  Storage as StorageIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
  QueryStats as QueryIcon
} from '@mui/icons-material';
import { DataSource as DataSourceType } from '../types';
import { useTheme } from '../contexts/ThemeContext';
import DataSource from './DataSource';
import MultiTableQuery from './MultiTableQuery';
import CustomerDataView from './CustomerDataView';
import apiService from '../services/api';

interface DataLayerProps {
  selectedCustomer?: { 
    customer_id: number; 
    first_name: string; 
    last_name: string;
    [key: string]: any;
  } | null;
}

const DataLayer: React.FC<DataLayerProps> = ({ selectedCustomer }) => {
  const [dataSources, setDataSources] = useState<DataSourceType[]>([]);
  const [showInfo, setShowInfo] = useState(false);
  const [showMultiTableQuery, setShowMultiTableQuery] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const { theme } = useTheme();

  useEffect(() => {
    const fetchDataSources = async () => {
      try {
        const sources = await apiService.getDataSources();
        console.log('Fetched data sources:', sources);
        
        // Ensure sources is an array
        if (Array.isArray(sources)) {
          setDataSources(sources);
        } else {
          console.error('Data sources is not an array:', sources);
          setDataSources([]);
        }
      } catch (error) {
        console.error('Error fetching data sources:', error);
        setDataSources([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDataSources();
  }, []);

  const handleToggleDataSource = (id: string) => {
    const updatedSources = dataSources.map(source => 
      source.id === id ? { ...source, is_enabled: !source.is_enabled } : source
    );
    setDataSources(updatedSources);
  };

  const getEnabledCount = () => {
    if (!Array.isArray(dataSources)) {
      console.warn('dataSources is not an array:', dataSources);
      return 0;
    }
    return dataSources.filter(ds => ds.is_enabled).length;
  };

  const getCategoryCount = (category: string) => {
    if (!Array.isArray(dataSources)) {
      console.warn('dataSources is not an array:', dataSources);
      return 0;
    }
    return dataSources.filter(ds => ds.category === category).length;
  };

  const getEnabledCategoryCount = (category: string) => {
    if (!Array.isArray(dataSources)) {
      console.warn('dataSources is not an array:', dataSources);
      return 0;
    }
    return dataSources.filter(ds => ds.category === category && ds.is_enabled).length;
  };

  if (isLoading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
        <Typography variant="h6" sx={{ color: theme.colors.text }}>
          Loading data sources...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Main Data Layer Tile with Translucent Background */}
      <Paper sx={{ 
        p: 4, 
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        border: `1px solid rgba(255, 255, 255, 0.2)`,
        borderRadius: 3,
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
      }}>
        {/* Header Section */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={4}>
          <Box display="flex" alignItems="center" gap={3}>
            <StorageIcon sx={{ fontSize: 40, color: theme.colors.primary }} />
            <Box>
              <Typography variant="h3" component="h1" gutterBottom sx={{ 
                color: theme.colors.text,
                fontWeight: 700,
                textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
              }}>
                Data Layer
              </Typography>
              <Typography variant="h6" sx={{ 
                color: theme.colors.textSecondary,
                fontWeight: 500
              }}>
                Select data sources for credit limit decisions
              </Typography>
            </Box>
          </Box>
          <Box display="flex" alignItems="center" gap={2}>
            <Chip
              label={`${getEnabledCount()}/${dataSources.length} sources selected`}
              color="primary"
              variant="filled"
              sx={{
                backgroundColor: theme.colors.primary,
                color: 'white',
                fontSize: '1rem',
                fontWeight: 600,
                height: 40,
                px: 2
              }}
            />
            <Button
              startIcon={<QueryIcon />}
              onClick={() => setShowMultiTableQuery(true)}
              variant="contained"
              size="large"
              sx={{
                backgroundColor: theme.colors.primary,
                px: 3,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                '&:hover': {
                  backgroundColor: theme.colors.primaryDark,
                  transform: 'translateY(-2px)',
                  boxShadow: '0 6px 20px rgba(0, 0, 0, 0.2)'
                }
              }}
            >
              Intelligent Query
            </Button>
            <Button
              startIcon={<InfoIcon />}
              onClick={() => setShowInfo(!showInfo)}
              variant="outlined"
              size="large"
              sx={{
                borderColor: 'rgba(255, 255, 255, 0.3)',
                color: theme.colors.text,
                px: 3,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                '&:hover': {
                  borderColor: theme.colors.primary,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  transform: 'translateY(-2px)'
                }
              }}
            >
              Info
            </Button>
          </Box>
        </Box>

        <Collapse in={showInfo}>
          <Alert severity="info" sx={{ 
            mb: 4, 
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            borderRadius: 2
          }}>
            <Typography variant="body2" sx={{ color: theme.colors.text }}>
              <strong>How to use:</strong>
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.text }}>
              • <strong>Click</strong> on a data source card to toggle it on/off for credit decisions
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.text }}>
              • <strong>Hover</strong> over cards to see interaction hints
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.text }}>
              • <strong>Double-click</strong> to open a natural language query interface for single table
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.text }}>
              • <strong>Intelligent Query</strong> button to automatically determine which tables to use
            </Typography>
            <Typography variant="body2" sx={{ color: theme.colors.text }}>
              • <strong>Enabled sources</strong> will be used in the credit decision process
            </Typography>
          </Alert>
        </Collapse>

        <Box mb={4}>
          <Typography variant="h5" gutterBottom sx={{ 
            color: theme.colors.text,
            fontWeight: 600,
            textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
          }}>
            Data Source Categories
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {['demographics', 'banking', 'credit_bureau', 'income', 'open_banking', 'fraud', 'economic'].map(category => (
              <Chip
                key={category}
                label={`${category.replace('_', ' ')}: ${getEnabledCategoryCount(category)}/${getCategoryCount(category)}`}
                color={getEnabledCategoryCount(category) > 0 ? 'primary' : 'default'}
                variant={getEnabledCategoryCount(category) > 0 ? 'filled' : 'outlined'}
                size="medium"
                sx={{
                  backgroundColor: getEnabledCategoryCount(category) > 0 ? theme.colors.primary : 'rgba(255, 255, 255, 0.2)',
                  color: getEnabledCategoryCount(category) > 0 ? 'white' : theme.colors.text,
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                  fontWeight: 500
                }}
              />
            ))}
          </Box>
        </Box>

        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 3,
          width: '100%',
          mb: 4
        }}>
          {dataSources.map((dataSource) => (
            <Box key={dataSource.id} sx={{ width: '100%' }}>
              <DataSource
                dataSource={dataSource}
                onToggle={handleToggleDataSource}
              />
            </Box>
          ))}
        </Box>


      </Paper>

      {/* Multi-Table Query Dialog */}
      <MultiTableQuery
        open={showMultiTableQuery}
        onClose={() => setShowMultiTableQuery(false)}
        dataSources={dataSources}
      />

              {/* Customer Data View */}
        {selectedCustomer && (
          <Box sx={{ mt: 4 }}>
            <CustomerDataView
              customerId={selectedCustomer.customer_id}
              customerName={`${selectedCustomer.first_name} ${selectedCustomer.last_name}`}
            />
          </Box>
        )}
    </Box>
  );
};

export default DataLayer;
