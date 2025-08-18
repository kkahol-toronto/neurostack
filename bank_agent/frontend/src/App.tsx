import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  AppBar,
  Toolbar,
  Paper,
  Chip,
  Alert
} from '@mui/material';
import DataSourceComponent from './components/DataSource';
import ThemeSwitcher from './components/ThemeSwitcher';
import { DataSource } from './types';
import { dataSources, toggleDataSource } from './data/dataSources';
import { useTheme } from './contexts/ThemeContext';
import './App.css';

function App() {
  const [dataSourceList, setDataSourceList] = useState<DataSource[]>(dataSources);
  const [error, setError] = useState<string | null>(null);
  const { theme } = useTheme();

  const handleToggleDataSource = (id: string) => {
    try {
      const updatedDataSources = toggleDataSource(id);
      setDataSourceList(updatedDataSources);
      setError(null);
    } catch (err) {
      setError('Failed to toggle data source');
    }
  };

  const enabledCount = dataSourceList.filter(ds => ds.isEnabled).length;
  const totalCount = dataSourceList.length;

  return (
    <div className="App">
      <AppBar 
        position="static" 
        sx={{
          backgroundColor: theme.colors.surface,
          boxShadow: theme.effects.shadow,
          borderBottom: `1px solid ${theme.colors.border}`
        }}
      >
        <Toolbar>
          <Typography 
            variant="h4" 
            component="div" 
            sx={{ 
              flexGrow: 1, 
              fontFamily: theme.fonts.primary,
              color: theme.colors.text,
              fontWeight: 700
            }}
          >
            🏦 Banking Agent - Data Source Management
          </Typography>
          <ThemeSwitcher />
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Paper 
          sx={{ 
            p: 3, 
            mb: 3,
            backgroundColor: theme.colors.surface,
            boxShadow: theme.effects.shadow,
            border: `1px solid ${theme.colors.border}`
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography 
              variant="h2" 
              sx={{ 
                fontFamily: theme.fonts.primary,
                color: theme.colors.text,
                fontWeight: 700
              }}
            >
              Data Sources
            </Typography>
            <Chip 
              label={`${enabledCount}/${totalCount} Sources Active`}
              variant="outlined"
              size="medium"
              sx={{ 
                fontFamily: theme.fonts.primary,
                color: '#000000',
                borderColor: '#000000',
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                fontSize: '1.1rem',
                fontWeight: 700,
                height: '40px',
                padding: '8px 16px',
                textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)'
              }}
            />
          </Box>
          <Typography 
            variant="h5" 
            sx={{ 
              mb: 3, 
              fontFamily: theme.fonts.primary,
              color: theme.colors.textSecondary,
              fontWeight: 500,
              lineHeight: 1.6
            }}
          >
            Manage your data sources for credit risk assessment. Click to toggle sources on/off, 
            double-click to query data using natural language.
          </Typography>
        </Paper>

        <Box 
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 3,
            justifyContent: 'center',
            mt: 4,
            px: 2
          }}
        >
          {dataSourceList.map((dataSource) => (
            <Box key={dataSource.id} sx={{ minWidth: 340, maxWidth: 400 }}>
              <DataSourceComponent
                dataSource={dataSource}
                onToggle={handleToggleDataSource}
              />
            </Box>
          ))}
        </Box>

        <Box 
          sx={{
            mt: 4,
            pt: 3,
            borderTop: `1px solid ${theme.colors.border}`,
            textAlign: 'center'
          }}
        >
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: theme.fonts.primary,
              color: theme.colors.textSecondary,
              fontWeight: 600
            }}
          >
            Powered by NeuroStack - AI-Powered Banking Intelligence
          </Typography>
        </Box>
      </Container>
    </div>
  );
}

export default App;
