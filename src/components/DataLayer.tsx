import React, { useState } from 'react';
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
  Info as InfoIcon
} from '@mui/icons-material';
import { DataSource as DataSourceType } from '../types';
import { dataSources, toggleDataSource } from '../data/dataSources';
import DataSource from './DataSource';

const DataLayer: React.FC = () => {
  const [currentDataSources, setCurrentDataSources] = useState<DataSourceType[]>(dataSources);
  const [showInfo, setShowInfo] = useState(false);

  const handleToggleDataSource = (id: string) => {
    const updatedSources = currentDataSources.map(source => 
      source.id === id ? { ...source, isEnabled: !source.isEnabled } : source
    );
    setCurrentDataSources(updatedSources);
  };

  const getEnabledCount = () => {
    return currentDataSources.filter(ds => ds.isEnabled).length;
  };

  const getCategoryCount = (category: string) => {
    return currentDataSources.filter(ds => ds.category === category).length;
  };

  const getEnabledCategoryCount = (category: string) => {
    return currentDataSources.filter(ds => ds.category === category && ds.isEnabled).length;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <StorageIcon sx={{ fontSize: 32, color: '#2196F3' }} />
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Data Layer
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Select data sources for credit limit decisions
            </Typography>
          </Box>
        </Box>
        <Box display="flex" gap={1}>
          <Button
            startIcon={<InfoIcon />}
            onClick={() => setShowInfo(!showInfo)}
            variant="outlined"
          >
            Info
          </Button>
          <Chip
            label={`${getEnabledCount()}/${currentDataSources.length} enabled`}
            color="primary"
            variant="outlined"
          />
        </Box>
      </Box>

      <Collapse in={showInfo}>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>How to use:</strong>
          </Typography>
          <Typography variant="body2">
            • <strong>Click</strong> on a data source card to toggle it on/off for credit decisions
          </Typography>
          <Typography variant="body2">
            • <strong>Hover</strong> over cards to see interaction hints
          </Typography>
          <Typography variant="body2">
            • <strong>Double-click</strong> to open a natural language query interface
          </Typography>
          <Typography variant="body2">
            • <strong>Enabled sources</strong> will be used in the credit decision process
          </Typography>
        </Alert>
      </Collapse>

      <Box mb={3}>
        <Typography variant="h6" gutterBottom>
          Data Source Categories
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          {['demographics', 'banking', 'credit_bureau', 'income', 'open_banking', 'fraud', 'economic'].map(category => (
            <Chip
              key={category}
              label={`${category.replace('_', ' ')}: ${getEnabledCategoryCount(category)}/${getCategoryCount(category)}`}
              color={getEnabledCategoryCount(category) > 0 ? 'primary' : 'default'}
              variant={getEnabledCategoryCount(category) > 0 ? 'filled' : 'outlined'}
              size="small"
            />
          ))}
        </Box>
      </Box>

      <Paper sx={{ p: 3, backgroundColor: '#f8f9fa' }}>
        <Grid container spacing={3}>
          {currentDataSources.map((dataSource) => (
            <Grid item key={dataSource.id}>
              <DataSource
                dataSource={dataSource}
                onToggle={handleToggleDataSource}
              />
            </Grid>
          ))}
        </Grid>
      </Paper>

      <Box mt={3} p={2} bgcolor="background.paper" borderRadius={1}>
        <Typography variant="h6" gutterBottom>
          Selected Data Sources Summary
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          {currentDataSources
            .filter(ds => ds.isEnabled)
            .map(ds => (
              <Chip
                key={ds.id}
                label={ds.name}
                color="success"
                size="small"
                variant="filled"
              />
            ))}
        </Box>
        {getEnabledCount() === 0 && (
          <Typography variant="body2" color="text.secondary" mt={1}>
            No data sources selected. Click on cards above to enable them.
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default DataLayer;
