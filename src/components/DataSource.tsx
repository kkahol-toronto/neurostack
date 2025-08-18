import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Storage as StorageIcon,
  QueryStats as QueryIcon,
  CheckCircle as EnabledIcon,
  Cancel as DisabledIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { DataSource as DataSourceType, QueryResult } from '../types';
import apiService from '../services/api';

interface DataSourceProps {
  dataSource: DataSourceType;
  onToggle: (id: string) => void;
}

const DataSource: React.FC<DataSourceProps> = ({ dataSource, onToggle }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showQueryDialog, setShowQueryDialog] = useState(false);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = () => {
    onToggle(dataSource.id);
  };

  const handleDoubleClick = () => {
    setQuery(dataSource.sampleQuery || '');
    setShowQueryDialog(true);
  };

  const handleQuerySubmit = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setQueryResult(null);

    try {
      const result = await apiService.convertTextToSQL(
        query,
        dataSource.tableName,
        dataSource.fields
      );
      setQueryResult(result);
    } catch (error) {
      setQueryResult({
        success: false,
        error: 'Failed to execute query'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      demographics: '#2196F3',
      banking: '#4CAF50',
      credit_bureau: '#FF9800',
      income: '#9C27B0',
      open_banking: '#00BCD4',
      fraud: '#F44336',
      economic: '#795548'
    };
    return colors[category] || '#757575';
  };

  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: string } = {
      demographics: '👥',
      banking: '🏦',
      credit_bureau: '📊',
      income: '💰',
      open_banking: '🔗',
      fraud: '⚠️',
      economic: '📈'
    };
    return icons[category] || '📋';
  };

  return (
    <>
      <Card
        sx={{
          width: 300,
          height: 200,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          transform: isHovered ? 'scale(1.02)' : 'scale(1)',
          boxShadow: isHovered ? 4 : 2,
          border: dataSource.isEnabled ? '2px solid #4CAF50' : '2px solid transparent',
          position: 'relative',
          overflow: 'visible'
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
      >
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="h6" component="div" fontSize="1.2rem">
                {getCategoryIcon(dataSource.category)}
              </Typography>
              <Typography variant="h6" component="div" fontSize="1rem">
                {dataSource.name}
              </Typography>
            </Box>
            {dataSource.isEnabled ? (
              <EnabledIcon color="success" />
            ) : (
              <DisabledIcon color="disabled" />
            )}
          </Box>

          <Chip
            label={dataSource.category.replace('_', ' ')}
            size="small"
            sx={{
              backgroundColor: getCategoryColor(dataSource.category),
              color: 'white',
              mb: 1
            }}
          />

          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {dataSource.description}
          </Typography>

          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="caption" color="text.secondary">
              {dataSource.fields.length} fields
            </Typography>
            <Tooltip title="Double-click to query">
              <IconButton size="small">
                <QueryIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>

          {isHovered && (
            <Box
              sx={{
                position: 'absolute',
                top: -10,
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: 'rgba(0,0,0,0.8)',
                color: 'white',
                padding: 1,
                borderRadius: 1,
                fontSize: '0.75rem',
                zIndex: 1000,
                maxWidth: 250,
                textAlign: 'center'
              }}
            >
              Click to toggle • Double-click to query
            </Box>
          )}
        </CardContent>
      </Card>

      <Dialog
        open={showQueryDialog}
        onClose={() => setShowQueryDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <QueryIcon />
            <Typography>Query {dataSource.name}</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary" mb={1}>
              Available fields: {dataSource.fields.join(', ')}
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Natural Language Query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Show me customers with income above $100,000"
              variant="outlined"
            />
          </Box>

          {isLoading && (
            <Box display="flex" justifyContent="center" my={2}>
              <CircularProgress />
            </Box>
          )}

          {queryResult && (
            <Box>
              {queryResult.success ? (
                <>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Query executed successfully in {queryResult.executionTime}ms
                  </Alert>
                  <Typography variant="subtitle2" gutterBottom>
                    Generated SQL:
                  </Typography>
                  <Box
                    sx={{
                      backgroundColor: '#f5f5f5',
                      padding: 1,
                      borderRadius: 1,
                      fontFamily: 'monospace',
                      fontSize: '0.875rem',
                      mb: 2
                    }}
                  >
                    {queryResult.sql}
                  </Box>
                  {queryResult.data && queryResult.data.length > 0 && (
                    <>
                      <Typography variant="subtitle2" gutterBottom>
                        Results ({queryResult.data.length} rows):
                      </Typography>
                      <Box
                        sx={{
                          maxHeight: 200,
                          overflow: 'auto',
                          border: '1px solid #ddd',
                          borderRadius: 1
                        }}
                      >
                        <pre style={{ margin: 0, padding: 8, fontSize: '0.75rem' }}>
                          {JSON.stringify(queryResult.data.slice(0, 5), null, 2)}
                          {queryResult.data.length > 5 && `\n... and ${queryResult.data.length - 5} more rows`}
                        </pre>
                      </Box>
                    </>
                  )}
                </>
              ) : (
                <Alert severity="error">
                  {queryResult.error}
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowQueryDialog(false)}>Close</Button>
          <Button
            onClick={handleQuerySubmit}
            variant="contained"
            disabled={!query.trim() || isLoading}
          >
            Execute Query
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DataSource;
